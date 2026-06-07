"""
app/ml/feature_builder.py
──────────────────────────
Chuyển đổi PredictInput → pandas DataFrame khớp chính xác với
feature vector lúc train từng notebook.

TARGET variable theo city:
  HN  (hanoi)   → log1p(price_vnd)       → predictor dùng expm1() ra VNĐ
  HCM (hcm)     → log1p(price_vnd)       → predictor dùng expm1() ra VNĐ
  DN  (danang)  → log1p(price_per_m2)    → predictor dùng expm1() × area ra VNĐ
  (other cities sẽ cần cập nhật khi có notebook)
"""

from __future__ import annotations

import logging
import re
import unicodedata
from typing import Any

import numpy as np
import pandas as pd

from app.core.exceptions import FeatureBuildError
from app.ml.schemas import PredictInput
from app.ml.registry import registry

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# TEXT NORMALIZATION
# ═══════════════════════════════════════════════════════════════════════════════

def _norm(text: str | None) -> str:
    """Strip + collapse whitespace."""
    if not text:
        return ""
    return re.sub(r"\s+", " ", str(text).strip())

def _norm_lower(text: str | None) -> str:
    return _norm(text).lower()

def _remove_accents(text: str) -> str:
    """Bỏ dấu tiếng Việt: 'mặt tiền' → 'mat tien'."""
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return text.replace("đ", "d").replace("Đ", "D")

