"""
app/services/predictor.py
──────────────────────────
Orchestration layer — kết nối HTTP request với ML pipeline.

Flow một request:
  1. Nhận PredictInput (đã validate từ route)
  2. Kiểm tra registry xem .pkl có sẵn không
  3a. Có model → build_features() → model.predict() → expm1 → wrap output
  3b. Không có model → mock fallback (dev / demo)
  4. Trả PredictOutput

Key notes:
  - Model được train với target = log1p(price) → predict trả log → expm1 để ra VNĐ
  - Price range = ±PRICE_INTERVAL_RATIO × price_mid
  - Confidence: RandomForest dùng std estimators, còn lại dùng range heuristic
"""

from __future__ import annotations

import logging
import random
from typing import Any

import numpy as np

from app.core.config import MOCK_PRICE_PER_M2, PRICE_INTERVAL_RATIO
from app.core.exceptions import FeatureBuildError
from app.ml.feature_builder import build_features
from app.ml.registry import registry
from app.ml.schemas import ModelKey, PredictInput, PredictOutput

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# PUBLIC ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def run_prediction(inp: PredictInput) -> PredictOutput:
    """
    Điểm vào duy nhất cho prediction. Gọi từ route handler.

    Args:
        inp: PredictInput đã validate

    Returns:
        PredictOutput với price range, confidence, metadata

    Raises:
        FeatureBuildError: lỗi khi build features
    """
    logger.info(
        f"[Predictor] city={inp.city} model={inp.model_type} "
        f"area={inp.area}m² district={inp.district} ward={inp.ward}"
    )

    key   = inp.model_key
    model = registry.get(key)

    if model is not None:
        output = _predict_with_model(model, key, inp)
    else:
        logger.warning(f"[Predictor] No .pkl for {key} → mock fallback")
        output = _predict_mock(key, inp)

    logger.info(
        f"[Predictor] {output.model_used} | "
        f"{output.price_low:,.0f}–{output.price_high:,.0f} VNĐ | "
        f"conf={output.confidence:.0%} | fallback={output.is_fallback}"
    )
    return output


# ═══════════════════════════════════════════════════════════════════════════════
# REAL MODEL PATH
# ═══════════════════════════════════════════════════════════════════════════════

def _predict_with_model(model: Any, key: ModelKey, inp: PredictInput) -> PredictOutput:
    """
    Chạy model .pkl thực.

    Hỗ trợ 2 cách xử lý categorical features:
      A) Pipeline có OHE/LabelEncoder bên trong → truyền string thẳng
      B) XGBoost train với enable_categorical=True → cần cast sang CategoricalDtype
    """
    X = build_features(inp)

    # Cities dùng target log1p(price_per_m2) → phải nhân area để ra price
    # Cần Thơ dùng log1p(price) thẳng nên KHÔNG nhân area
    PRICE_PER_M2_TARGET_CITIES = {"danang", "haiphong", "dongnai"}

    try:
        # Huế: bundle có artifacts riêng (imputer, capper, preprocessor)
        # Cần transform thủ công trước khi đưa vào model
        if inp.city == "hue":
            log_pred = _predict_hue(model, key, X)
        else:
            log_pred = _predict_with_retry(model, X)
        pred_val = float(np.expm1(log_pred[0]))

        if inp.city in PRICE_PER_M2_TARGET_CITIES:
            # Model predict log1p(price_per_m2) → price = price_per_m2 × area
            price_mid = pred_val * inp.area
            logger.info(f"[Predictor] price_per_m2={pred_val:,.0f} × area={inp.area} = {price_mid:,.0f}")
        else:
            # HN / HCM / CT: model predict log1p(price_vnd) thẳng
            price_mid = pred_val

    except FeatureBuildError:
        raise
    except Exception as exc:
        raise FeatureBuildError(
            f"Model predict thất bại: {exc}. "
            "Kiểm tra feature vector có khớp với lúc train không."
        ) from exc

    # Giá trị hợp lệ: 100tr – 500 tỷ
    if not (1e8 <= price_mid <= 5e11):
        logger.warning(
            f"[Predictor] Predicted price {price_mid:,.0f} ngoài khoảng hợp lý "
            f"(100tr – 500 tỷ). Có thể feature mismatch."
        )

    price_low  = price_mid * (1 - PRICE_INTERVAL_RATIO)
    price_high = price_mid * (1 + PRICE_INTERVAL_RATIO)
    confidence = _estimate_confidence(model, X, price_low, price_high, price_mid)

    return PredictOutput(
        price_low   = _round_price(price_low),
        price_mid   = _round_price(price_mid),
        price_high  = _round_price(price_high),
        confidence  = confidence,
        model_used  = str(key),
        is_fallback = False,
    )


