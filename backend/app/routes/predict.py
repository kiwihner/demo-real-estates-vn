"""
app/routes/predict.py
──────────────────────
HTTP layer — validate request, gọi service, trả response.
Không chứa business logic.

Thay đổi so với version trước:
  - PredictResponse thêm field "features_used" để debug
  - Thêm endpoint GET /predict/debug/{city}/{model_type}
    → trả về feature vector mẫu không cần call model
  - PropertyInfo thêm description để frontend hiển thị lại
"""

import logging
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field, field_validator, model_validator

from app.core.config import VALID_CITIES, VALID_MODEL_TYPES
from app.core.exceptions import (
    FeatureBuildError,
    InvalidCityError,
    InvalidModelTypeError,
    ModelNotFoundError,
)
from app.ml.feature_builder import build_features
from app.ml.registry import registry
from app.ml.schemas import ModelKey, PredictInput
from app.services.predictor import run_prediction

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Prediction"])


# ─────────────────────────────────────────────────────────────────────────────
# Request schema
# ─────────────────────────────────────────────────────────────────────────────

class PredictRequest(BaseModel):
    # ── Required ──────────────────────────────────────────────────────────────
    city:         str   = Field(..., description="hanoi | hcm | danang | hue | dongnai | cantho")
    modelType:    str   = Field(..., description="land | non_land")
    district:     str   = Field(..., min_length=1,  max_length=200, description="Quận / Huyện")
    ward:         str   = Field(..., min_length=1,  max_length=200, description="Phường / Xã")
    area:         float = Field(..., gt=0, le=100_000,              description="Diện tích m²")
    propertyType: str   = Field(..., min_length=1,  max_length=200, description="Loại hình BĐS")
    description:  str   = Field("",  max_length=3000, description="Mô tả BĐS (optional, để trống → backend dùng mock)")

    # ── Optional ──────────────────────────────────────────────────────────────
    street:    Optional[str] = Field(None, max_length=200, description="Tên đường (HN/HCM)")
    bedrooms:  Optional[int] = Field(None, ge=0, le=50,    description="Số phòng ngủ (non_land)")
    bathrooms: Optional[int] = Field(None, ge=0, le=20,    description="Số phòng tắm (non_land)")

    # ── Validators ────────────────────────────────────────────────────────────
    @field_validator("city")
    @classmethod
    def validate_city(cls, v: str) -> str:
        v = v.strip().lower()
        if v not in VALID_CITIES:
            raise ValueError(f"city '{v}' không hợp lệ. Chọn: {sorted(VALID_CITIES)}")
        return v

    @field_validator("modelType")
    @classmethod
    def validate_model_type(cls, v: str) -> str:
        v = v.strip().lower()
        if v not in VALID_MODEL_TYPES:
            raise ValueError(f"modelType '{v}' không hợp lệ. Chọn: {sorted(VALID_MODEL_TYPES)}")
        return v

    @model_validator(mode="after")
    def warn_land_with_rooms(self) -> "PredictRequest":
        if self.modelType == "land" and (self.bedrooms or self.bathrooms):
            logger.warning("[Route] bedrooms/bathrooms ignored for land model")
        return self


# ─────────────────────────────────────────────────────────────────────────────
# Response schemas
# ─────────────────────────────────────────────────────────────────────────────

class PropertyInfo(BaseModel):
    """Echo lại thông tin BĐS người dùng nhập."""
    city:         str
    modelType:    str
    district:     str
    ward:         str
    area:         float
    propertyType: str
    description:  str
    street:       Optional[str] = None
    bedrooms:     Optional[int] = None
    bathrooms:    Optional[int] = None