def _normalize_description_text(text: str | None) -> str:
    """Chuẩn hoá text cho Đà Nẵng: bỏ dấu + lowercase + giữ số và ký tự đặc biệt."""
    if not text:
        return ""
    text = _remove_accents(str(text)).lower()
    text = re.sub(r"[^0-9a-z.,+/%\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


# ═══════════════════════════════════════════════════════════════════════════════
# DISTRICT GROUPS
# ═══════════════════════════════════════════════════════════════════════════════

HANOI_CORE_DISTRICTS  = {"hoàn kiếm", "ba đình", "đống đa", "tây hồ", "hai bà trưng"}
HANOI_URBAN_DISTRICTS = {"cầu giấy", "thanh xuân", "nam từ liêm", "bắc từ liêm",
                          "hoàng mai", "long biên", "hà đông"}
HCM_CORE_DISTRICTS    = {"quận 1", "quận 3", "quận 4", "bình thạnh", "phú nhuận"}
HCM_URBAN_DISTRICTS   = {"quận 2", "quận 7", "quận 10", "quận 11", "quận 5", "quận 6",
                          "tân bình", "tân phú", "gò vấp", "thủ đức"}

CITY_CORE_MAP:  dict[str, set[str]] = {
    "hanoi": HANOI_CORE_DISTRICTS, "hcm": HCM_CORE_DISTRICTS,
}
CITY_URBAN_MAP: dict[str, set[str]] = {
    "hanoi": HANOI_URBAN_DISTRICTS, "hcm": HCM_URBAN_DISTRICTS,
}

CITY_PROVINCE_NORM: dict[str, str] = {
    "hcm": "hồ chí minh", "hanoi": "hà nội",
    "danang": "đà nẵng", "hue": "thừa thiên huế",
    "dongnai": "đồng nai", "cantho": "cần thơ", "haiphong": "hải phòng",
}
STREET_CITIES = {"hanoi", "hcm"}


# ═══════════════════════════════════════════════════════════════════════════════
# KEYWORD RULES — HN / HCM (có dấu, match với _norm_lower)
# ═══════════════════════════════════════════════════════════════════════════════

COMMON_KW: dict[str, list[str]] = {
    "has_mat_tien":         ["mặt tiền", "mặt phố", "mặt đường", "mt phố", "mt đường"],
    "has_goc_2_mat_tien":   ["góc 2 mặt tiền", "2 mặt tiền", "hai mặt tiền", "lô góc"],
    "has_so_hong":          ["sổ hồng", "sổ đỏ", "pháp lý rõ", "sổ riêng", "chính chủ"],
    "has_full_noi_that":    ["full nội thất", "đầy đủ nội thất", "nội thất cao cấp",
                             "full đồ", "tặng nội thất", "có nội thất"],
    "has_hem_xe_hoi":       ["hẻm xe hơi", "hẻm ô tô", "ô tô vào", "oto vào",
                             "ô tô tránh", "hẻm rộng", "ngõ ô tô", "ngõ rộng"],
    "has_hem_ngo":          ["hẻm", "hem"],
    "has_kdc":              ["khu dân cư", "kdc", "khu đô thị"],
    "has_penthouse_duplex": ["penthouse", "duplex", "căn góc"],
}
HN_TRUNG_TAM_KW  = ["trung tâm", "gần trung tâm", "phố cổ", "hoàn kiếm", "ba đình"]
HCM_TRUNG_TAM_KW = ["trung tâm", "gần trung tâm", "quận 1", "quận 3", "bến thành"]
HUE_TRUNG_TAM_KW = ["trung tâm", "gần trung tâm", "sông hương","vincom", "đại nội", "phú hội"]
HN_LAND_KW: dict[str, list[str]] = {
    "land_kw_duong_rong":      ["đường rộng", "đường lớn", "đường thông", "mặt đường lớn"],
    "land_kw_oto_tranh":       ["ô tô tránh", "oto tránh", "2 ô tô tránh", "xe tải vào"],
    "land_kw_ngo_oto":         ["ngõ ô tô", "ngõ oto", "ô tô vào", "ngõ rộng"],
    "land_kw_quy_hoach_risk":  ["dính quy hoạch", "vướng quy hoạch", "quy hoạch treo"],
    "land_kw_khong_quy_hoach": ["không quy hoạch", "ko quy hoạch", "quy hoạch ổn định"],
    "land_kw_no_hau":          ["nở hậu", "no hau"],
    "land_kw_vuong_van":       ["vuông vắn", "vuong van", "thửa đẹp", "lô đẹp"],
    "land_kw_mat_tien_rong":   ["mặt tiền rộng", "mặt tiền đẹp", "mt rộng"],
    "land_kw_dat_dau_gia":     ["đất đấu giá", "đấu giá"],
    "land_kw_phan_lo":         ["phân lô", "liền kề", "khu đô thị", "kđt"],
    "land_kw_gan_ho":          ["gần hồ", "view hồ", "ven hồ", "hồ tây"],
}
HN_NONLAND_KW: dict[str, list[str]] = {
    "nonland_kw_thang_may":           ["thang máy", "có thang máy"],
    "nonland_kw_nha_moi":             ["nhà mới", "mới xây", "xây mới", "vào ở ngay"],
    "nonland_kw_chung_cu_cao_cap":    ["cao cấp", "luxury", "vinhomes", "masteri", "imperia"],
    "nonland_kw_view_dep":            ["view đẹp", "view hồ", "view sông", "view thoáng"],
    "nonland_kw_gan_metro":           ["metro", "đường sắt đô thị", "ga metro"],
    "nonland_kw_gan_tien_ich":        ["gần trường", "gần chợ", "gần bệnh viện", "gần siêu thị"],
    "nonland_kw_san_thuong":          ["sân thượng", "ban công", "logia"],
    "nonland_kw_kinh_doanh_cho_thue": ["kinh doanh", "cho thuê", "dòng tiền", "shophouse"],
    "nonland_kw_can_goc":             ["căn góc", "hai mặt thoáng", "2 mặt thoáng"],
}

HUE_LAND_KW: dict[str, list[str]] = {
    "land_kw_duong_rong":      ["đường rộng", "đường lớn", "đường thông"],
    "land_kw_ngo_oto":         ["ô tô vào", "ngõ ô tô", "kiệt ô tô"],
    "land_kw_quy_hoach_risk":  ["dính quy hoạch", "quy hoạch treo"],
    "land_kw_khong_quy_hoach": ["không quy hoạch", "pháp lý chuẩn"],
    "land_kw_phan_lo":         ["phân lô", "khu dân cư", "kđt"],
    "land_kw_gan_song_huong":  ["sông hương", "view sông", "ven sông"],
}

HUE_NONLAND_KW: dict[str, list[str]] = {
    "nonland_kw_thang_may":           ["thang máy", "có thang máy"],
    "nonland_kw_nha_moi":             ["nhà mới", "mới xây", "xây mới"],
    "nonland_kw_view_dep":            ["view đẹp", "view sông", "view thoáng"],
    "nonland_kw_gan_tien_ich":        ["gần chợ", "gần trường", "gần bệnh viện"],
    "nonland_kw_kinh_doanh_cho_thue": ["kinh doanh", "cho thuê", "homestay"],
}

# ═══════════════════════════════════════════════════════════════════════════════
# KEYWORD RULES — ĐÀ NẴNG (không dấu, match với _normalize_description_text)
# ═══════════════════════════════════════════════════════════════════════════════

DN_PATTERN_FEATURES: dict[str, str] = {
    "desc_has_legal_docs":          r"\b(?:so do|so hong|so rieng|phap ly|hoan cong|cong chung)\b",
    "desc_has_car_access":          r"\b(?:o to|oto|xe hoi|dau xe|duong o to)\b",
    "desc_has_frontage":            r"\b(?:mat tien|mat pho|mat duong)\b",
    "desc_has_alley":               r"\b(?:hem|kiet|ngo)\b",
    "desc_has_corner":              r"\b(?:lo goc|2 mat tien|hai mat tien|2 mat thoang)\b",
    "desc_has_business":            r"\b(?:kinh doanh|cho thue|dong tien|shophouse|van phong)\b",
    "desc_has_elevator":            r"\b(?:thang may)\b",
    "desc_has_sea_river_lake_view": r"\b(?:view bien|view song|view ho|ven song|gan song|gan bien)\b",
    "desc_has_near_beach":          r"\b(?:gan bien|cach bien|di bo ra bien)\b",
    "desc_has_near_amenities":      r"\b(?:gan cho|gan truong|gan benh vien|gan sieu thi|gan cong vien|gan san bay)\b",
    "desc_has_urgent_sale":         r"\b(?:ban gap|can ban gap|cat lo|giam gia|ngop)\b",
    "desc_has_new_house":           r"\b(?:nha moi|moi xay|xay moi|moi hoan thien)\b",
}


# ═══════════════════════════════════════════════════════════════════════════════
# FEATURE LISTS — khớp chính xác với notebook
# ═══════════════════════════════════════════════════════════════════════════════

# ── Hà Nội ────────────────────────────────────────────────────────────────────
HN_LAND_NUMERIC = [
    "area_m2_raw", "area_m2_missing", "log_area_m2",
    "is_core_district", "is_urban_district", "is_suburban_district",
    "is_tiny_land", "is_small_land", "is_medium_land", "is_large_land",
    "tiny_land_x_core", "large_land_x_suburban", "large_land_x_urban",
    "district_name_freq", "ward_name_freq", "district_address_freq", "ward_address_freq",
    "area_x_district_name_freq", "area_x_ward_name_freq",
    "area_x_district_address_freq", "area_x_ward_address_freq",
    "log_area_x_district_name_freq", "log_area_x_ward_name_freq",
    "log_area_x_district_address_freq", "log_area_x_ward_address_freq",
    "land_frontage_score", "land_accessibility_score", "land_premium_location_score",
    "land_frontage_x_log_area", "land_accessibility_x_log_area",
    "land_premium_location_x_log_area", "land_premium_x_core",
    "land_accessibility_x_urban",
    "land_legal_positive_score", "land_planning_risk_score",
    "land_legal_x_log_area", "land_planning_risk_x_log_area",
    "land_shape_quality_score", "land_shape_quality_x_log_area",
    "has_mat_tien", "has_goc_2_mat_tien", "has_so_hong", "has_gan_trung_tam",
    "land_kw_duong_rong", "land_kw_oto_tranh", "land_kw_ngo_oto",
    "land_kw_quy_hoach_risk", "land_kw_khong_quy_hoach",
    "land_kw_no_hau", "land_kw_vuong_van", "land_kw_mat_tien_rong",
    "land_kw_dat_dau_gia", "land_kw_phan_lo", "land_kw_gan_ho",
    "name_len", "description_len", "description_word_count",
    # street (optional)
    "street_name_freq", "street_address_freq",
    "area_x_street_name_freq", "area_x_street_address_freq",
    "log_area_x_street_name_freq", "log_area_x_street_address_freq",
]
HN_LAND_CATEGORICAL = [
    "property_type_name", "district_address", "ward_address",
    "district_group", "area_bin", "district_area_bin",
    "street_address",
]

HN_NONLAND_NUMERIC = [
    "area_m2_raw", "bedroom_count", "bathroom_count",
    "area_m2_missing", "bedroom_count_missing", "bathroom_count_missing",
    "log_area_m2", "bedroom_per_m2", "bathroom_per_m2", "bathroom_per_bedroom",
    "room_total", "bedroom_x_log_area", "bathroom_x_log_area",
    "is_studio_like", "is_large_unit", "is_family_unit", "room_density_score",
    "district_name_freq", "ward_name_freq", "district_address_freq", "ward_address_freq",
    "area_x_district_name_freq", "area_x_ward_name_freq",
    "area_x_district_address_freq", "area_x_ward_address_freq",
    "log_area_x_district_name_freq", "log_area_x_ward_name_freq",
    "log_area_x_district_address_freq", "log_area_x_ward_address_freq",
    "is_core_district", "is_urban_district", "is_suburban_district",
    "nonland_luxury_score", "nonland_convenience_score",
    "nonland_building_quality_score", "nonland_business_score",
    "nonland_luxury_x_log_area", "nonland_convenience_x_log_area",
    "nonland_building_quality_x_log_area", "nonland_business_x_log_area",
    "nonland_luxury_x_core", "nonland_business_x_core",
    "has_mat_tien", "has_goc_2_mat_tien", "has_so_hong", "has_gan_trung_tam",
    "has_hem_xe_hoi", "has_full_noi_that",
    "nonland_kw_thang_may", "nonland_kw_nha_moi", "nonland_kw_chung_cu_cao_cap",
    "nonland_kw_view_dep", "nonland_kw_gan_metro", "nonland_kw_gan_tien_ich",
    "nonland_kw_san_thuong", "nonland_kw_kinh_doanh_cho_thue", "nonland_kw_can_goc",
    "full_noi_that_x_bedroom", "full_noi_that_x_bathroom",
    "thang_may_x_area", "nha_moi_x_log_area",
    "name_len", "description_len", "description_word_count",
    # street (optional)
    "street_name_freq", "street_address_freq",
    "area_x_street_name_freq", "area_x_street_address_freq",
    "log_area_x_street_name_freq", "log_area_x_street_address_freq",
]
HN_NONLAND_CATEGORICAL = [
    "property_type_name", "district_address", "ward_address",
    "district_group", "area_bin", "district_area_bin",
    "street_address",
]

# ── HCM ───────────────────────────────────────────────────────────────────────
HCM_LAND_NUMERIC = [
    "area_m2_raw", "area_m2_missing", "log_area_m2",
    "has_mat_tien", "has_goc_2_mat_tien", "has_so_hong", "has_gan_trung_tam",
    "has_hem_ngo", "has_kdc",
    "district_name_freq", "ward_name_eff_freq", "district_address_freq", "ward_address_freq",
    "is_core_district", "is_urban_district", "is_suburban_district",
    "area_x_district_name_freq", "area_x_ward_name_eff_freq",
    "log_area_x_district_name_freq", "log_area_x_ward_name_eff_freq",
    "has_mat_tien_x_log_area", "has_goc_2_mat_tien_x_log_area",
    "has_so_hong_x_log_area", "has_gan_trung_tam_x_log_area",
    "has_mat_tien_x_core", "has_goc_2_mat_tien_x_core",
    "has_so_hong_x_core", "has_gan_trung_tam_x_core",
    "hem_x_log_area", "hem_x_core",
    "street_name_freq", "street_address_freq",
    "area_x_street_name_freq", "area_x_street_address_freq",
    "log_area_x_street_name_freq", "log_area_x_street_address_freq",
]
HCM_LAND_CATEGORICAL = [
    "property_type_name", "district_address", "ward_address",
    "district_group", "area_bin", "district_area_bin",
    "province_name_norm", "street_address",
]
HCM_NONLAND_NUMERIC = [
    "area_m2_raw", "bedroom_count", "bathroom_count",
    "area_m2_missing", "bedroom_count_missing", "bathroom_count_missing",
    "log_area_m2", "bedroom_per_m2", "bathroom_per_m2", "bathroom_per_bedroom",
    "name_len", "description_len", "description_word_count",
    "has_mat_tien", "has_goc_2_mat_tien", "has_so_hong", "has_gan_trung_tam",
    "has_hem_xe_hoi", "has_full_noi_that", "has_hem_ngo", "has_kdc", "has_penthouse_duplex",
    "district_name_freq", "ward_name_eff_freq", "district_address_freq", "ward_address_freq",
    "is_core_district", "is_urban_district", "is_suburban_district",
    "room_total", "bedroom_x_log_area", "bathroom_x_log_area",
    "is_studio_like", "is_large_unit",
    "area_x_district_name_freq", "area_x_ward_name_eff_freq",
    "log_area_x_district_name_freq", "log_area_x_ward_name_eff_freq",
    "full_noi_that_x_bedroom", "full_noi_that_x_log_area",
    "hem_xe_hoi_x_log_area", "mat_tien_x_core", "full_noi_that_x_core",
    "hem_x_log_area", "kdc_x_log_area", "penthouse_x_log_area",
    "street_name_freq", "street_address_freq",
    "area_x_street_name_freq", "area_x_street_address_freq",
    "log_area_x_street_name_freq", "log_area_x_street_address_freq",
]
HCM_NONLAND_CATEGORICAL = [
    "property_type_name", "district_address", "ward_address",
    "district_group", "area_bin", "district_area_bin",
    "province_name_norm", "street_address",
]

# ── Đà Nẵng ───────────────────────────────────────────────────────────────────
# Base numeric: raw struct + freq + desc features
# Categorical: raw admin columns + project/direction
DN_LAND_BASE_NUMERIC = [
    "area", "frontage_width", "house_depth", "road_width",
    "published_year", "published_month",
    # freq features (count, không phải ratio)
    "district_name_freq", "ward_name_freq", "street_name_freq", "project_name_freq",
    # description numeric
    "desc_floor_count_text", "desc_bedroom_count_text", "desc_bathroom_count_text",
    "desc_road_width_text_m", "desc_frontage_width_text_m",
    "desc_distance_beach_m", "desc_distance_center_m", "desc_signal_count",
    # description flags
    "desc_has_legal_docs", "desc_has_car_access", "desc_has_frontage",
    "desc_has_alley", "desc_has_corner", "desc_has_business", "desc_has_elevator",
    "desc_has_sea_river_lake_view", "desc_has_near_beach", "desc_has_near_amenities",
    "desc_has_urgent_sale", "desc_has_new_house",
]
DN_LAND_CATEGORICAL = [
    "district_name", "ward_name", "street_name", "project_name", "house_direction",
]

DN_NONLAND_BASE_NUMERIC = [
    "area", "floor_count", "frontage_width", "house_depth", "road_width",
    "bedroom_count", "bathroom_count", "published_year", "published_month",
    # freq
    "district_name_freq", "ward_name_freq", "street_name_freq", "project_name_freq",
    # description numeric
    "desc_floor_count_text", "desc_bedroom_count_text", "desc_bathroom_count_text",
    "desc_road_width_text_m", "desc_frontage_width_text_m",
    "desc_distance_beach_m", "desc_distance_center_m", "desc_signal_count",
    # description flags
    "desc_has_legal_docs", "desc_has_car_access", "desc_has_frontage",
    "desc_has_alley", "desc_has_corner", "desc_has_business", "desc_has_elevator",
    "desc_has_sea_river_lake_view", "desc_has_near_beach", "desc_has_near_amenities",
    "desc_has_urgent_sale", "desc_has_new_house",
]
DN_NONLAND_CATEGORICAL = [
    "property_type_name", "district_name", "ward_name", "street_name",
    "project_name", "house_direction", "balcony_direction",
]

# ── HUẾ ──────────────────────────────────────────────────────────────────────
HUE_LAND_NUMERIC = [
    "area_m2_raw",
    "area_m2_missing",
    "log_area_m2",

    "is_hue_core",
    "is_hue_urban",
    "is_hue_suburban",

    "district_name_freq",
    "ward_name_freq",
    "district_address_freq",
    "ward_address_freq",

    "area_x_district_freq",
    "area_x_ward_freq",
    "log_area_x_district_freq",
    "log_area_x_ward_freq",

    "has_mat_tien",
    "has_goc_2_mat_tien",
    "has_so_hong",
    "has_gan_trung_tam",
    "land_kw_duong_rong",
    "land_kw_ngo_oto",
    "land_kw_quy_hoach_risk",
    "land_kw_khong_quy_hoach",
    "land_kw_phan_lo",
    "land_kw_gan_song_huong",

    "mat_tien_x_log_area",
    "goc_2_mat_tien_x_log_area",
    "so_hong_x_log_area",
    "gan_trung_tam_x_log_area",

    "land_accessibility_score",
    "land_legal_score",
    "land_accessibility_x_log_area",
    "land_legal_x_log_area",

    "is_large_land",
    "large_land_x_suburban",

    "name_len",
    "description_len",
    "description_word_count",
    "street_missing"
]

HUE_LAND_CATEGORICAL = [
    "property_type_name",
    "district_address",
    "ward_address",
    "district_group",
    "area_bin",
    "district_area_bin"
]

HUE_NONLAND_NUMERIC = [
    "area_m2_raw",
    "bedroom_count",
    "bathroom_count",

    "area_m2_missing",
    "bedroom_count_missing",
    "bathroom_count_missing",

    "log_area_m2",
    "bedroom_per_m2",
    "bathroom_per_m2",
    "bathroom_per_bedroom",

    "is_hue_core",
    "is_hue_urban",
    "is_hue_suburban",

    "district_name_freq",
    "ward_name_freq",
    "district_address_freq",
    "ward_address_freq",

    "area_x_district_freq",
    "area_x_ward_freq",
    "log_area_x_district_freq",
    "log_area_x_ward_freq",

    "room_total",
    "bedroom_x_log_area",
    "bathroom_x_log_area",
    "is_studio_like",
    "is_large_unit",

    "has_mat_tien",
    "has_goc_2_mat_tien",
    "has_so_hong",
    "has_gan_trung_tam",
    "has_hem_xe_hoi",
    "has_full_noi_that",
    "nonland_kw_thang_may",
    "nonland_kw_nha_moi",
    "nonland_kw_view_dep",
    "nonland_kw_gan_tien_ich",
    "nonland_kw_kinh_doanh_cho_thue",

    "nonland_business_score",
    "nonland_luxury_score",
    "nonland_business_x_log_area",
    "nonland_luxury_x_log_area",
    "thang_may_x_area",

    "name_len","description_len", "description_word_count", "street_missing",
]
HUE_NONLAND_CATEGORICAL = [
    "property_type_name",
    "district_address",
    "ward_address",
    "district_group",
    "area_bin",
    "district_area_bin"
]
# ── CanTho base feature lists ─────────────────────────────────────────────────
# Copy NGUYÊN XI từ CanTho.ipynb BASE_OHE_COLS, BASE_FREQ_COLS, BASE_NUMERIC_COLS
CT_OHE_COLS     = ["property_type_name", "province_name", "district_name",
                   "ward_name", "house_direction", "balcony_direction"]
CT_FREQ_COLS    = ["street_name", "project_name"]
CT_NUMERIC_COLS = ["area", "log_area", "frontage_width", "bedroom_count", "bathroom_count"]


# ═══════════════════════════════════════════════════════════════════════════════
# PUBLIC ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def build_features(inp: PredictInput) -> pd.DataFrame:
    """
    Build DataFrame 1 row với đúng feature vector mà model .pkl expect.
    Dispatch theo city → HN / HCM / Đà Nẵng / generic.
    """
    try:
        if inp.city in {"danang", "haiphong"}:
            # Danang + Haiphong: cùng format notebook (raw struct + freq + desc features)
            # target: log1p(price_per_m2) → predictor nhân × area
            return _build_danang(inp)
        elif inp.city == "cantho":
            return _build_cantho(inp)
        elif inp.city == "hanoi":
            return _build_hanoi(inp)
        elif inp.city == "hue":
            return _build_hue(inp)
        else:
            # hcm, hue, dongnai — dùng HCM group logic
            return _build_hcm_group(inp)
    except Exception as exc:
        raise FeatureBuildError(f"Không thể build feature vector: {exc}") from exc


# ═══════════════════════════════════════════════════════════════════════════════
# HÀ NỘI
# ═══════════════════════════════════════════════════════════════════════════════

def _build_hanoi(inp: PredictInput) -> pd.DataFrame:
    row: dict[str, Any] = {}
    area      = float(inp.area)
    bedrooms  = float(inp.bedrooms  or 0)
    bathrooms = float(inp.bathrooms or 0)
    log_area  = float(np.log1p(area))
    use_street = bool(inp.street)

    text = (_norm_lower(inp.description) + " " + _norm_lower(inp.property_type))
    district_norm = _norm_lower(inp.district)
    ward_norm     = _norm_lower(inp.ward)
    street_norm   = _norm_lower(inp.street) if inp.street else ""
    province_norm = CITY_PROVINCE_NORM["hanoi"]

    # ── Common keywords ────────────────────────────────────────────────────────
    for feat, kws in {**COMMON_KW, "has_gan_trung_tam": HN_TRUNG_TAM_KW}.items():
        row[feat] = int(bool(re.search("|".join(re.escape(k) for k in kws), text)))
    for feat, kws in HN_LAND_KW.items():
        row[feat] = int(bool(re.search("|".join(re.escape(k) for k in kws), text)))
    for feat, kws in HN_NONLAND_KW.items():
        row[feat] = int(bool(re.search("|".join(re.escape(k) for k in kws), text)))

    # ── Numerics ────────────────────────────────────────────────────────────────
    row.update({
        "area_m2_raw": area, "area_m2_missing": int(area <= 0), "log_area_m2": log_area,
        "bedroom_count": bedrooms, "bathroom_count": bathrooms,
        "bedroom_count_missing": int(inp.bedrooms is None),
        "bathroom_count_missing": int(inp.bathrooms is None),
        "bedroom_per_m2": bedrooms / (area + 1),
        "bathroom_per_m2": bathrooms / (area + 1),
        "bathroom_per_bedroom": bathrooms / (bedrooms + 1),
        "name_len": len(inp.property_type),
        "description_len": len(inp.description),
        "description_word_count": len(inp.description.split()),
        "room_total": bedrooms + bathrooms,
        "bedroom_x_log_area": bedrooms * log_area,
        "bathroom_x_log_area": bathrooms * log_area,
        "is_studio_like": int(bedrooms <= 1 and area <= 45),
        "is_large_unit": int(area >= 100 or bedrooms >= 4),
        "is_family_unit": int(bedrooms >= 3),
        "room_density_score": (bedrooms + bathrooms) / (area + 1),
        "is_tiny_land": int(area < 30), "is_small_land": int(30 <= area < 50),
        "is_medium_land": int(50 <= area < 100), "is_large_land": int(area >= 100),
    })

    # ── District group ──────────────────────────────────────────────────────────
    is_core     = int(district_norm in HANOI_CORE_DISTRICTS)
    is_urban    = int(district_norm in HANOI_URBAN_DISTRICTS)
    is_suburban = int(is_core == 0 and is_urban == 0)
    row.update({"is_core_district": is_core, "is_urban_district": is_urban,
                "is_suburban_district": is_suburban})
    district_group = "core" if is_core else ("urban" if is_urban else "suburban")
    row["district_group"] = district_group

    # ── Size × district ─────────────────────────────────────────────────────────
    row["tiny_land_x_core"]      = row["is_tiny_land"]  * is_core
    row["large_land_x_suburban"] = row["is_large_land"] * is_suburban
    row["large_land_x_urban"]    = row["is_large_land"] * is_urban

    # ── Address keys ────────────────────────────────────────────────────────────
    row["district_address"]  = f"{district_norm}__{province_norm}"
    row["ward_address"]      = f"{ward_norm}__{district_norm}__{province_norm}"
    row["street_address"]    = (f"{street_norm}__{ward_norm}__{district_norm}__{province_norm}"
                                if use_street else "unknown")
    row["property_type_name"] = _norm_lower(inp.property_type)

    # ── Frequency lookup ────────────────────────────────────────────────────────
    freq_maps = _get_freq_maps(inp.model_key)
    _set_freq(row, "district_name_freq",    district_norm,          freq_maps, "district_name")
    _set_freq(row, "ward_name_freq",        ward_norm,              freq_maps, "ward_name")
    _set_freq(row, "district_address_freq", row["district_address"],freq_maps, "district_address")
    _set_freq(row, "ward_address_freq",     row["ward_address"],    freq_maps, "ward_address")
    _set_freq(row, "street_name_freq",    street_norm if use_street else "", freq_maps, "street_name")
    _set_freq(row, "street_address_freq", row["street_address"]    if use_street else "", freq_maps, "street_address")

    # ── Area bin ────────────────────────────────────────────────────────────────
    area_bins = _get_area_bins(inp.model_key)
    area_bin  = _apply_area_bin(area, area_bins)
    row["area_bin"] = area_bin
    row["district_area_bin"] = f"{district_group}__{area_bin}"

    # ── Relationship features ────────────────────────────────────────────────────
    for fc in ["district_name_freq", "ward_name_freq", "district_address_freq", "ward_address_freq"]:
        v = row.get(fc, 0.0)
        row[f"area_x_{fc}"]     = area * v
        row[f"log_area_x_{fc}"] = log_area * v
    # Luôn tính street interaction (= 0 khi không có street, freq đã = 0.0)
    for fc in ["street_name_freq", "street_address_freq"]:
        v = row.get(fc, 0.0)
        row[f"area_x_{fc}"]     = area * v
        row[f"log_area_x_{fc}"] = log_area * v

    # Land scores
    row["land_frontage_score"]         = row.get("has_mat_tien",0) + row.get("has_goc_2_mat_tien",0) + row.get("land_kw_mat_tien_rong",0)
    row["land_accessibility_score"]    = row.get("land_kw_duong_rong",0) + row.get("land_kw_oto_tranh",0) + row.get("land_kw_ngo_oto",0)
    row["land_premium_location_score"] = row["land_frontage_score"] + row["land_accessibility_score"] + row.get("has_gan_trung_tam",0) + row.get("land_kw_gan_ho",0)
    row["land_legal_positive_score"]   = row.get("has_so_hong",0) + row.get("land_kw_khong_quy_hoach",0)
    row["land_planning_risk_score"]    = row.get("land_kw_quy_hoach_risk",0)
    row["land_shape_quality_score"]    = row.get("land_kw_no_hau",0) + row.get("land_kw_vuong_van",0)

    for score in ["land_frontage_score","land_accessibility_score","land_premium_location_score",
                  "land_legal_positive_score","land_planning_risk_score","land_shape_quality_score"]:
        row[f"{score.replace('_score','')}_x_log_area"] = row[score] * log_area
    row["land_premium_x_core"]       = row["land_premium_location_score"] * is_core
    row["land_accessibility_x_urban"]= row["land_accessibility_score"]    * is_urban

    # Non-land composite scores
    row["nonland_luxury_score"]           = row.get("has_full_noi_that",0) + row.get("nonland_kw_chung_cu_cao_cap",0) + row.get("nonland_kw_view_dep",0) + row.get("nonland_kw_can_goc",0)
    row["nonland_convenience_score"]      = row.get("nonland_kw_gan_metro",0) + row.get("nonland_kw_gan_tien_ich",0) + row.get("has_gan_trung_tam",0)
    row["nonland_building_quality_score"] = row.get("nonland_kw_thang_may",0) + row.get("nonland_kw_nha_moi",0) + row.get("nonland_kw_san_thuong",0)
    row["nonland_business_score"]         = row.get("has_mat_tien",0) + row.get("has_hem_xe_hoi",0) + row.get("nonland_kw_kinh_doanh_cho_thue",0)

    for score in ["nonland_luxury","nonland_convenience","nonland_building_quality","nonland_business"]:
        row[f"{score}_x_log_area"] = row[f"{score}_score"] * log_area
    row["nonland_luxury_x_core"]   = row["nonland_luxury_score"]   * is_core
    row["nonland_business_x_core"] = row["nonland_business_score"] * is_core

    row["full_noi_that_x_bedroom"]  = row.get("has_full_noi_that",0) * bedrooms
    row["full_noi_that_x_bathroom"] = row.get("has_full_noi_that",0) * bathrooms
    row["thang_may_x_area"]         = row.get("nonland_kw_thang_may",0) * area
    row["nha_moi_x_log_area"]       = row.get("nonland_kw_nha_moi",0)   * log_area

    # ── Build DataFrame ─────────────────────────────────────────────────────────
    num_feats = HN_LAND_NUMERIC  if inp.model_type == "land" else HN_NONLAND_NUMERIC
    cat_feats = HN_LAND_CATEGORICAL if inp.model_type == "land" else HN_NONLAND_CATEGORICAL
    return _to_df(row, num_feats, cat_feats, use_street)


# ═══════════════════════════════════════════════════════════════════════════════
# HCM GROUP
# ═══════════════════════════════════════════════════════════════════════════════

def _build_hcm_group(inp: PredictInput) -> pd.DataFrame:
    row: dict[str, Any] = {}
    area      = float(inp.area)
    bedrooms  = float(inp.bedrooms  or 0)
    bathrooms = float(inp.bathrooms or 0)
    log_area  = float(np.log1p(area))
    use_street = inp.city in STREET_CITIES and bool(inp.street)

    text = (_norm_lower(inp.description) + " " + _norm_lower(inp.property_type))
    district_norm = _norm_lower(inp.district)
    ward_norm     = _norm_lower(inp.ward)
    street_norm   = _norm_lower(inp.street) if inp.street else ""
    province_norm = CITY_PROVINCE_NORM.get(inp.city, inp.city)

    for feat, kws in {**COMMON_KW, "has_gan_trung_tam": HCM_TRUNG_TAM_KW}.items():
        row[feat] = int(bool(re.search("|".join(re.escape(k) for k in kws), text)))

    row.update({
        "area_m2_raw": area, "area_m2_missing": int(area <= 0), "log_area_m2": log_area,
        "bedroom_count": bedrooms, "bathroom_count": bathrooms,
        "bedroom_count_missing": int(inp.bedrooms is None),
        "bathroom_count_missing": int(inp.bathrooms is None),
        "bedroom_per_m2": bedrooms/(area+1), "bathroom_per_m2": bathrooms/(area+1),
        "bathroom_per_bedroom": bathrooms/(bedrooms+1),
        "name_len": len(inp.property_type), "description_len": len(inp.description),
        "description_word_count": len(inp.description.split()),
        "room_total": bedrooms+bathrooms,
        "bedroom_x_log_area": bedrooms*log_area, "bathroom_x_log_area": bathrooms*log_area,
        "is_studio_like": int(bedrooms<=1 and area<=45), "is_large_unit": int(area>=100 or bedrooms>=4),
    })

    is_core     = int(district_norm in HCM_CORE_DISTRICTS)
    is_urban    = int(district_norm in HCM_URBAN_DISTRICTS)
    is_suburban = int(is_core==0 and is_urban==0)
    row.update({"is_core_district": is_core, "is_urban_district": is_urban,
                "is_suburban_district": is_suburban})
    district_group = "core" if is_core else ("urban" if is_urban else "suburban")
    row["district_group"] = district_group

    row["district_address"]   = f"{district_norm}__{province_norm}"
    row["ward_address"]       = f"{ward_norm}__{district_norm}__{province_norm}"
    row["street_address"]     = (f"{street_norm}__{ward_norm}__{district_norm}__{province_norm}"
                                 if use_street else "unknown")
    row["province_name_norm"] = province_norm
    row["property_type_name"] = _norm_lower(inp.property_type)

    freq_maps = _get_freq_maps(inp.model_key)
    _set_freq(row, "district_name_freq",    district_norm,          freq_maps, "district_name")
    _set_freq(row, "ward_name_eff_freq",    ward_norm,              freq_maps, "ward_name_eff")
    _set_freq(row, "district_address_freq", row["district_address"],freq_maps, "district_address")
    _set_freq(row, "ward_address_freq",     row["ward_address"],    freq_maps, "ward_address")
    _set_freq(row, "street_name_freq",    street_norm if use_street else "", freq_maps, "street_name")
    _set_freq(row, "street_address_freq", row["street_address"] if use_street else "", freq_maps, "street_address")

    area_bins = _get_area_bins(inp.model_key)
    area_bin  = _apply_area_bin(area, area_bins)
    row["area_bin"] = area_bin
    row["district_area_bin"] = f"{district_group}__{area_bin}"

    # HCM relationships
    for fc in ["district_name_freq","ward_name_eff_freq","district_address_freq","ward_address_freq"]:
        v = row.get(fc, 0.0)
        row[f"area_x_{fc}"] = area * v; row[f"log_area_x_{fc}"] = log_area * v
    # Luôn tính street interaction (= 0 khi không có street, freq đã = 0.0)
    for fc in ["street_name_freq","street_address_freq"]:
        v = row.get(fc, 0.0)
        row[f"area_x_{fc}"]     = area * v
        row[f"log_area_x_{fc}"] = log_area * v

    for kw in ["has_mat_tien","has_goc_2_mat_tien","has_so_hong","has_gan_trung_tam"]:
        v = row.get(kw, 0)
        row[f"{kw}_x_log_area"] = v * log_area
        row[f"{kw}_x_core"]     = v * is_core

    row["hem_x_log_area"]        = row.get("has_hem_ngo",0) * log_area
    row["hem_x_core"]            = row.get("has_hem_ngo",0) * is_core
    row["full_noi_that_x_bedroom"]  = row.get("has_full_noi_that",0) * bedrooms
    row["full_noi_that_x_log_area"] = row.get("has_full_noi_that",0) * log_area
    row["hem_xe_hoi_x_log_area"]    = row.get("has_hem_xe_hoi",0) * log_area
    row["mat_tien_x_core"]          = row.get("has_mat_tien",0) * is_core
    row["full_noi_that_x_core"]     = row.get("has_full_noi_that",0) * is_core
    row["kdc_x_log_area"]           = row.get("has_kdc",0) * log_area
    row["penthouse_x_log_area"]     = row.get("has_penthouse_duplex",0) * log_area

    num_feats = HCM_LAND_NUMERIC  if inp.model_type == "land" else HCM_NONLAND_NUMERIC
    cat_feats = HCM_LAND_CATEGORICAL if inp.model_type == "land" else HCM_NONLAND_CATEGORICAL
    return _to_df(row, num_feats, cat_feats, use_street)


# ═══════════════════════════════════════════════════════════════════════════════
# ĐÀ NẴNG
# ═══════════════════════════════════════════════════════════════════════════════

def _build_danang(inp: PredictInput) -> pd.DataFrame:
    """
    Đà Nẵng: dùng feature list LẤY TRỰC TIẾP từ bundle artifact.
    Target: log1p(price_per_m2) → predictor nhân × area để ra price.

    Bundle lưu:
      numeric_features   : list[str]  — numeric cols (base + freq + desc selected)
      categorical_features: list[str] — categorical cols
      feature_cols       : list[str]  = numeric + categorical (thứ tự đúng)

    Pipeline nhận DataFrame với đúng các cột này, không thêm không bớt.
    """
    # ── Lấy feature list từ bundle ────────────────────────────────────────────
    num_feats = registry.get_artifact(inp.model_key, "numeric_features")
    cat_feats = registry.get_artifact(inp.model_key, "categorical_features")

    if not num_feats or not cat_feats:
        logger.warning(
            f"[FeatureBuilder] Danang bundle missing feature lists for {inp.model_key}. "
            "Using hardcoded fallback — predictions may be inaccurate."
        )
        num_feats = DN_LAND_BASE_NUMERIC  if inp.model_type == "land" else DN_NONLAND_BASE_NUMERIC
        cat_feats = DN_LAND_CATEGORICAL   if inp.model_type == "land" else DN_NONLAND_CATEGORICAL

    # ── Build raw values ──────────────────────────────────────────────────────
    area      = float(inp.area)
    bedrooms  = float(inp.bedrooms  or 0)
    bathrooms = float(inp.bathrooms or 0)

    text_norm     = _normalize_description_text((inp.description or "") + " " + (inp.property_type or ""))
    district_norm = _norm_lower(inp.district)
    ward_norm     = _norm_lower(inp.ward)
    street_norm   = _norm_lower(inp.street) if inp.street else ""

    row: dict[str, Any] = {}

    # ── Struct numeric ────────────────────────────────────────────────────────
    row["area"]           = area
    row["bedroom_count"]  = bedrooms
    row["bathroom_count"] = bathrooms
    row["floor_count"]    = np.nan
    row["frontage_width"] = _extract_number(text_norm, [r"ngang[^0-9]{0,10}([\d.,]+)\s*m"], 1, 50)
    row["house_depth"]    = np.nan
    row["road_width"]     = _extract_number(text_norm, [r"(?:duong|mat duong|lo gioi|hem|kiet)[^0-9]{0,15}([\d.,]+)\s*m"], 0.5, 100)

    import datetime
    now = datetime.datetime.now()
    row["published_year"]  = now.year
    row["published_month"] = now.month

    # ── Frequency features (value_counts count, not ratio) ────────────────────
    # Đà Nẵng dùng train_key.value_counts() (absolute count, không normalize)
    # → unseen category = 0
    freq_maps = _get_freq_maps(inp.model_key)
    row["district_name_freq"] = float(freq_maps.get("district_name", {}).get(district_norm, 0))
    row["ward_name_freq"]     = float(freq_maps.get("ward_name",     {}).get(ward_norm,     0))
    row["street_name_freq"]   = float(freq_maps.get("street_name",   {}).get(street_norm,   0))
    row["project_name_freq"]  = 0.0   # không có từ user input

    # ── Description pattern flags ─────────────────────────────────────────────
    for col, pattern in DN_PATTERN_FEATURES.items():
        row[col] = int(bool(re.search(pattern, text_norm)))

    # ── Description numeric ───────────────────────────────────────────────────
    row["desc_floor_count_text"]      = _extract_number(text_norm, [r"([\d]+)\s*(?:tang|lau)"], 1, 100)
    row["desc_bedroom_count_text"]    = _extract_number(text_norm, [r"([\d]+)\s*(?:pn|phong ngu|ngu)"], 1, 50)
    row["desc_bathroom_count_text"]   = _extract_number(text_norm, [r"([\d]+)\s*(?:wc|toilet|phong tam|ve sinh)"], 1, 50)
    row["desc_road_width_text_m"]     = row["road_width"]
    row["desc_frontage_width_text_m"] = row["frontage_width"]
    row["desc_distance_beach_m"]      = _extract_distance_m(text_norm, r"bien")
    row["desc_distance_center_m"]     = _extract_distance_m(text_norm, r"trung tam")
    row["desc_signal_count"]          = float(sum(row.get(c, 0) for c in DN_PATTERN_FEATURES.keys()))

    # ── Categorical admin ─────────────────────────────────────────────────────
    row["district_name"]     = district_norm
    row["ward_name"]         = ward_norm
    row["street_name"]       = street_norm if street_norm else "__missing__"
    row["project_name"]      = "__missing__"
    row["house_direction"]   = "__missing__"
    row["balcony_direction"] = "__missing__"
    row["property_type_name"]= _norm_lower(inp.property_type)

    # ── Build DataFrame với đúng feature list từ bundle ───────────────────────
    all_feats = list(num_feats) + list(cat_feats)
    df = pd.DataFrame([row])
    for col in all_feats:
        if col not in df.columns:
            # Numeric default = NaN (imputer sẽ xử lý), categorical = "__missing__"
            df[col] = np.nan if col in num_feats else "__missing__"
    return df[all_feats]


def _build_cantho(inp: PredictInput) -> pd.DataFrame:
    """
    Cần Thơ: pipeline nhận DataFrame với đúng feature_cols từ bundle.
    Bundle có:
      ohe_cols     : ["property_type_name","province_name","district_name","ward_name",
                       "house_direction","balcony_direction"]
      freq_cols    : ["street_name","project_name"]
      numeric_cols : ["area","log_area","frontage_width","bedroom_count","bathroom_count"]
      feature_cols : ohe_cols + freq_cols + numeric_cols

    Target: log1p(price) → expm1() ra thẳng VNĐ (không nhân area).
    """
    # ── Lấy feature list từ bundle ────────────────────────────────────────────
    # Lấy từ bundle — nếu None thì trigger load lại để cache artifacts
    ohe_cols     = registry.get_artifact(inp.model_key, "ohe_cols")
    freq_cols    = registry.get_artifact(inp.model_key, "freq_cols")
    numeric_cols = registry.get_artifact(inp.model_key, "numeric_cols")
    feature_cols = registry.get_artifact(inp.model_key, "feature_cols")

    if not ohe_cols or not freq_cols or not numeric_cols:
        _ = registry.get(inp.model_key)
        ohe_cols     = registry.get_artifact(inp.model_key, "ohe_cols")
        freq_cols    = registry.get_artifact(inp.model_key, "freq_cols")
        numeric_cols = registry.get_artifact(inp.model_key, "numeric_cols")
        feature_cols = registry.get_artifact(inp.model_key, "feature_cols")

    ohe_cols     = list(ohe_cols     or CT_OHE_COLS)
    freq_cols    = list(freq_cols    or CT_FREQ_COLS)
    numeric_cols = list(numeric_cols or CT_NUMERIC_COLS)
    feature_cols = list(feature_cols or (ohe_cols + freq_cols + numeric_cols))

    logger.info(
        f"[FeatureBuilder] CanTho {inp.model_type}: "
        f"ohe={len(ohe_cols)} freq={len(freq_cols)} num={len(numeric_cols)} "
        f"total={len(feature_cols)}"
    )

    # ── Build raw values ──────────────────────────────────────────────────────
    area      = float(inp.area)
    bedrooms  = float(inp.bedrooms  or 0)
    bathrooms = float(inp.bathrooms or 0)

    text_norm     = _normalize_description_text((inp.description or "") + " " + (inp.property_type or ""))
    district_norm = _norm_lower(inp.district)
    ward_norm     = _norm_lower(inp.ward)
    # QUAN TRỌNG: dùng "__MISSING__" (uppercase) để khớp với
    # SimpleImputer(fill_value="__MISSING__") và FrequencyEncoder lúc train
    street_norm   = _norm_lower(inp.street) if inp.street else "__MISSING__"

    row: dict[str, Any] = {}

    # ── Numeric ───────────────────────────────────────────────────────────────
    row["area"]           = area
    row["log_area"]       = float(np.log1p(area))
    row["frontage_width"] = _extract_number(text_norm, [r"ngang[^0-9]{0,10}([\d.,]+)\s*m"], 1, 50)
    row["bedroom_count"]  = bedrooms
    row["bathroom_count"] = bathrooms

    # ── OHE categorical ───────────────────────────────────────────────────────
    row["property_type_name"] = _norm_lower(inp.property_type) or "__MISSING__"
    row["province_name"]      = CITY_PROVINCE_NORM.get(inp.city, inp.city)
    row["district_name"]      = district_norm or "__MISSING__"
    row["ward_name"]          = ward_norm     or "__MISSING__"
    row["house_direction"]    = "__MISSING__"
    row["balcony_direction"]  = "__MISSING__"

    # ── Freq categorical ──────────────────────────────────────────────────────
    # FrequencyEncoder bên trong pipeline tự lookup freq_map
    # Unseen value (kể cả "__MISSING__") → freq = 0 → không gây lỗi
    row["street_name"]  = street_norm
    row["project_name"] = "__MISSING__"

    # ── Build DataFrame ───────────────────────────────────────────────────────
    df = pd.DataFrame([row])

    for col in feature_cols:
        if col not in df.columns:
            df[col] = np.nan if col in numeric_cols else "__MISSING__"
            logger.warning(f"[FeatureBuilder] CanTho missing col '{col}', using default")

    df = df[feature_cols].copy()

    # QUAN TRỌNG: đúng dtype cho từng nhóm cột
    # ColumnTransformer route theo tên cột — sai dtype → SimpleImputer/OHE xử lý sai → treo
    for col in list(numeric_cols):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in list(ohe_cols) + list(freq_cols):
        if col in df.columns:
            df[col] = df[col].astype(str).replace("nan", "__MISSING__").fillna("__MISSING__")

    return df

def _build_hue(inp: PredictInput) -> pd.DataFrame:
    row: dict[str, Any] = {}

    area      = float(inp.area)
    bedrooms  = float(inp.bedrooms or 0)
    bathrooms = float(inp.bathrooms or 0)
    log_area  = float(np.log1p(area))

    text = (_norm_lower(inp.description) + " " + _norm_lower(inp.property_type))

    district_norm = _norm_lower(inp.district)
    ward_norm     = _norm_lower(inp.ward)
    province_norm = CITY_PROVINCE_NORM["hue"]

    # keyword flags
    for feat, kws in {**COMMON_KW, "has_gan_trung_tam": HUE_TRUNG_TAM_KW}.items():
        row[feat] = int(bool(re.search("|".join(re.escape(k) for k in kws), text)))

    for feat, kws in HUE_LAND_KW.items():
        row[feat] = int(bool(re.search("|".join(re.escape(k) for k in kws), text)))

    for feat, kws in HUE_NONLAND_KW.items():
        row[feat] = int(bool(re.search("|".join(re.escape(k) for k in kws), text)))

    # numeric base
    row.update({
        "area_m2_raw": area,
        "area_m2_missing": int(area <= 0),
        "log_area_m2": log_area,

        "bedroom_count": bedrooms,
        "bathroom_count": bathrooms,

        "bedroom_count_missing": int(inp.bedrooms is None),
        "bathroom_count_missing": int(inp.bathrooms is None),

        "bedroom_per_m2": bedrooms / (area + 1),
        "bathroom_per_m2": bathrooms / (area + 1),
        "bathroom_per_bedroom": bathrooms / (bedrooms + 1),

        "room_total": bedrooms + bathrooms,

        "bedroom_x_log_area": bedrooms * log_area,
        "bathroom_x_log_area": bathrooms * log_area,

        "is_studio_like": int(bedrooms <= 1 and area <= 45),
        "is_large_unit": int(area >= 100 or bedrooms >= 4),

        "is_large_land": int(area >= 120),

        "name_len": len(inp.property_type or ""),
        "description_len": len(inp.description or ""),
        "description_word_count": len((inp.description or "").split()),

        "street_missing": int(not bool(inp.street)),
    })

    # district grouping
    core_districts = {"thuận hóa", "phú xuân"}
    urban_districts = {"hương thủy", "hương trà"}

    is_core = int(district_norm in core_districts)
    is_urban = int(district_norm in urban_districts)
    is_suburban = int(is_core == 0 and is_urban == 0)

    row["is_hue_core"] = is_core
    row["is_hue_urban"] = is_urban
    row["is_hue_suburban"] = is_suburban

    district_group = "core" if is_core else ("urban" if is_urban else "suburban")
    row["district_group"] = district_group

    # address keys
    row["district_address"] = f"{district_norm}__{province_norm}"
    row["ward_address"] = f"{ward_norm}__{district_norm}__{province_norm}"

    row["property_type_name"] = _norm_lower(inp.property_type)
    # frequency maps
    freq_maps = _get_freq_maps(inp.model_key)

    _set_freq(row, "district_name_freq", district_norm, freq_maps, "district_name")
    _set_freq(row, "ward_name_freq", ward_norm, freq_maps, "ward_name")
    _set_freq(row, "district_address_freq", row["district_address"], freq_maps, "district_address")
    _set_freq(row, "ward_address_freq", row["ward_address"], freq_maps, "ward_address")

    row["area_x_district_freq"] = area * row["district_name_freq"]
    row["area_x_ward_freq"] = area * row["ward_name_freq"]

    row["log_area_x_district_freq"] = log_area * row["district_name_freq"]
    row["log_area_x_ward_freq"] = log_area * row["ward_name_freq"]
     # interaction
    row["mat_tien_x_log_area"] = row.get("has_mat_tien", 0) * log_area
    row["goc_2_mat_tien_x_log_area"] = row.get("has_goc_2_mat_tien", 0) * log_area
    row["so_hong_x_log_area"] = row.get("has_so_hong", 0) * log_area
    row["gan_trung_tam_x_log_area"] = row.get("has_gan_trung_tam", 0) * log_area

    row["land_accessibility_score"] = (
        row.get("land_kw_duong_rong", 0)
        + row.get("land_kw_ngo_oto", 0)
    )

    row["land_legal_score"] = (
        row.get("has_so_hong", 0)
        + row.get("land_kw_khong_quy_hoach", 0)
        - row.get("land_kw_quy_hoach_risk", 0)
    )

    row["land_accessibility_x_log_area"] = row["land_accessibility_score"] * log_area
    row["land_legal_x_log_area"] = row["land_legal_score"] * log_area

    row["large_land_x_suburban"] = row["is_large_land"] * is_suburban

    row["nonland_business_score"] = (
        row.get("has_mat_tien", 0)
        + row.get("has_hem_xe_hoi", 0)
        + row.get("nonland_kw_kinh_doanh_cho_thue", 0)
    )

    row["nonland_luxury_score"] = (
        row.get("has_full_noi_that", 0)
        + row.get("nonland_kw_thang_may", 0)
        + row.get("nonland_kw_view_dep", 0)
    )

    row["nonland_business_x_log_area"] = row["nonland_business_score"] * log_area
    row["nonland_luxury_x_log_area"] = row["nonland_luxury_score"] * log_area

    row["thang_may_x_area"] = row.get("nonland_kw_thang_may", 0) * area

    # area bin
    area_bins = _get_area_bins(inp.model_key)
    area_bin = _apply_area_bin(area, area_bins)

    row["area_bin"] = area_bin
    row["district_area_bin"] = f"{district_group}__{area_bin}"

    num_feats = HUE_LAND_NUMERIC if inp.model_type == "land" else HUE_NONLAND_NUMERIC
    cat_feats = HUE_LAND_CATEGORICAL if inp.model_type == "land" else HUE_NONLAND_CATEGORICAL

    return _to_df(row, num_feats, cat_feats, use_street=False)
# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _to_df(row: dict, num_feats: list[str], cat_feats: list[str],
           use_street: bool) -> pd.DataFrame:
    """
    Build DataFrame, điền default cho cột thiếu.

    Khi use_street=False: KHÔNG bỏ street columns — giữ lại với giá trị neutral
    (0.0 / "unknown") để feature count khớp với model.
    Model vẫn chạy được, chỉ không có signal từ street.
    """
    all_feats = num_feats + cat_feats
    STREET_NUM_COLS = {
        "street_name_freq", "street_address_freq",
        "area_x_street_name_freq", "area_x_street_address_freq",
        "log_area_x_street_name_freq", "log_area_x_street_address_freq",
    }
    STREET_CAT_COLS = {"street_address"}

    # Điền default vào row dict TRƯỚC khi tạo DataFrame
    # Tránh lỗi pandas khi gán cột mới vào DataFrame 1 row
    complete_row = dict(row)  # copy để không thay đổi row gốc
    for col in all_feats:
        if col not in complete_row:
            if col in STREET_NUM_COLS:
                complete_row[col] = 0.0
            elif col in STREET_CAT_COLS:
                complete_row[col] = "unknown"
            elif col in num_feats:
                complete_row[col] = 0
            else:
                complete_row[col] = "unknown"

    return pd.DataFrame([complete_row])[all_feats]


