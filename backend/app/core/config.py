"""
app/core/config.py
──────────────────
Nguồn duy nhất cho toàn bộ cấu hình ứng dụng.
Đọc từ biến môi trường (.env), có giá trị mặc định hợp lý.
"""

import os
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────

# Root của backend/ (thư mục chứa main.py)
# config.py nằm ở app/core/config.py
# parents[0] = app/core | parents[1] = app | parents[2] = backend/
BASE_DIR = Path(__file__).resolve().parents[2]

# Thư mục chứa các file .pkl
# Ưu tiên env var PKL_DIR nếu được set (hữu ích khi mount volume Docker)
# Mặc định: BASE_DIR/pkl_models — luôn là absolute path
_pkl_dir_env = os.getenv("PKL_DIR")
PKL_DIR: Path = Path(_pkl_dir_env).resolve() if _pkl_dir_env else (BASE_DIR / "pkl_models")


# ── App ───────────────────────────────────────────────────────────────────────

APP_ENV     = os.getenv("ENV", "development")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
IS_PROD     = APP_ENV == "production"

CORS_ORIGINS: list[str] = os.getenv("CORS_ORIGINS", "*").split(",")


# ── Model registry ────────────────────────────────────────────────────────────

VALID_CITIES      = {"hanoi", "hcm", "danang", "hue", "dongnai", "cantho", "haiphong"}
VALID_MODEL_TYPES = {"land", "non_land"}

PKL_FILENAME_PATTERN = "{city}_{model_type}.pkl"

STRICT_MODEL_LOADING = os.getenv("STRICT_MODEL_LOADING", "false").lower() == "true"


# ── Prediction ────────────────────────────────────────────────────────────────

MOCK_PRICE_PER_M2: dict[str, dict[str, tuple[float, float]]] = {
    "hanoi":   {"land": (45_000_000, 180_000_000), "non_land": (30_000_000, 120_000_000)},
    "hcm":     {"land": (50_000_000, 200_000_000), "non_land": (35_000_000, 150_000_000)},
    "danang":  {"land": (25_000_000, 100_000_000), "non_land": (18_000_000,  80_000_000)},
    "haiphong":{"land": (25_000_000, 100_000_000), "non_land": (18_000_000,  80_000_000)},
    "hue":     {"land": (12_000_000,  60_000_000), "non_land": (10_000_000,  50_000_000)},
    "dongnai": {"land": (10_000_000,  55_000_000), "non_land": ( 8_000_000,  45_000_000)},
    "cantho":  {"land": (10_000_000,  50_000_000), "non_land": ( 8_000_000,  40_000_000)},
}

PRICE_INTERVAL_RATIO = float(os.getenv("PRICE_INTERVAL_RATIO", "0.18"))