class PredictResponse(BaseModel):
    model_config = {"protected_namespaces": ()}  # suppress model_* namespace warning

    # ── Kết quả định giá ──────────────────────────────────────────────────────
    price_low:         float = Field(..., description="Giá thấp nhất ước tính (VNĐ)")
    price_mid:         float = Field(..., description="Giá trung bình ước tính (VNĐ)")
    price_high:        float = Field(..., description="Giá cao nhất ước tính (VNĐ)")
    confidence:        float = Field(..., ge=0, le=1, description="Độ chính xác model (0–1)")
    model_used:        str   = Field(..., description="Tên model đã dùng")
    is_fallback:       bool  = Field(..., description="True nếu chưa có .pkl")

    # ── Thông tin BĐS đã nhập ─────────────────────────────────────────────────
    property_info:     PropertyInfo = Field(..., description="Thông tin BĐS được định giá")

    # ── Derived fields — frontend dùng trực tiếp ──────────────────────────────
    price_per_sqm:     float = Field(..., description="Giá trung bình / m²")
    price_range_label: str   = Field(..., description="VD: '3,2 tỷ – 4,8 tỷ'")
    confidence_label:  str   = Field(..., description="VD: '85%'")
    target_mode:       str   = Field(..., description="Cách model predict: price_per_m2 | log_price | ...")

    # ── Debug (chỉ trả về khi ENV != production) ──────────────────────────────
    features_count:    Optional[int]  = Field(None, description="Số features đã build")


# ─────────────────────────────────────────────────────────────────────────────
# POST /predict  — main endpoint
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/predict",
    response_model=PredictResponse,
    summary="Dự đoán giá bất động sản",
    description=(
        "Nhận thông tin BĐS từ frontend, trả về khoảng giá dự đoán "
        "kèm độ chính xác và thông tin BĐS echo lại.\n\n"
        "**Target modes** (từ meta.pkl):\n"
        "- `price_per_m2`: model predict đơn giá/m² → nhân area\n"
        "- `log_price`: model predict log1p(price) → expm1\n"
        "- `log_price_per_m2`: model predict log1p(price/m²) → expm1 × area\n"
        "- `price`: model predict giá tuyệt đối"
    ),
)
async def predict(req: PredictRequest):
    try:
        inp = _build_predict_input(req)

        # Build feature count (dev only) — dùng get_artifact thay vì get_meta
        features_count = None
        try:
            from app.core.config import IS_PROD
            if not IS_PROD:
                df_debug       = build_features(inp)
                features_count = len(df_debug.columns)
        except Exception:
            pass

        output = run_prediction(inp)

        # Lấy target_mode từ bundle artifact nếu có
        target_mode = "price_per_m2"
        try:
            freq_maps = registry.get_artifact(inp.model_key, "freq_maps")
            # target_mode không được lưu riêng trong registry mới
            # → hardcode theo city convention đã biết
            _CITY_TARGET_MODE = {
                "hanoi":    "log_price",
                "hcm":      "log_price",
                "danang":   "log_price_per_m2",
                "haiphong": "log_price_per_m2",
                "dongnai":  "log_price_per_m2",
                "hue":      "log_price",
                "cantho":   "log_price",
            }
            target_mode = _CITY_TARGET_MODE.get(req.city, "log_price")
        except Exception:
            pass

        return PredictResponse(
            price_low   = output.price_low,
            price_mid   = output.price_mid,
            price_high  = output.price_high,
            confidence  = output.confidence,
            model_used  = output.model_used,
            is_fallback = output.is_fallback,

            property_info = PropertyInfo(
                city         = req.city,
                modelType    = req.modelType,
                district     = req.district,
                ward         = req.ward,
                area         = req.area,
                propertyType = req.propertyType,
                description  = req.description,
                street       = req.street,
                bedrooms     = req.bedrooms  if req.modelType == "non_land" else None,
                bathrooms    = req.bathrooms if req.modelType == "non_land" else None,
            ),

            price_per_sqm     = round(output.price_mid / req.area),
            price_range_label = _fmt_range(output.price_low, output.price_high),
            confidence_label  = f"{round(output.confidence * 100)}%",
            target_mode       = target_mode,
            features_count    = features_count,
        )

    except (InvalidCityError, InvalidModelTypeError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,       detail=str(exc))
    except ModelNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,         detail=str(exc))
    except FeatureBuildError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    except Exception as exc:
        logger.exception(f"[Route] Unhandled error: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Lỗi hệ thống. Vui lòng thử lại sau.")