def _set_freq(row: dict, target: str, key: str,
              freq_maps: dict, map_key: str) -> None:
    fmap = freq_maps.get(map_key, {})
    row[target] = float(fmap.get(key, 0.0))


def _get_freq_maps(model_key: Any) -> dict[str, dict]:
    try:
        fm = registry.get_artifact(model_key, "freq_maps")
        if isinstance(fm, dict):
            return fm
    except Exception:
        pass
    return {}


def _get_area_bins(model_key: Any) -> np.ndarray:
    try:
        bins = registry.get_artifact(model_key, "area_bins")
        if bins is not None:
            return np.array(bins)
    except Exception:
        pass
    return np.array([0, 30, 50, 80, 120, 200, 500, 100_000])


def _apply_area_bin(area: float, bins: np.ndarray) -> str:
    try:
        idx = int(np.clip(np.searchsorted(bins, area, side="right") - 1, 0, len(bins)-2))
        return f"({bins[idx]:.1f}, {bins[idx+1]:.1f}]"
    except Exception:
        return "unknown"


def _extract_number(text: str, patterns: list[str],
                    min_val: float | None = None,
                    max_val: float | None = None) -> float:
    for pat in patterns:
        m = re.search(pat, text)
        if not m:
            continue
        try:
            v = float(m.group(1).replace(",", "."))
            if min_val is not None and v < min_val:
                continue
            if max_val is not None and v > max_val:
                continue
            return v
        except Exception:
            continue
    return np.nan


def _extract_distance_m(text: str, keyword: str) -> float:
    patterns = [
        rf"(?:cach|gan)\s+{keyword}[^0-9]{{0,30}}([\d.,]+)\s*(km|m)\b",
        rf"{keyword}[^0-9]{{0,30}}([\d.,]+)\s*(km|m)\b",
        rf"([\d.,]+)\s*(km|m)\s+(?:toi|den|ra|cach|gan)?\s*{keyword}",
    ]
    for pat in patterns:
        m = re.search(pat, text)
        if not m:
            continue
        try:
            v = float(m.group(1).replace(",", "."))
            unit = m.group(2)
            if unit == "km":
                v *= 1000
            if 1 <= v <= 100000:
                return v
        except Exception:
            continue
    return np.nan