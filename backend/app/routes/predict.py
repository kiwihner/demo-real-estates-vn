"""
app/routes/predict.py
──────────────────────
HTTP layer — mỏng nhất có thể.
Chỉ làm 3 việc:
  1. Validate request (Pydantic)
  2. Gọi service
  3. Trả response

Không chứa business logic.

──────────────────────
CITIES hỗ trợ:
  hanoi   → Hà Nội (có street)
  hcm     → TP. Hồ Chí Minh (có street)
  danang  → Đà Nẵng
  hue     → Huế / Thừa Thiên Huế
  dongnai → Đồng Nai
  cantho  → Cần Thơ

MODEL TYPES:
  land     → Đất / Nhà đất (không cần bedrooms/bathrooms)
  non_land → Căn hộ / Nhà phố / Nhà riêng (cần bedrooms + bathrooms)

STREET:
  Bắt buộc khi city = hanoi hoặc hcm.
  Bỏ qua cho các city còn lại.
"""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, field_validator, model_validator

from app.core.config import VALID_CITIES, VALID_MODEL_TYPES
from app.core.exceptions import (
    FeatureBuildError,
    InvalidCityError,
    InvalidModelTypeError,
    ModelNotFoundError,
)
from app.ml.schemas import PredictInput
from app.services.predictor import run_prediction

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/predict", tags=["Prediction"])

# Cities yêu cầu street input để model cho kết quả tốt
STREET_REQUIRED_CITIES = {"hanoi", "hcm"}


# ═══════════════════════════════════════════════════════════════════════════════
# REQUEST SCHEMA
# ═══════════════════════════════════════════════════════════════════════════════

class PredictRequest(BaseModel):
    # ── Bắt buộc ─────────────────────────────────────────────────────────────
    city: str = Field(
        ...,
        description="ID thành phố: hanoi | hcm | danang | hue | dongnai | cantho",
        examples=["hcm"],
    )
    modelType: str = Field(
        ...,
        description="Loại model: land | non_land",
        examples=["land"],
    )
    district: str = Field(
        ..., min_length=1, max_length=100,
        description="Quận / Huyện (VD: Bình Thạnh)",
        examples=["Bình Thạnh"],
    )
    ward: str = Field(
        ..., min_length=1, max_length=100,
        description="Phường / Xã (VD: Phường 13)",
        examples=["Phường 13"],
    )
    area: float = Field(
        ..., gt=0, le=100_000,
        description="Diện tích m²",
        examples=[75.0],
    )
    propertyType: str = Field(
        ..., min_length=1, max_length=100,
        description="Loại hình BĐS (VD: Nhà mặt phố, Căn hộ chung cư)",
        examples=["Nhà mặt phố"],
    )
    description: str = Field(
        ..., min_length=10, max_length=3000,
        description="Mô tả BĐS — càng chi tiết model càng chính xác",
        examples=["Nhà mặt tiền đường rộng, sổ hồng chính chủ, gần trung tâm"],
    )

    # ── Tùy chọn ─────────────────────────────────────────────────────────────
    street: Optional[str] = Field(
        None, max_length=200,
        description="Tên đường — BẮT BUỘC cho hanoi và hcm để model chính xác hơn",
        examples=["Đinh Bộ Lĩnh"],
    )
    bedrooms: Optional[int] = Field(
        None, ge=0, le=50,
        description="Số phòng ngủ — chỉ dùng cho modelType=non_land",
        examples=[3],
    )
    bathrooms: Optional[int] = Field(
        None, ge=0, le=20,
        description="Số phòng tắm — chỉ dùng cho modelType=non_land",
        examples=[2],
    )

    # ── Validators ────────────────────────────────────────────────────────────

    @field_validator("city")
    @classmethod
    def validate_city(cls, v: str) -> str:
        v = v.strip().lower()
        if v not in VALID_CITIES:
            raise ValueError(
                f"city '{v}' không hợp lệ. "
                f"Hợp lệ: {sorted(VALID_CITIES)}"
            )
        return v

    @field_validator("modelType")
    @classmethod
    def validate_model_type(cls, v: str) -> str:
        v = v.strip().lower()
        if v not in VALID_MODEL_TYPES:
            raise ValueError(
                f"modelType '{v}' không hợp lệ. "
                f"Hợp lệ: {sorted(VALID_MODEL_TYPES)}"
            )
        return v

    @model_validator(mode="after")
    def cross_validate(self) -> "PredictRequest":
        # Cảnh báo nếu city cần street mà không có
        if self.city in STREET_REQUIRED_CITIES and not self.street:
            logger.warning(
                f"[Route] city={self.city} nhưng street không được cung cấp. "
                "Model sẽ dùng frequency=0 cho street features — kết quả kém chính xác hơn."
            )

        # Bỏ qua bedrooms/bathrooms nếu là land model
        if self.modelType == "land":
            if self.bedrooms is not None or self.bathrooms is not None:
                logger.info(
                    "[Route] bedrooms/bathrooms bị bỏ qua vì modelType=land"
                )

        return self


# ═══════════════════════════════════════════════════════════════════════════════
# RESPONSE SCHEMA
# ═══════════════════════════════════════════════════════════════════════════════