def _predict_hue(model: Any, key: "ModelKey", X: "pd.DataFrame") -> Any:
    """
    Huế bundle: {model, artifacts:{imputer, capper, preprocessor, ...}, report}
    Pipeline KHÔNG phải sklearn Pipeline — cần transform thủ công:
      X_df → imputer.transform → capper.transform → preprocessor.transform → model.predict

    model đã được load từ bundle["model"] bởi registry._extract_pipeline().
    artifacts được cache riêng với key "artifacts".
    """
    artifacts = registry.get_artifact(key, "artifacts")

    if artifacts is None or not isinstance(artifacts, dict):
        logger.warning(f"[Predictor] Hue artifacts not found for {key}, trying direct predict")
        return _predict_with_retry(model, X)

    imputer     = artifacts.get("imputer")
    capper      = artifacts.get("capper")
    preprocessor = artifacts.get("preprocessor")

    if imputer is None or preprocessor is None:
        logger.warning(f"[Predictor] Hue artifacts incomplete for {key}, trying direct predict")
        return _predict_with_retry(model, X)

    try:
        # Step 1: KMeansClusterMeanImputer — nhận DataFrame, trả DataFrame
        X_imp = imputer.transform(X)
        if not hasattr(X_imp, "columns"):
            import pandas as pd
            X_imp = pd.DataFrame(X_imp, columns=X.columns)

        # Step 2: IQRCapper — nhận DataFrame, trả DataFrame
        if capper is not None:
            X_cap = capper.transform(X_imp)
        else:
            X_cap = X_imp

        # Step 3: ColumnTransformer (OHE + passthrough) → numpy array
        X_trans = preprocessor.transform(X_cap)

        # Step 4: XGBoost/LGBM predict
        return model.predict(X_trans)

    except Exception as exc:
        logger.error(f"[Predictor] Hue transform failed: {exc}, trying direct predict")
        return _predict_with_retry(model, X)


def _predict_with_retry(model: Any, X: "pd.DataFrame") -> Any:
    """
    Gọi model.predict(X).

    Nếu XGBoost báo lỗi dtype (enable_categorical=True mode) →
    cast object columns sang category rồi thử lại 1 lần.
    Không có detection logic phức tạp, không có vòng lặp nặng.
    """
    import pandas as pd

    try:
        return model.predict(X)

    except Exception as exc:
        err = str(exc)
        # XGBoost enable_categorical=True: cần cast object → category
        if "categorical" in err.lower() or "dtypes for data must be int" in err:
            logger.info("[Predictor] Retrying with category dtype cast (enable_categorical mode)")
            X_cat = X.copy()
            for col in X_cat.columns:
                if X_cat[col].dtype == object or str(X_cat[col].dtype) == "string":
                    X_cat[col] = X_cat[col].astype("category")
            return model.predict(X_cat)
        raise


def _estimate_confidence(
    model: Any,
    X: "pd.DataFrame",
    price_low: float,
    price_high: float,
    price_mid: float,
) -> float:
    """
    Ước lượng confidence từ model.

    Thứ tự ưu tiên:
      1. RandomForest: std giữa các estimators (coefficient of variation)
      2. Quantile / range heuristic từ interval ratio
    """
    # RandomForest — tính variance từ individual trees
    if hasattr(model, "named_steps"):
        final_step = list(model.named_steps.values())[-1]
        if hasattr(final_step, "estimators_"):
            try:
                log_preds = np.array([
                    est.predict(model[:-1].transform(X))[0]
                    for est in final_step.estimators_
                ])
                prices = np.expm1(log_preds)
                cv = prices.std() / (prices.mean() + 1)
                return round(float(np.clip(1 - cv * 2, 0.50, 0.95)), 2)
            except Exception:
                pass

    # Heuristic: range nhỏ → confidence cao
    range_ratio = (price_high - price_low) / (price_mid + 1)
    confidence = max(0.55, min(0.93, 1 - range_ratio * 0.8))
    return round(float(confidence), 2)


# ═══════════════════════════════════════════════════════════════════════════════
# MOCK FALLBACK (khi chưa có .pkl)
# ═══════════════════════════════════════════════════════════════════════════════

def _predict_mock(key: ModelKey, inp: PredictInput) -> PredictOutput:
    """
    Demo fallback — dùng mock price/m² theo city + model_type.
    Output trông hợp lý nhưng KHÔNG phải từ model thực.
    """
    city_ranges  = MOCK_PRICE_PER_M2.get(key.city, MOCK_PRICE_PER_M2["hanoi"])
    model_ranges = city_ranges.get(key.model_type, city_ranges["land"])

    lo_per_m2, hi_per_m2 = model_ranges
    price_per_m2 = random.uniform(lo_per_m2, hi_per_m2)
    price_mid    = price_per_m2 * inp.area

    price_low  = price_mid * (1 - PRICE_INTERVAL_RATIO)
    price_high = price_mid * (1 + PRICE_INTERVAL_RATIO)

    return PredictOutput(
        price_low   = _round_price(price_low),
        price_mid   = _round_price(price_mid),
        price_high  = _round_price(price_high),
        confidence  = round(random.uniform(0.65, 0.80), 2),
        model_used  = f"{key}_mock",
        is_fallback = True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _round_price(value: float) -> float:
    """Làm tròn về hàng triệu gần nhất."""
    return round(value / 1_000_000) * 1_000_000
