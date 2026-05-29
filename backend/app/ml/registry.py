"""
app/ml/registry.py
──────────────────
Quản lý việc load/cache model .pkl từ disk.

Hỗ trợ 2 format được save từ notebook:

  FORMAT A — HCM inference bundle (dict):
    {
      "model":               sklearn Pipeline,
      "freq_maps":           dict[col → dict[value → float]],
      "area_bins":           np.ndarray,
      "numeric_features":    list[str],
      "categorical_features":list[str],
      "segment":             "land" | "non_land",
      "model_type":          str,
      "ward_mapping":        dict,
      "provinces":           list[str],
    }
    File naming: hcm_land_inference_bundle.pkl
                 hcm_non_land_inference_bundle.pkl

  FORMAT B — HN standalone pipeline (sklearn Pipeline):
    File naming: hanoi_land.pkl  |  hanoi_non_land.pkl
    Freq maps riêng: hanoi_land_freq_maps.pkl  |  hanoi_non_land_freq_maps.pkl
    Area bins riêng: hanoi_land_area_bins.pkl  |  hanoi_non_land_area_bins.pkl

  FORMAT C — Generic city khác:
    File naming: {city}_{model_type}.pkl  (VD: danang_land.pkl)
    Freq maps:   {city}_{model_type}_freq_maps.pkl  (optional)
    Area bins:   {city}_{model_type}_area_bins.pkl  (optional)

Tất cả được cache in-memory sau lần load đầu tiên.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    # Chỉ import lúc type-check (mypy / pylance), không import lúc runtime
    # → tránh circular import giữa registry ↔ schemas
    from app.ml.schemas import ModelKey

logger = logging.getLogger(__name__)

# ── Config ─────────────────────────────────────────────────────────────────────
try:
    from app.core.config import PKL_DIR, VALID_CITIES, VALID_MODEL_TYPES
except ImportError:
    PKL_DIR           = Path("pkl_models")
    VALID_CITIES      = {"hanoi", "hcm", "danang", "hue", "dongnai", "cantho"}
    VALID_MODEL_TYPES = {"land", "non_land"}


def _resolve_pkl_dir(pkl_dir: Path | str) -> Path:
    """
    PKL_DIR tu config.py luon la absolute path nen chi can resolve() la du.
    Giu lai fallback cho truong hop truyen relative path thu cong.
    """
    p = Path(pkl_dir).resolve()
    if not p.exists():
        logger.warning(f"[Registry] PKL_DIR khong ton tai: {p}")
    else:
        logger.info(f"[Registry] PKL_DIR: {p}")
    return p


class ModelRegistry:
    """Thread-safe (GIL bảo vệ) in-memory cache cho models và artifacts."""

    def __init__(self, pkl_dir: Path | str = PKL_DIR):
        self._dir   = _resolve_pkl_dir(pkl_dir)
        self._cache: dict[str, Any] = {}

    # ─────────────────────────────────────────────────────────────────────────
    # Public API — dùng trong predictor / feature_builder
    # ─────────────────────────────────────────────────────────────────────────

    def get(self, model_key: "ModelKey") -> Any | None:
        """
        Trả về sklearn Pipeline hoặc None nếu chưa có .pkl.
        Kết quả được cache in-memory sau lần đầu.
        """
        cache_k = self._cache_key("model", model_key)
        if cache_k not in self._cache:
            self._cache[cache_k] = self._load_model(model_key)
        return self._cache[cache_k]

    def get_artifact(self, model_key: "ModelKey", artifact: str) -> Any | None:
        """
        Lấy artifact phụ (freq_maps, area_bins) theo model key.
        artifact: "freq_maps" | "area_bins" | "ward_mapping" | "numeric_features" | "categorical_features"
        """
        cache_k = self._cache_key(artifact, model_key)
        if cache_k not in self._cache:
            self._cache[cache_k] = self._load_artifact(model_key, artifact)
        return self._cache[cache_k]

    def is_available(self, model_key: "ModelKey") -> bool:
        """True nếu model .pkl đã được load thành công (không phải mock)."""
        return self.get(model_key) is not None

    def list_loaded(self) -> list[str]:
        """Trả về list key string của các model đã load thành công."""
        prefix = "model::"
        return [
            k[len(prefix):]
            for k, v in self._cache.items()
            if k.startswith(prefix) and v is not None
        ]

    def preload_all(self) -> dict[str, bool]:
        """
        Được gọi khi startup — load tất cả combinations city × model_type.
        Trả về dict {key_str: loaded_ok} để main.py log kết quả.
        """
        from app.ml.schemas import ModelKey  # import runtime ở đây, tránh circular

        results: dict[str, bool] = {}
        for city in sorted(VALID_CITIES):
            for mtype in sorted(VALID_MODEL_TYPES):
                key              = ModelKey(city=city, model_type=mtype)
                model            = self.get(key)
                results[str(key)] = model is not None
        return results

    def clear_cache(self) -> None:
        """Hot-reload: xoá cache để force load lại file mới từ disk."""
        self._cache.clear()
        logger.info("[Registry] Cache cleared — models will reload on next request.")

    # ─────────────────────────────────────────────────────────────────────────
    # Internal helpers
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    def _cache_key(prefix: str, key: "ModelKey") -> str:
        """
        Tạo cache key nhất quán: "{prefix}::{city}_{model_type}"
        VD: "model::hanoi_non_land", "freq_maps::hcm_land"

        Dùng key.city + key.model_type trực tiếp thay vì str(key)
        để đảm bảo không phụ thuộc vào __str__ implementation.
        """
        return f"{prefix}::{key.city}_{key.model_type}"

    # ─────────────────────────────────────────────────────────────────────────
    # Internal loaders
    # ─────────────────────────────────────────────────────────────────────────

    # Map city → các prefix tên file có thể có trong notebook
    _CITY_FILE_PREFIXES: dict[str, list[str]] = {
        "hanoi":   ["hanoi", "ha_noi", "HaNoi", "HANOI"],
        "hcm":     ["hcm", "ho_chi_minh", "HCM"],
        "danang":  ["danang", "da_nang", "DANANG"],
        "hue":     ["hue", "HUE", "thua_thien_hue"],
        "dongnai": ["dongnai", "dong_nai", "DONGNAI"],
        "cantho":  ["cantho", "can_tho", "CANTHO"],
    }

    # Map model_type → các token tên file có thể có
    _MTYPE_FILE_TOKENS: dict[str, list[str]] = {
        "land":     ["land", "LAND"],
        "non_land": ["non_land", "nonland", "NON_LAND", "NONLAND"],
    }

    def _load_model(self, key: "ModelKey") -> Any | None:
        """
        Tìm file .pkl theo nhiều naming convention:
          1. Exact names: {city}_{mtype}_inference_bundle.pkl, {city}_{mtype}.pkl
          2. Glob scan: tìm file chứa đồng thời city token VÀ mtype token
             → xử lý tên như ha_noi_land_xgboost_v4_optimized.pkl
                          hay DANANG_LAND_XGBOOST_ORIGINAL_15052026.pkl
        """
        import joblib
        city  = key.city
        mtype = key.model_type

        logger.info(f"[Registry] Looking for {city}_{mtype} in: {self._dir}")

        # ── Bước 1: Exact name candidates ────────────────────────────────────
        exact_candidates = [
            self._dir / f"{city}_{mtype}_inference_bundle.pkl",
            self._dir / f"{city}_{mtype}.pkl",
            self._dir / f"{city}-{mtype}.pkl",
        ]
        for path in exact_candidates:
            result = self._try_load(path)
            if result is not None:
                self._maybe_cache_bundle(key, result, path)
                return self._extract_pipeline(result)

        # ── Bước 2: Glob scan với city + mtype tokens ─────────────────────────
        city_tokens  = self._CITY_FILE_PREFIXES.get(city, [city])
        mtype_tokens = self._MTYPE_FILE_TOKENS.get(mtype, [mtype])

        all_pkls = list(self._dir.glob("*.pkl"))
        logger.info(f"[Registry] Scanning {len(all_pkls)} .pkl files in {self._dir}")

        matched = []
        for pkl_file in sorted(all_pkls):
            name_lower = pkl_file.stem.lower()
            city_match  = any(tok.lower() in name_lower for tok in city_tokens)
            mtype_match = any(tok.lower() in name_lower for tok in mtype_tokens)
            if city_match and mtype_match:
                matched.append(pkl_file)

        if not matched:
            logger.warning(f"[Registry] ⚠️  No .pkl matched for {city}_{mtype} → mock fallback")
            return None

        # Ưu tiên file ngắn nhất (ít suffix nhất = model chính, không phải checkpoint)
        matched.sort(key=lambda p: len(p.stem))
        logger.info(f"[Registry] Glob matched: {[p.name for p in matched]}")

        for path in matched:
            result = self._try_load(path)
            if result is not None:
                self._maybe_cache_bundle(key, result, path)
                return self._extract_pipeline(result)

        logger.warning(f"[Registry] ⚠️  All matched files failed to load for {city}_{mtype}")
        return None

    def _try_load(self, path: Path) -> Any | None:
        """
        Load mot file .pkl, tra ve object hoac None neu loi.

        Truoc khi joblib.load(), inject custom classes vao sys.modules['__main__']
        vi notebook train trong __main__ nen pickle luu module path la __main__.
        Import thong thuong khong du -- phai gan thang vao __main__.
        """
        import sys
        import joblib

        if not path.exists():
            return None

        # Inject custom classes vao __main__ truoc khi unpickle
        try:
            from app.ml.custom_transformers import (
                KMeansClusterMeanImputer,
                IQRCapper,
                FrequencyEncoder,
                SafeFrequencyEncoder,
            )
            main_module = sys.modules["__main__"]
            for cls in [KMeansClusterMeanImputer, IQRCapper,
                        FrequencyEncoder, SafeFrequencyEncoder]:
                if not hasattr(main_module, cls.__name__):
                    setattr(main_module, cls.__name__, cls)
        except Exception as inject_exc:
            logger.warning(f"[Registry] Could not inject custom transformers: {inject_exc}")

        try:
            obj = joblib.load(path)
            logger.info(f"[Registry] ✅ Loaded (joblib): {path.name}")
            return obj
        except ModuleNotFoundError as exc:
            if "cloudpickle" in str(exc):
                # File được save bằng cloudpickle (VD: Cần Thơ notebook)
                # cloudpickle embed class definition → không cần inject __main__
                try:
                    import cloudpickle
                    with open(path, "rb") as f:
                        obj = cloudpickle.load(f)
                    logger.info(f"[Registry] ✅ Loaded (cloudpickle): {path.name}")
                    return obj
                except Exception as cp_exc:
                    logger.error(f"[Registry] ❌ Failed (cloudpickle): {path.name}: {type(cp_exc).__name__}: {cp_exc}")
                    return None
            logger.error(f"[Registry] ❌ Failed: {path.name}: {type(exc).__name__}: {exc}")
            return None
        except Exception as exc:
            logger.error(f"[Registry] ❌ Failed: {path.name}: {type(exc).__name__}: {exc}")
            return None

    @staticmethod
    def _extract_pipeline(obj: Any) -> Any:
        """
        Trích xuất sklearn Pipeline có thể predict() từ object được load.

        Hỗ trợ các format bundle:
          - FORMAT A (HCM): dict với key "model"        → pipeline + preprocessor
          - FORMAT CT (Cần Thơ): dict với key "pipeline" → sklearn Pipeline đầy đủ
          - FORMAT B (HN): sklearn Pipeline trực tiếp    → trả thẳng
        """
        if not isinstance(obj, dict):
            return obj   # Pipeline trực tiếp (HN format)

        # Ưu tiên "pipeline" (Cần Thơ) vì đó là Pipeline đầy đủ (preprocessor + model)
        if "pipeline" in obj:
            return obj["pipeline"]

        # Fallback "model" (HCM bundle)
        if "model" in obj:
            return obj["model"]

        raise KeyError(
            f"Bundle dict không có key 'pipeline' hay 'model'. "
            f"Keys hiện có: {list(obj.keys())}"
        )

    def _maybe_cache_bundle(self, key: "ModelKey", obj: Any, path: Path) -> None:
        """Cache artifacts nếu obj là bundle dict (FORMAT A hoặc FORMAT CT)."""
        if not isinstance(obj, dict):
            return
        self._cache_bundle_artifacts(key, obj)

    def _load_artifact(self, key: "ModelKey", artifact: str) -> Any | None:
        """
        Load artifact riêng lẻ cho FORMAT B/C (HN, Đà Nẵng…).
        Với FORMAT A, artifact đã được cache trong _cache_bundle_artifacts.
        """
        import joblib

        city  = key.city
        mtype = key.model_type

        candidates = [
            self._dir / f"{city}_{mtype}_{artifact}.pkl",
            self._dir / f"{city}-{mtype}-{artifact}.pkl",
        ]

        for path in candidates:
            if path.exists():
                try:
                    obj = joblib.load(path)
                    logger.info(f"[Registry] ✅ Loaded artifact: {path.name}")
                    return obj
                except Exception as exc:
                    logger.error(
                        f"[Registry] ❌ Failed to load artifact {path.name}: {type(exc).__name__}: {exc}"
                    )

        return None

    def _cache_bundle_artifacts(self, key: "ModelKey", bundle: dict) -> None:
        """
        Extract và cache artifacts từ bundle dict.
        Hỗ trợ:
          FORMAT A  (HCM)   : top-level keys freq_maps, area_bins, numeric_features...
          FORMAT HUE (Huế)  : nested bundle["artifacts"] dict
          FORMAT CT (CanTho): ohe_cols, freq_cols, numeric_cols
        """
        # ── FORMAT HUE: nested artifacts dict ─────────────────────────────────
        # bundle = {model, artifacts:{imputer,capper,preprocessor,
        #                             numeric_features,categorical_features,feature_cols},
        #           report}
        if "artifacts" in bundle and isinstance(bundle["artifacts"], dict):
            cache_k = self._cache_key("artifacts", key)
            if cache_k not in self._cache:
                self._cache[cache_k] = bundle["artifacts"]
            # Cũng cache numeric_features và categorical_features ở top-level
            # để _get_hue_feature_lists() có thể lấy từ artifacts
            arts = bundle["artifacts"]
            for artifact in ("numeric_features", "categorical_features", "feature_cols",
                             "freq_maps", "area_bins"):
                if artifact in arts:
                    top_k = self._cache_key(artifact, key)
                    if top_k not in self._cache:
                        self._cache[top_k] = arts[artifact]

        # ── FORMAT A / FORMAT CT: top-level keys ──────────────────────────────
        top_level_artifacts = (
            "freq_maps", "area_bins",
            "numeric_features", "categorical_features", "ward_mapping",
            "feature_config", "feature_cols",
            "ohe_cols", "freq_cols", "numeric_cols",
            "target_col", "target_transform",
        )
        for artifact in top_level_artifacts:
            if artifact in bundle:
                cache_k = self._cache_key(artifact, key)
                if cache_k not in self._cache:
                    self._cache[cache_k] = bundle[artifact]


# Singleton — import từ mọi nơi trong app
registry = ModelRegistry()