class PropertyInfo(BaseModel):
    """Echo lại thông tin BĐS để frontend hiển thị cùng kết quả."""
    city:         str
    modelType:    str
    district:     str
    ward:         str
    area:         float
    propertyType: str
    street:       Optional[str] = None
    bedrooms:     Optional[int] = None
    bathrooms:    Optional[int] = None


class PredictResponse(BaseModel):
    # ── Kết quả định giá ─────────────────────────────────────────────────────
    price_low:  float = Field(..., description="Giá thấp nhất ước tính (VNĐ)")
    price_mid:  float = Field(..., description="Giá trung bình ước tính (VNĐ)")
    price_high: float = Field(..., description="Giá cao nhất ước tính (VNĐ)")
    confidence: float = Field(..., ge=0, le=1, description="Độ tin cậy mô hình (0–1)")
    model_used: str   = Field(..., description="Tên model đã dùng")
    is_fallback: bool = Field(..., description="True nếu chưa có .pkl, đang dùng mock")

    # ── Thông tin BĐS đầu vào ────────────────────────────────────────────────
    property_info: PropertyInfo

    # ── Derived — tính sẵn cho frontend ──────────────────────────────────────
    price_per_sqm:     float = Field(..., description="Giá trung bình / m² (VNĐ)")
    price_range_label: str   = Field(..., description="VD: '3,2 tỷ – 4,8 tỷ'")
    confidence_label:  str   = Field(..., description="VD: '85%'")

    # ── Warning ───────────────────────────────────────────────────────────────
    warnings: list[str] = Field(
        default_factory=list,
        description="Cảnh báo về chất lượng dự đoán (nếu có)",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# ROUTE
# ═══════════════════════════════════════════════════════════════════════════════

@router.post(
    "",
    response_model=PredictResponse,
    summary="Dự đoán giá bất động sản",
    description=(
        "Nhận thông tin BĐS, trả về khoảng giá dự đoán kèm độ tin cậy.\n\n"
        "**Street**: Bắt buộc với `city=hanoi` hoặc `city=hcm` để model cho kết quả tốt nhất.\n\n"
        "**Bedrooms / Bathrooms**: Chỉ cần với `modelType=non_land`."
    ),
)
async def predict(req: PredictRequest):
    warnings: list[str] = []

    # Cảnh báo chất lượng dự đoán
    if req.city in STREET_REQUIRED_CITIES and not req.street:
        warnings.append(
            f"Không có tên đường (street) cho city={req.city}. "
            "Kết quả có thể kém chính xác hơn — khuyến nghị nhập tên đường."
        )
    if req.modelType == "non_land" and (req.bedrooms is None or req.bathrooms is None):
        warnings.append(
            "Thiếu số phòng ngủ hoặc phòng tắm cho modelType=non_land. "
            "Model sẽ dùng giá trị mặc định = 0."
        )

    try:
        # ── 1. Build ML input ─────────────────────────────────────────────────
        inp = PredictInput(
            city          = req.city,
            model_type    = req.modelType,
            district      = req.district,
            ward          = req.ward,
            area          = req.area,
            property_type = req.propertyType,
            description   = req.description,
            street        = req.street if req.city in STREET_REQUIRED_CITIES else None,
            bedrooms      = req.bedrooms  if req.modelType == "non_land" else None,
            bathrooms     = req.bathrooms if req.modelType == "non_land" else None,
        )

        # ── 2. Run prediction ─────────────────────────────────────────────────
        output = run_prediction(inp)

        if output.is_fallback:
            warnings.append(
                f"Model .pkl cho {req.city}/{req.modelType} chưa được tải. "
                "Giá hiển thị là ước tính mock — chưa có độ tin cậy thực."
            )

        # ── 3. Build response ─────────────────────────────────────────────────
        is_non_land = req.modelType == "non_land"

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
                street       = req.street if req.city in STREET_REQUIRED_CITIES else None,
                bedrooms     = req.bedrooms  if is_non_land else None,
                bathrooms    = req.bathrooms if is_non_land else None,
            ),

            price_per_sqm     = round(output.price_mid / req.area),
            price_range_label = _fmt_range(output.price_low, output.price_high),
            confidence_label  = f"{round(output.confidence * 100)}%",
            warnings          = warnings,
        )

    # ── Known business errors → 4xx ──────────────────────────────────────────
    except (InvalidCityError, InvalidModelTypeError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    except ModelNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    except FeatureBuildError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )

    # ── Unknown errors → 500 ─────────────────────────────────────────────────
    except Exception as exc:
        logger.exception(f"[Route] Unexpected error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi hệ thống. Vui lòng thử lại sau.",
        )


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _fmt_vnd(value: float) -> str:
    """3_200_000_000 → '3,2 tỷ' | 450_000_000 → '450 triệu'"""
    if value >= 1_000_000_000:
        v = value / 1_000_000_000
        s = f"{v:.1f} tỷ"
        return s.replace(".0 ", " ")
    if value >= 1_000_000:
        v = value / 1_000_000
        return f"{v:.0f} triệu"
    return f"{value:,.0f} đ"


def _fmt_range(low: float, high: float) -> str:
    return f"{_fmt_vnd(low)} – {_fmt_vnd(high)}"
