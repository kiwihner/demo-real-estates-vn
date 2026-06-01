"""
app/services/predictor.py
──────────────────────────
Orchestration layer — kết nối HTTP request với ML pipeline.

Flow một request:
  1. Nhận PredictInput (đã validate từ route)
  2. Inject mock description nếu user để trống
  3. Kiểm tra registry xem .pkl có sẵn không
  4a. Có model → build_features() → model.predict() → expm1 → wrap output
  4b. Không có model → mock fallback (dev / demo)
  5. Trả PredictOutput

Key notes:
  - Model được train với target = log1p(price) → predict trả log → expm1 để ra VNĐ
  - Price range = ±PRICE_INTERVAL_RATIO × price_mid
  - Confidence: range heuristic (estimators_ loop đã bị bỏ để tránh timeout)
  - description là optional từ frontend — nếu rỗng sẽ inject mock description tối giản
    để feature_builder vẫn build được nhưng keyword features = 0 → khoảng giá kém
    chính xác hơn, confidence thấp hơn — đúng ý muốn
"""

from __future__ import annotations

import logging
import random
from dataclasses import replace as _dc_replace
from typing import Any

import numpy as np

from app.core.config import MOCK_PRICE_PER_M2, PRICE_INTERVAL_RATIO
from app.core.exceptions import FeatureBuildError
from app.ml.feature_builder import build_features
from app.ml.registry import registry
from app.ml.schemas import ModelKey, PredictInput, PredictOutput

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# MOCK DESCRIPTION — inject khi user để trống description
# ═══════════════════════════════════════════════════════════════════════════════

_MOCK_DESCRIPTION_TEMPLATES = {
    "land": (
        "Bất động sản loại {property_type} tại phường {ward}, quận {district}. "
        "Diện tích {area}m2."
    ),
    "non_land": (
        "Nhà ở loại {property_type} tại phường {ward}, quận {district}. "
        "Diện tích {area}m2, {bedrooms} phòng ngủ, {bathrooms} phòng tắm."
    ),
}


def _inject_mock_description(inp: PredictInput) -> PredictInput:
    if inp.description and len(inp.description.strip()) >= 5:
        return inp

    template = _MOCK_DESCRIPTION_TEMPLATES.get(
        inp.model_type,
        _MOCK_DESCRIPTION_TEMPLATES["land"],
    )
    mock_desc = template.format(
        property_type = inp.property_type or "nhà đất",
        ward          = inp.ward          or "không rõ",
        district      = inp.district      or "không rõ",
        area          = int(inp.area)     if inp.area else 0,
        bedrooms      = int(inp.bedrooms  or 0),
        bathrooms     = int(inp.bathrooms or 0),
    )

    logger.info(
        f"[Predictor] description rỗng → mock: \"{mock_desc[:80]}…\" "
        f"(keyword features sẽ = 0)"
    )
    return _dc_replace(inp, description=mock_desc)


