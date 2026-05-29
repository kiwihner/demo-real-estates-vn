"""
app/core/exceptions.py
───────────────────────
Exception hierarchy của ứng dụng.
Tách biệt lỗi business logic khỏi lỗi hệ thống.
"""


class PropVisionError(Exception):
    """Base exception — tất cả lỗi nội bộ đều kế thừa từ đây."""
    pass


# ── Model errors ──────────────────────────────────────────────────────────────

class ModelNotFoundError(PropVisionError):
    """File .pkl chưa tồn tại cho city + model_type yêu cầu."""
    def __init__(self, city: str, model_type: str):
        self.city = city
        self.model_type = model_type
        super().__init__(
            f"Model chưa có cho '{city}' / '{model_type}'. "
            f"Đặt file pkl_models/{city}_{model_type}.pkl để kích hoạt."
        )


class ModelLoadError(PropVisionError):
    """File .pkl tồn tại nhưng không load được (corrupt, incompatible version...)."""
    def __init__(self, path: str, reason: str):
        self.path = path
        super().__init__(f"Không thể load model '{path}': {reason}")


class FeatureBuildError(PropVisionError):
    """Không thể xây dựng feature vector từ input."""
    pass


# ── Input validation errors ───────────────────────────────────────────────────

class InvalidCityError(PropVisionError):
    """City ID không hợp lệ."""
    def __init__(self, city: str, valid: set):
        super().__init__(
            f"City '{city}' không hợp lệ. Chọn một trong: {sorted(valid)}"
        )


class InvalidModelTypeError(PropVisionError):
    """Model type không hợp lệ."""
    def __init__(self, model_type: str, valid: set):
        super().__init__(
            f"Model type '{model_type}' không hợp lệ. Chọn: {sorted(valid)}"
        )
