"""
app/ml/schemas.py
──────────────────
Các dataclass nội bộ dùng trong ML layer.
Tách biệt hoàn toàn với Pydantic HTTP schema ở routes/.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class ModelKey:
    """
    Khoá định danh duy nhất cho một model.
    Dùng làm key trong ModelRegistry cache dict.

    Ví dụ:
        ModelKey("hanoi", "land")      → hanoi_land.pkl
        ModelKey("hcm", "non_land")    → hcm_non_land.pkl
    """
    city:       str
    model_type: str  # "land" | "non_land"

    @property
    def filename(self) -> str:
        return f"{self.city}_{self.model_type}.pkl"

    def __str__(self) -> str:
        return f"{self.city}_{self.model_type}"


@dataclass
class PredictInput:
    """
    Input đã được validate, sẵn sàng đưa vào feature_builder.
    Phản ánh đúng những gì model ML cần.
    """
    city:          str
    model_type:    str
    district:      str
    ward:          str
    area:          float
    property_type: str
    description:   str =""
    # optional — có hay không tùy city/model
    street:        Optional[str] = None
    bedrooms:      Optional[int] = None
    bathrooms:     Optional[int] = None

    @property
    def model_key(self) -> ModelKey:
        return ModelKey(self.city, self.model_type)


@dataclass
class PredictOutput:
    """
    Output từ ML layer trả về cho service layer.
    """
    price_low:    float
    price_mid:    float
    price_high:   float
    confidence:   float
    model_used:   str
    is_fallback:  bool = False   # True nếu dùng mock thay vì model thật

    def to_dict(self) -> dict:
        return {
            "price_low":   self.price_low,
            "price_mid":   self.price_mid,
            "price_high":  self.price_high,
            "confidence":  self.confidence,
            "model_used":  self.model_used,
            "is_fallback": self.is_fallback,
        }
