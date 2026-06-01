"""
app/ml/custom_transformers.py
──────────────────────────────
Custom sklearn transformers được inject vào sys.modules['__main__']
trước khi joblib/pickle load model .pkl.

Vấn đề: cùng tên class KMeansClusterMeanImputer nhưng 2 notebook
dùng 2 implementation khác nhau:

  HN notebook  → __init__(self, numeric_cols, n_clusters=8, random_state=42)
                  attributes: numeric_cols_, global_medians_ (dict), cluster_means_ (dict of dict)

  DN notebook  → __init__(self, n_clusters=5, random_state=42, batch_size=4096)
                  attributes: feature_names_in_, global_median_ (Series), cluster_means_ (dict of Series)

Giải pháp: 1 class duy nhất với __init__ nhận cả 2 signature.
fit() tự detect version dựa vào có numeric_cols hay không.
"""

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.cluster import MiniBatchKMeans
from sklearn.preprocessing import StandardScaler


# ═══════════════════════════════════════════════════════════════════════════════
# KMeansClusterMeanImputer
# Hỗ trợ cả HN (numeric_cols) và Đà Nẵng (không có numeric_cols)
# ═══════════════════════════════════════════════════════════════════════════════

class KMeansClusterMeanImputer(BaseEstimator, TransformerMixin):
    """
    Version HN : KMeansClusterMeanImputer(numeric_cols=[...], n_clusters=8)
    Version DN  : KMeansClusterMeanImputer(n_clusters=5, batch_size=4096)

    fit() tự detect version qua sự tồn tại của numeric_cols.
    """

    def __init__(self, numeric_cols=None, n_clusters=8, random_state=42, batch_size=4096):
        self.numeric_cols = numeric_cols   # HN truyền list, DN để None
        self.n_clusters   = n_clusters
        self.random_state = random_state
        self.batch_size   = batch_size

    # ─── HN VERSION ───────────────────────────────────────────────────────────
    # Nhận DataFrame, dùng numeric_cols để select columns
    # Attributes: numeric_cols_, global_medians_ (dict), cluster_means_ (dict of dict)

    def _fit_hn(self, X):
        X = X.copy()
        self.numeric_cols_ = [c for c in self.numeric_cols if c in X.columns]

        self.global_medians_ = {}
        for col in self.numeric_cols_:
            v = X[col].median()
            self.global_medians_[col] = 0 if pd.isna(v) else v

        X_init = X[self.numeric_cols_].copy()
        for col in self.numeric_cols_:
            X_init[col] = X_init[col].fillna(self.global_medians_[col])

        self.scaler_ = StandardScaler()
        X_scaled = self.scaler_.fit_transform(X_init)

        n_clusters_real = min(self.n_clusters, max(2, len(X_init) // 1500))
        self.kmeans_ = MiniBatchKMeans(
            n_clusters=n_clusters_real,
            random_state=self.random_state,
            batch_size=4096,
            n_init=3,
        )
        clusters = self.kmeans_.fit_predict(X_scaled)

        tmp = X[self.numeric_cols_].copy()
        tmp["_cluster"] = clusters
        self.cluster_means_ = (
            tmp.groupby("_cluster")[self.numeric_cols_]
            .mean()
            .to_dict(orient="index")
        )
        return self

    def _transform_hn(self, X):
        X = X.copy()
        X_init = X[self.numeric_cols_].copy()
        for col in self.numeric_cols_:
            X_init[col] = X_init[col].fillna(self.global_medians_[col])

        X_scaled = self.scaler_.transform(X_init)
        clusters  = self.kmeans_.predict(X_scaled)
        X["_cluster"] = clusters

        for col in self.numeric_cols_:
            missing_mask = X[col].isna()
            if missing_mask.any():
                fill_values = []
                for cluster_id in X.loc[missing_mask, "_cluster"]:
                    cluster_mean = self.cluster_means_.get(cluster_id, {}).get(col, np.nan)
                    if pd.isna(cluster_mean):
                        cluster_mean = self.global_medians_[col]
                    fill_values.append(cluster_mean)
                X.loc[missing_mask, col] = fill_values
            X[col] = X[col].fillna(self.global_medians_[col]).astype("float32")

        return X.drop(columns=["_cluster"])

    # ─── ĐÀ NẴNG VERSION ─────────────────────────────────────────────────────
    # Nhận array/DataFrame, không có numeric_cols
    # Attributes: n_features_in_, feature_names_in_, global_median_ (Series),
    #             n_clusters_ (int), cluster_means_ (dict of Series)

    def _fit_dn(self, X):
        X_df = (
            pd.DataFrame(X)
            .apply(pd.to_numeric, errors="coerce")
            .replace([np.inf, -np.inf], np.nan)
        )
        self.n_features_in_   = X_df.shape[1]
        self.feature_names_in_ = np.asarray(
            getattr(X, "columns", [f"numeric_{i}" for i in range(self.n_features_in_)])
        )
        self.global_median_ = X_df.median().fillna(0.0)

        X_filled = X_df.fillna(self.global_median_)
        self.n_clusters_ = int(min(self.n_clusters, max(1, len(X_filled))))
        self.scaler_ = StandardScaler()
        X_scaled = self.scaler_.fit_transform(X_filled)

        self.kmeans_ = MiniBatchKMeans(
            n_clusters=self.n_clusters_,
            random_state=self.random_state,
            batch_size=self.batch_size,
            n_init=10,
        )
        labels = self.kmeans_.fit_predict(X_scaled)
        self.cluster_means_ = {
            i: (
                X_df.iloc[labels == i].mean().fillna(self.global_median_)
                if (labels == i).sum() else self.global_median_
            )
            for i in range(self.n_clusters_)
        }
        return self

    def _transform_dn(self, X):
        X_df = (
            pd.DataFrame(X)
            .apply(pd.to_numeric, errors="coerce")
            .replace([np.inf, -np.inf], np.nan)
        )
        labels = self.kmeans_.predict(
            self.scaler_.transform(X_df.fillna(self.global_median_))
        )
        X_out = X_df.copy()
        for i in range(self.n_clusters_):
            mask = labels == i
            if mask.sum():
                X_out.loc[mask, :] = X_out.loc[mask, :].fillna(self.cluster_means_[i])
        return X_out.fillna(self.global_median_).values.astype(np.float32)

    # ─── DISPATCH ────────────────────────────────────────────────────────────

    def _is_hn_version(self):
        """
        Detect version sau khi fit:
          HN  → có attribute numeric_cols_
          DN  → có attribute feature_names_in_
        Trước khi fit → dựa vào __init__ param numeric_cols.
        """
        if hasattr(self, "numeric_cols_"):
            return True
        if hasattr(self, "feature_names_in_"):
            return False
        # Chưa fit → dùng __init__ param
        return self.numeric_cols is not None

    def fit(self, X, y=None):
        if self.numeric_cols is not None:
            return self._fit_hn(X)
        return self._fit_dn(X)

    def transform(self, X):
        if self._is_hn_version():
            return self._transform_hn(X)
        return self._transform_dn(X)

    def get_feature_names_out(self, input_features=None):
        if self._is_hn_version():
            return np.asarray(self.numeric_cols_, dtype=object)
        if input_features is None:
            input_features = getattr(
                self, "feature_names_in_",
                [f"numeric_{i}" for i in range(getattr(self, "n_features_in_", 0))]
            )
        return np.asarray(input_features, dtype=object)


# ═══════════════════════════════════════════════════════════════════════════════
# IQRCapper — Hà Nội notebook (copy nguyên xi)
# ═══════════════════════════════════════════════════════════════════════════════

class IQRCapper(BaseEstimator, TransformerMixin):
    def __init__(self, cols, lower_q=0.01, upper_q=0.99):
        self.cols    = cols
        self.lower_q = lower_q
        self.upper_q = upper_q

    def fit(self, X, y=None):
        self.cols_ = [c for c in self.cols if c in X.columns]
        self.bounds_ = {}
        for col in self.cols_:
            lower = X[col].quantile(self.lower_q)
            upper = X[col].quantile(self.upper_q)
            if pd.isna(lower):
                lower = X[col].min()
            if pd.isna(upper):
                upper = X[col].max()
            self.bounds_[col] = (lower, upper)
        return self

    def transform(self, X):
        X = X.copy()
        for col in self.cols_:
            lower, upper = self.bounds_[col]
            X[col] = X[col].clip(lower, upper).astype("float32")
        return X


# ═══════════════════════════════════════════════════════════════════════════════
# FrequencyEncoder — Cần Thơ notebook (copy nguyên xi)
# ═══════════════════════════════════════════════════════════════════════════════

class FrequencyEncoder(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.freq_maps_ = {}
        self.feature_names_in_ = None

    def fit(self, X, y=None):
        X_df = pd.DataFrame(X).copy()
        self.feature_names_in_ = X_df.columns.astype(str).tolist()
        n = len(X_df)
        self.freq_maps_ = {}
        for col in X_df.columns:
            s = X_df[col].astype("object").where(X_df[col].notna(), "__MISSING__")
            self.freq_maps_[col] = (s.value_counts(dropna=False) / max(n, 1)).to_dict()
        return self

    def transform(self, X):
        # Luôn dùng feature_names_in_ để gán column names
        # ColumnTransformer có thể truyền array không có column names
        cols = self.feature_names_in_ or []
        if cols and hasattr(X, "shape") and X.shape[1] == len(cols):
            X_df = pd.DataFrame(X, columns=cols).copy()
        else:
            X_df = pd.DataFrame(X).copy()
        out = pd.DataFrame(index=X_df.index)
        for col in X_df.columns:
            s = X_df[col].astype("object").where(X_df[col].notna(), "__MISSING__")
            out[f"{col}_freq"] = s.map(self.freq_maps_.get(col, {})).fillna(0.0)
        return out.values

    def get_feature_names_out(self, input_features=None):
        if input_features is None:
            input_features = self.feature_names_in_
        return np.array([f"{col}_freq" for col in input_features])


# ═══════════════════════════════════════════════════════════════════════════════
# SafeFrequencyEncoder — Cần Thơ notebook (copy nguyên xi)
# ═══════════════════════════════════════════════════════════════════════════════

class SafeFrequencyEncoder(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.freq_maps_ = {}
        self.columns_   = None

    def fit(self, X, y=None):
        X_df = pd.DataFrame(X).copy()
        self.columns_ = list(X_df.columns)
        self.freq_maps_ = {}
        for col in self.columns_:
            s = X_df[col].astype("string").fillna("__MISSING__")
            self.freq_maps_[col] = s.value_counts(normalize=True).to_dict()
        return self

    def transform(self, X):
        # ColumnTransformer có thể truyền array không có column names
        # → luôn gán columns_ vào DataFrame để lookup đúng
        X_df = pd.DataFrame(X, columns=self.columns_).copy()

        encoded_cols = []
        for col in self.columns_:
            s = X_df[col].astype("string").fillna("__MISSING__")
            encoded = s.map(self.freq_maps_.get(col, {})).fillna(0).astype(float)
            encoded_cols.append(encoded.to_numpy())

        if len(encoded_cols) == 0:
            return np.empty((len(X_df), 0))
        return np.vstack(encoded_cols).T

    def get_feature_names_out(self, input_features=None):
        if input_features is None:
            input_features = self.columns_
        return np.array([f"{col}_freq" for col in input_features])