# ─────────────────────────────────────────────────────────────────────────────
# GET /predict/debug/{city}/{model_type}  — xem feature vector mẫu
# ─────────────────────────────────────────────────────────────────────────────

@router.get(
    "/predict/debug/{city}/{model_type}",
    summary="[Dev] Xem feature vector mẫu",
    description="Trả về feature DataFrame mẫu với input giả để kiểm tra feature building.",
)
async def debug_features(
    city:       str,
    model_type: str,
    district:   str = Query("hoàn kiếm",  description="Quận/Huyện"),
    ward:       str = Query("hàng bài",   description="Phường/Xã"),
    area:       float = Query(85.0,       description="Diện tích m²"),
    street:     Optional[str] = Query(None, description="Tên đường"),
    description: str = Query(
        "nhà mặt tiền sổ hồng chính chủ gần trung tâm ô tô vào thoải mái",
        description="Mô tả BĐS"
    ),
):
    from app.core.config import IS_PROD
    if IS_PROD:
        raise HTTPException(status_code=403, detail="Debug endpoint disabled in production")

    if city not in VALID_CITIES:
        raise HTTPException(status_code=400, detail=f"city không hợp lệ: {city}")
    if model_type not in VALID_MODEL_TYPES:
        raise HTTPException(status_code=400, detail=f"model_type không hợp lệ: {model_type}")

    inp = PredictInput(
        city=city, model_type=model_type,
        district=district, ward=ward, area=area,
        property_type="đất thổ cư" if model_type == "land" else "chung cư / căn hộ",
        description=description,
        street=street,
        bedrooms=2 if model_type == "non_land" else None,
        bathrooms=2 if model_type == "non_land" else None,
    )

    # registry mới dùng get_artifact() thay vì get_meta()/has_meta()/has_model()
    df   = build_features(inp)

    _CITY_TARGET_MODE = {
        "hanoi": "log_price", "hcm": "log_price",
        "danang": "log_price_per_m2", "haiphong": "log_price_per_m2",
        "dongnai": "log_price_per_m2", "hue": "log_price", "cantho": "log_price",
    }

    return {
        "city":          city,
        "model_type":    model_type,
        "has_meta":      registry.get_artifact(inp.model_key, "freq_maps") is not None,
        "has_model":     registry.is_available(inp.model_key),
        "target_mode":   _CITY_TARGET_MODE.get(city, "log_price"),
        "features_count": len(df.columns),
        "features": {
            col: (
                round(float(df[col].iloc[0]), 6)
                if isinstance(df[col].iloc[0], (int, float))
                else str(df[col].iloc[0])
            )
            for col in df.columns
        },
    }


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _build_predict_input(req: PredictRequest) -> PredictInput:
    return PredictInput(
        city          = req.city,
        model_type    = req.modelType,
        district      = req.district,
        ward          = req.ward,
        area          = req.area,
        property_type = req.propertyType,
        description   = req.description,
        street        = req.street,
        bedrooms      = req.bedrooms  if req.modelType == "non_land" else None,
        bathrooms     = req.bathrooms if req.modelType == "non_land" else None,
    )


def _fmt_vnd(value: float) -> str:
    if value >= 1_000_000_000:
        v = value / 1_000_000_000
        s = f"{v:.2f}".rstrip("0").rstrip(".")
        return f"{s} tỷ"
    if value >= 1_000_000:
        v = value / 1_000_000
        return f"{v:.0f} triệu"
    return f"{value:,.0f} đ"


def _fmt_range(low: float, high: float) -> str:
    return f"{_fmt_vnd(low)} – {_fmt_vnd(high)}"