# ═══════════════════════════════════════════════════════════════════════════════
# PUBLIC ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def run_prediction(inp: PredictInput) -> PredictOutput:
    logger.info(
        f"[Predictor] city={inp.city} model={inp.model_type} "
        f"area={inp.area}m² district={inp.district} ward={inp.ward}"
    )

    inp   = _inject_mock_description(inp)
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
    X = build_features(inp)

    # Cities dùng target log1p(price_per_m2) → phải nhân area để ra price
    # Cần Thơ dùng log1p(price) thẳng nên KHÔNG nhân area
    PRICE_PER_M2_TARGET_CITIES = {"danang", "haiphong", "dongnai"}

    try:
        if inp.city == "hue":
            log_pred = _predict_hue(model, key, X)
        elif inp.city == "cantho":
            log_pred = _predict_cantho(model, key, X)
        else:
            log_pred = _predict_with_retry(model, X)

        pred_val = float(np.expm1(log_pred[0]))

        if inp.city in PRICE_PER_M2_TARGET_CITIES:
            price_mid = pred_val * inp.area
            logger.info(f"[Predictor] price_per_m2={pred_val:,.0f} × area={inp.area} = {price_mid:,.0f}")
        else:
            price_mid = pred_val

    except FeatureBuildError:
        raise
    except Exception as exc:
        raise FeatureBuildError(
            f"Model predict thất bại: {exc}. "
            "Kiểm tra feature vector có khớp với lúc train không."
        ) from exc

    if not (1e8 <= price_mid <= 5e11):
        logger.warning(
            f"[Predictor] Predicted price {price_mid:,.0f} ngoài khoảng hợp lý "
            f"(100tr – 500 tỷ). Có thể feature mismatch."
        )

    price_low  = price_mid * (1 - PRICE_INTERVAL_RATIO)
    price_high = price_mid * (1 + PRICE_INTERVAL_RATIO)
    confidence = _estimate_confidence(price_low, price_high, price_mid)

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
    Huế: bundle lưu artifacts riêng (imputer, capper, preprocessor) tách biệt với model.
    Pipeline thực = imputer → capper → preprocessor → model.predict(array).
    KHÔNG fallback về _predict_with_retry vì raw DataFrame sẽ sai shape.
    """
    import pandas as pd

    artifacts = registry.get_artifact(key, "artifacts")

    if not artifacts or not isinstance(artifacts, dict):
        raise FeatureBuildError(
            f"Hue artifacts not found for {key}. "
            "Bundle phải có key 'artifacts' chứa imputer, capper, preprocessor."
        )

    imputer      = artifacts.get("imputer")
    capper       = artifacts.get("capper")
    preprocessor = artifacts.get("preprocessor")

    if imputer is None or preprocessor is None:
        raise FeatureBuildError(
            f"Hue artifacts incomplete for {key}: "
            f"imputer={imputer is not None}, preprocessor={preprocessor is not None}"
        )

    logger.info(f"[Predictor] Hue transform: imputer→capper→preprocessor→{type(model).__name__}")

    # Step 1: KMeansClusterMeanImputer
    X_imp = imputer.transform(X)
    if not isinstance(X_imp, pd.DataFrame):
        X_imp = pd.DataFrame(X_imp, columns=X.columns)

    # Step 2: IQRCapper
    X_cap = capper.transform(X_imp) if capper is not None else X_imp
    if not isinstance(X_cap, pd.DataFrame):
        X_cap = pd.DataFrame(X_cap, columns=X_imp.columns)

    # Step 3: ColumnTransformer → numpy array
    X_trans = preprocessor.transform(X_cap)
    logger.info(f"[Predictor] Hue X_trans shape: {X_trans.shape}")

    # Step 4: predict
    return model.predict(X_trans)


def _predict_cantho(model: Any, key: "ModelKey", X: "pd.DataFrame") -> Any:
    """
    Cần Thơ: pipeline = ColumnTransformer(ohe+freq+num) → LGBMRegressor.
    Pipeline nhận raw DataFrame với đúng feature_cols.
    Timeout xảy ra khi LightGBM predict lần đầu tiên (cold start với large model).
    Dùng thread timeout 55s để surface lỗi thay vì nginx timeout mà không có log.
    """
    import concurrent.futures

    logger.info(f"[Predictor] CanTho predict: X shape={X.shape}, cols={X.columns.tolist()}")

    def _do_predict():
        return model.predict(X)

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_do_predict)
        try:
            result = future.result(timeout=55)
            logger.info(f"[Predictor] CanTho predict OK: {result}")
            return result
        except concurrent.futures.TimeoutError:
            raise FeatureBuildError(
                "CanTho model.predict() vượt quá 55s. "
                "LightGBM cold start hoặc ColumnTransformer bị treo. "
                f"X shape={X.shape}, dtypes={X.dtypes.to_dict()}"
            )


def _predict_with_retry(model: Any, X: "pd.DataFrame") -> Any:
    """
    Gọi model.predict(X). Retry với category dtype nếu XGBoost enable_categorical.
    """
    try:
        return model.predict(X)
    except Exception as exc:
        err = str(exc)
        if "categorical" in err.lower() or "dtypes for data must be int" in err:
            logger.info("[Predictor] Retrying with category dtype cast (enable_categorical mode)")
            X_cat = X.copy()
            for col in X_cat.columns:
                if X_cat[col].dtype == object or str(X_cat[col].dtype) == "string":
                    X_cat[col] = X_cat[col].astype("category")
            return model.predict(X_cat)
        raise


def _estimate_confidence(
    price_low: float,
    price_high: float,
    price_mid: float,
) -> float:
    """
    Ước lượng confidence từ khoảng giá (heuristic).
    KHÔNG dùng estimators_ loop — gây timeout với RF/XGB nhiều cây.
    """
    range_ratio = (price_high - price_low) / (price_mid + 1)
    confidence  = max(0.55, min(0.93, 1 - range_ratio * 0.8))
    return round(float(confidence), 2)


# ═══════════════════════════════════════════════════════════════════════════════
# MOCK FALLBACK
# ═══════════════════════════════════════════════════════════════════════════════

def _predict_mock(key: ModelKey, inp: PredictInput) -> PredictOutput:
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
    return round(value / 1_000_000) * 1_000_000