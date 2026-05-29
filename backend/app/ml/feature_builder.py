"""
app/ml/feature_builder.py
──────────────────────────
Build feature DataFrame cho từng city/model_type.

TARGET theo city:
  hanoi, hcm          → log1p(price_vnd)      → expm1() ra VNĐ
  hue                 → log1p(price_vnd)      → expm1() ra VNĐ
  cantho              → log1p(price)          → expm1() ra VNĐ
  danang, haiphong    → log1p(price_per_m2)   → expm1() × area ra VNĐ
  dongnai             → log1p(price_per_m2)   → expm1() × area ra VNĐ

Bundle format theo city:
  hcm     → dict {model, freq_maps, area_bins, numeric_features, categorical_features, ...}
  hue     → dict {model, artifacts:{imputer,capper,preprocessor,numeric_features,
                                     categorical_features,feature_cols}, report}
  cantho  → dict {pipeline, feature_cols, ohe_cols, freq_cols, numeric_cols, ...}
  hanoi   → standalone sklearn Pipeline + riêng freq_maps.pkl + area_bins.pkl
  danang  → dict {model, numeric_features, categorical_features, feature_cols, ...}
             hoặc standalone pipeline + riêng freq_maps.pkl
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
# TEXT HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _norm(text: str | None) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", str(text).strip())

def _norm_lower(text: str | None) -> str:
    return _norm(text).lower()

def _remove_accents(text: str) -> str:
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return text.replace("đ", "d").replace("Đ", "D")

def _normalize_description_text(text: str | None) -> str:
    """Bỏ dấu + lowercase + giữ số và ký tự đặc biệt — dùng cho Đà Nẵng."""
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
HUE_CORE_DISTRICTS    = {"huế", "thành phố huế", "tp huế", "thuận hóa", "phú xuân"}
HUE_URBAN_DISTRICTS   = {"hương thủy", "hương trà"}

CITY_PROVINCE_NORM: dict[str, str] = {
    "hanoi": "hà nội", "hcm": "hồ chí minh",
    "danang": "đà nẵng", "hue": "thừa thiên huế",
    "dongnai": "đồng nai", "cantho": "cần thơ",
    "haiphong": "hải phòng",
}
STREET_CITIES = {"hanoi", "hcm"}


# ═══════════════════════════════════════════════════════════════════════════════
# KEYWORD RULES
# ═══════════════════════════════════════════════════════════════════════════════

COMMON_KW: dict[str, list[str]] = {
    "has_mat_tien":         ["mặt tiền", "mặt phố", "mặt đường", "mt phố", "mt đường", "kinh doanh"],
    "has_goc_2_mat_tien":   ["góc 2 mặt tiền", "2 mặt tiền", "hai mặt tiền", "lô góc"],
    "has_so_hong":          ["sổ hồng", "sổ đỏ", "so hong", "pháp lý rõ", "sổ riêng", "chính chủ"],
    "has_full_noi_that":    ["full nội thất", "đầy đủ nội thất", "nội thất cao cấp",
                             "full đồ", "tặng nội thất", "có nội thất"],
    "has_hem_xe_hoi":       ["hẻm xe hơi", "hẻm ô tô", "ô tô vào", "oto vào",
                             "ô tô tránh", "hẻm rộng", "ngõ ô tô", "kiệt ô tô"],
    "has_hem_ngo":          ["hẻm", "hem"],
    "has_kdc":              ["khu dân cư", "kdc", "khu đô thị"],
    "has_penthouse_duplex": ["penthouse", "duplex", "căn góc"],
}

HN_TRUNG_TAM_KW  = ["trung tâm", "gần trung tâm", "phố cổ", "hoàn kiếm", "ba đình"]
HCM_TRUNG_TAM_KW = ["trung tâm", "gần trung tâm", "quận 1", "quận 3", "bến thành"]
HUE_TRUNG_TAM_KW = ["trung tâm", "gần trung tâm", "tp huế", "thành phố huế",
                     "đại nội", "sông hương"]

HN_LAND_KW: dict[str, list[str]] = {
    "land_kw_duong_rong":      ["đường rộng", "đường lớn", "đường thông", "mặt đường lớn"],
    "land_kw_oto_tranh":       ["ô tô tránh", "oto tránh", "2 ô tô tránh", "xe tải vào"],
    "land_kw_ngo_oto":         ["ngõ ô tô", "ngõ oto", "ô tô vào", "ngõ rộng"],
    "land_kw_quy_hoach_risk":  ["dính quy hoạch", "vướng quy hoạch", "quy hoạch treo"],
    "land_kw_khong_quy_hoach": ["không quy hoạch", "ko quy hoạch", "quy hoạch ổn định"],
    "land_kw_no_hau":          ["nở hậu", "no hau"],
    "land_kw_vuong_van":       ["vuông vắn", "thửa đẹp", "lô đẹp"],
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
    "land_kw_duong_rong":      ["đường rộng", "đường lớn", "đường thông", "đường ô tô", "ô tô tránh"],
    "land_kw_ngo_oto":         ["ngõ ô tô", "ô tô vào", "oto vào", "hẻm xe hơi", "kiệt ô tô"],
    "land_kw_quy_hoach_risk":  ["dính quy hoạch", "vướng quy hoạch", "quy hoạch treo"],
    "land_kw_khong_quy_hoach": ["không quy hoạch", "ko quy hoạch", "quy hoạch ổn định"],
    "land_kw_phan_lo":         ["phân lô", "khu phân lô", "khu đô thị", "kđt", "đất đấu giá"],
    "land_kw_gan_song_huong":  ["sông hương", "gần sông hương", "view sông hương",
                                 "ven sông", "view sông"],
}
HUE_NONLAND_KW: dict[str, list[str]] = {
    "nonland_kw_thang_may":           ["thang máy", "thang may", "có thang máy"],
    "nonland_kw_nha_moi":             ["nhà mới", "mới xây", "xây mới", "ở ngay", "vào ở ngay"],
    "nonland_kw_view_dep":            ["view đẹp", "view sông", "view sông hương",
                                       "view thoáng", "ban công"],
    "nonland_kw_gan_tien_ich":        ["gần trường", "gần chợ", "gần bệnh viện",
                                       "gần siêu thị", "trung tâm thương mại", "tiện ích"],
    "nonland_kw_kinh_doanh_cho_thue": ["kinh doanh", "cho thuê", "dòng tiền",
                                       "văn phòng", "shop", "shophouse"],
}

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
# HUE FEATURE LISTS (copy từ notebook)
# ═══════════════════════════════════════════════════════════════════════════════

# Copy NGUYÊN XI từ notebook HUE__1_.ipynb
HUE_LAND_NUMERIC = [
    "area_m2_raw", "area_m2_missing", "log_area_m2",
    "is_hue_core", "is_hue_urban", "is_hue_suburban",
    "district_name_freq", "ward_name_freq", "district_address_freq", "ward_address_freq",
    "area_x_district_freq", "area_x_ward_freq",
    "log_area_x_district_freq", "log_area_x_ward_freq",
    "has_mat_tien", "has_goc_2_mat_tien", "has_so_hong", "has_gan_trung_tam",
    "land_kw_duong_rong", "land_kw_ngo_oto",
    "land_kw_quy_hoach_risk", "land_kw_khong_quy_hoach",
    "land_kw_phan_lo", "land_kw_gan_song_huong",
    "mat_tien_x_log_area", "goc_2_mat_tien_x_log_area",
    "so_hong_x_log_area", "gan_trung_tam_x_log_area",
    "land_accessibility_score", "land_legal_score",
    "land_accessibility_x_log_area", "land_legal_x_log_area",
    "is_large_land", "large_land_x_suburban",
    "name_len", "description_len", "description_word_count", "street_missing",
]
HUE_LAND_CATEGORICAL = [
    "property_type_name", "district_address", "ward_address",
    "district_group", "area_bin", "district_area_bin",
]

# Copy NGUYÊN XI từ HUE_NON_LAND_NUMERIC_FEATURES trong notebook
HUE_NONLAND_NUMERIC = [
    "area_m2_raw", "bedroom_count", "bathroom_count",
    "area_m2_missing", "bedroom_count_missing", "bathroom_count_missing",
    "log_area_m2", "bedroom_per_m2", "bathroom_per_m2", "bathroom_per_bedroom",
    "is_hue_core", "is_hue_urban", "is_hue_suburban",
    "district_name_freq", "ward_name_freq", "district_address_freq", "ward_address_freq",
    "area_x_district_freq", "area_x_ward_freq",
    "log_area_x_district_freq", "log_area_x_ward_freq",
    "room_total", "bedroom_x_log_area", "bathroom_x_log_area",
    "is_studio_like", "is_large_unit",
    "has_mat_tien", "has_goc_2_mat_tien", "has_so_hong", "has_gan_trung_tam",
    "has_hem_xe_hoi", "has_full_noi_that",
    "nonland_kw_thang_may", "nonland_kw_nha_moi", "nonland_kw_view_dep",
    "nonland_kw_gan_tien_ich", "nonland_kw_kinh_doanh_cho_thue",
    "nonland_business_score", "nonland_luxury_score",
    "nonland_business_x_log_area", "nonland_luxury_x_log_area",
    "thang_may_x_area",
    "name_len", "description_len", "description_word_count", "street_missing",
]
HUE_NONLAND_CATEGORICAL = [
    "property_type_name", "district_address", "ward_address",
    "district_group", "area_bin", "district_area_bin",
]

# ── HN feature lists ──────────────────────────────────────────────────────────
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
    "street_name_freq", "street_address_freq",
    "area_x_street_name_freq", "area_x_street_address_freq",
    "log_area_x_street_name_freq", "log_area_x_street_address_freq",
]
HN_LAND_CATEGORICAL = [
    "property_type_name", "district_address", "ward_address",
    "district_group", "area_bin", "district_area_bin", "street_address",
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
    "street_name_freq", "street_address_freq",
    "area_x_street_name_freq", "area_x_street_address_freq",
    "log_area_x_street_name_freq", "log_area_x_street_address_freq",
]
HN_NONLAND_CATEGORICAL = [
    "property_type_name", "district_address", "ward_address",
    "district_group", "area_bin", "district_area_bin", "street_address",
]

# ── HCM feature lists ─────────────────────────────────────────────────────────
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

# ── Danang feature lists ──────────────────────────────────────────────────────
DN_LAND_BASE_NUMERIC = [
    "area", "frontage_width", "house_depth", "road_width",
    "published_year", "published_month",
    "district_name_freq", "ward_name_freq", "street_name_freq", "project_name_freq",
    "desc_floor_count_text", "desc_bedroom_count_text", "desc_bathroom_count_text",
    "desc_road_width_text_m", "desc_frontage_width_text_m",
    "desc_distance_beach_m", "desc_distance_center_m", "desc_signal_count",
    "desc_has_legal_docs", "desc_has_car_access", "desc_has_frontage",
    "desc_has_alley", "desc_has_corner", "desc_has_business", "desc_has_elevator",
    "desc_has_sea_river_lake_view", "desc_has_near_beach", "desc_has_near_amenities",
    "desc_has_urgent_sale", "desc_has_new_house",
]
DN_LAND_CATEGORICAL = ["district_name", "ward_name", "street_name", "project_name", "house_direction"]
DN_NONLAND_BASE_NUMERIC = [
    "area", "floor_count", "frontage_width", "house_depth", "road_width",
    "bedroom_count", "bathroom_count", "published_year", "published_month",
    "district_name_freq", "ward_name_freq", "street_name_freq", "project_name_freq",
    "desc_floor_count_text", "desc_bedroom_count_text", "desc_bathroom_count_text",
    "desc_road_width_text_m", "desc_frontage_width_text_m",
    "desc_distance_beach_m", "desc_distance_center_m", "desc_signal_count",
    "desc_has_legal_docs", "desc_has_car_access", "desc_has_frontage",
    "desc_has_alley", "desc_has_corner", "desc_has_business", "desc_has_elevator",
    "desc_has_sea_river_lake_view", "desc_has_near_beach", "desc_has_near_amenities",
    "desc_has_urgent_sale", "desc_has_new_house",
]
DN_NONLAND_CATEGORICAL = [
    "property_type_name", "district_name", "ward_name", "street_name",
    "project_name", "house_direction", "balcony_direction",
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
    try:
        if inp.city == "hue":
            return _build_hue(inp)
        elif inp.city == "cantho":
            return _build_cantho(inp)
        elif inp.city in {"danang", "haiphong"}:
            return _build_danang(inp)
        elif inp.city == "hanoi":
            return _build_hanoi(inp)
        else:
            return _build_hcm_group(inp)
    except Exception as exc:
        raise FeatureBuildError(f"Không thể build feature vector: {exc}") from exc


# ═══════════════════════════════════════════════════════════════════════════════
# HUẾ
# ═══════════════════════════════════════════════════════════════════════════════

def _build_hue(inp: PredictInput) -> pd.DataFrame:
    """
    Bundle format: {model, artifacts:{numeric_features, categorical_features,
                                       feature_cols, imputer, capper, preprocessor}}
    Pipeline: imputer → capper → preprocessor (ColumnTransformer OHE) → XGB/LGBM
    Target: log1p(price_vnd) → expm1() ra VNĐ
    """
    # Lấy feature list từ bundle artifacts (nested dict)
    num_feats, cat_feats = _get_hue_feature_lists(inp)

    row: dict[str, Any] = {}
    area      = float(inp.area)
    bedrooms  = float(inp.bedrooms  or 0)
    bathrooms = float(inp.bathrooms or 0)
    log_area  = float(np.log1p(area))
    province_norm = CITY_PROVINCE_NORM["hue"]

    text          = _norm_lower(inp.description) + " " + _norm_lower(inp.property_type)
    district_norm = _norm_lower(inp.district)
    ward_norm     = _norm_lower(inp.ward)
    street_norm   = _norm_lower(inp.street) if inp.street else ""

    # ── Keywords ──────────────────────────────────────────────────────────────
    for feat, kws in {**COMMON_KW, "has_gan_trung_tam": HUE_TRUNG_TAM_KW}.items():
        row[feat] = int(bool(re.search("|".join(re.escape(k) for k in kws), text)))
    for feat, kws in HUE_LAND_KW.items():
        row[feat] = int(bool(re.search("|".join(re.escape(k) for k in kws), text)))
    for feat, kws in HUE_NONLAND_KW.items():
        row[feat] = int(bool(re.search("|".join(re.escape(k) for k in kws), text)))

    # ── Numerics ──────────────────────────────────────────────────────────────
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
        "is_large_land": int(area >= 100),
        "street_missing": int(not bool(street_norm)),
    })

    # ── District group (Huế) ──────────────────────────────────────────────────
    is_core     = int(district_norm in HUE_CORE_DISTRICTS)
    is_urban    = int(district_norm in HUE_URBAN_DISTRICTS)
    is_suburban = int(is_core == 0 and is_urban == 0)
    row.update({"is_hue_core": is_core, "is_hue_urban": is_urban, "is_hue_suburban": is_suburban})
    district_group = "core" if is_core else ("urban" if is_urban else "suburban")
    row["district_group"] = district_group
    row["large_land_x_suburban"] = row["is_large_land"] * is_suburban

    # ── Address ───────────────────────────────────────────────────────────────
    row["district_address"]   = f"{district_norm}__{province_norm}"
    row["ward_address"]       = f"{ward_norm}__{district_norm}__{province_norm}"
    row["property_type_name"] = _norm_lower(inp.property_type)

    # ── Frequency ─────────────────────────────────────────────────────────────
    freq_maps = _get_freq_maps(inp.model_key)
    _set_freq(row, "district_name_freq",    district_norm,          freq_maps, "district_name")
    _set_freq(row, "ward_name_freq",        ward_norm,              freq_maps, "ward_name")
    _set_freq(row, "district_address_freq", row["district_address"],freq_maps, "district_address")
    _set_freq(row, "ward_address_freq",     row["ward_address"],    freq_maps, "ward_address")

    # ── Area bin ──────────────────────────────────────────────────────────────
    area_bins = _get_area_bins(inp.model_key)
    area_bin  = _apply_area_bin(area, area_bins)
    row["area_bin"]          = area_bin
    row["district_area_bin"] = f"{district_group}__{area_bin}"

    # ── Relationships ─────────────────────────────────────────────────────────
    for fc in ["district_name_freq", "ward_name_freq", "district_address_freq", "ward_address_freq"]:
        v = row.get(fc, 0.0)
        row[f"area_x_{fc.replace('_freq','_freq')}"]     = area * v
        row[f"log_area_x_{fc.replace('_freq','_freq')}"] = log_area * v
    # Huế dùng tên riêng: area_x_district_freq (không phải area_x_district_name_freq)
    row["area_x_district_freq"]     = area * row.get("district_name_freq", 0.0)
    row["area_x_ward_freq"]         = area * row.get("ward_name_freq", 0.0)
    row["log_area_x_district_freq"] = log_area * row.get("district_name_freq", 0.0)
    row["log_area_x_ward_freq"]     = log_area * row.get("ward_name_freq", 0.0)

    row["mat_tien_x_log_area"]       = row.get("has_mat_tien",0) * log_area
    row["goc_2_mat_tien_x_log_area"] = row.get("has_goc_2_mat_tien",0) * log_area
    row["so_hong_x_log_area"]        = row.get("has_so_hong",0) * log_area
    row["gan_trung_tam_x_log_area"]  = row.get("has_gan_trung_tam",0) * log_area

    row["land_accessibility_score"]    = row.get("land_kw_duong_rong",0) + row.get("land_kw_ngo_oto",0)
    row["land_legal_score"]            = row.get("has_so_hong",0) + row.get("land_kw_khong_quy_hoach",0)
    row["land_accessibility_x_log_area"] = row["land_accessibility_score"] * log_area
    row["land_legal_x_log_area"]         = row["land_legal_score"] * log_area

    row["nonland_business_score"] = (row.get("has_mat_tien",0) + row.get("has_hem_xe_hoi",0)
                                     + row.get("nonland_kw_kinh_doanh_cho_thue",0))
    row["nonland_luxury_score"]   = (row.get("has_full_noi_that",0) + row.get("nonland_kw_thang_may",0)
                                     + row.get("nonland_kw_view_dep",0))
    row["nonland_business_x_log_area"] = row["nonland_business_score"] * log_area
    row["nonland_luxury_x_log_area"]   = row["nonland_luxury_score"] * log_area
    row["thang_may_x_area"]            = row.get("nonland_kw_thang_may",0) * area

    return _to_df(row, num_feats, cat_feats, use_street=False)


def _get_hue_feature_lists(inp: PredictInput) -> tuple[list[str], list[str]]:
    """
    Bundle Huế lưu feature list trong bundle["artifacts"]["numeric_features"].
    Fallback về hardcoded nếu không có bundle.
    """
    # Registry cache artifact với key "artifacts" (từ _cache_bundle_artifacts)
    artifacts = registry.get_artifact(inp.model_key, "artifacts")
    if artifacts and isinstance(artifacts, dict):
        num = artifacts.get("numeric_features")
        cat = artifacts.get("categorical_features")
        if num and cat:
            logger.debug(f"[FeatureBuilder] Hue using bundle feature list: {len(num)}+{len(cat)}")
            return list(num), list(cat)

    # Fallback hardcoded
    logger.warning(f"[FeatureBuilder] Hue bundle artifacts not found for {inp.model_key}, using hardcoded")
    if inp.model_type == "land":
        return HUE_LAND_NUMERIC, HUE_LAND_CATEGORICAL
    return HUE_NONLAND_NUMERIC, HUE_NONLAND_CATEGORICAL


# ═══════════════════════════════════════════════════════════════════════════════
# CẦN THƠ
# ═══════════════════════════════════════════════════════════════════════════════

def _build_cantho(inp: PredictInput) -> pd.DataFrame:
    """
    Bundle: {pipeline, ohe_cols, freq_cols, numeric_cols, feature_cols, ...}

    feature_cols = ohe_cols + freq_cols + numeric_cols = 6 + 2 + 5 = 13 cột thô.
    Pipeline bên trong tự OHE + FrequencyEncode + Scale.

    QUAN TRỌNG: tên cột phải khớp CHÍNH XÁC với lúc train.
    - ohe_cols: string thô → ColumnTransformer OHE encode
    - freq_cols: string thô → FrequencyEncoder encode  
    - numeric_cols: float → SimpleImputer + StandardScaler

    Target: log1p(price) → expm1() ra VNĐ (KHÔNG nhân area).
    """
    # Lấy từ bundle, fallback hardcoded từ notebook
    ohe_cols     = list(registry.get_artifact(inp.model_key, "ohe_cols")     or CT_OHE_COLS)
    freq_cols    = list(registry.get_artifact(inp.model_key, "freq_cols")    or CT_FREQ_COLS)
    numeric_cols = list(registry.get_artifact(inp.model_key, "numeric_cols") or CT_NUMERIC_COLS)
    feature_cols = ohe_cols + freq_cols + numeric_cols

    area      = float(inp.area)
    bedrooms  = float(inp.bedrooms  or 0)
    bathrooms = float(inp.bathrooms or 0)
    district_norm = _norm_lower(inp.district)
    ward_norm     = _norm_lower(inp.ward)
    # Freq encoder dùng "__MISSING__" cho unseen — phải dùng đúng string này
    street_norm   = _norm_lower(inp.street) if inp.street else "__MISSING__"
    province_norm = CITY_PROVINCE_NORM.get(inp.city, inp.city)
    text_norm     = _normalize_description_text((inp.description or "") + " " + (inp.property_type or ""))

    # Build đúng 13 cột theo thứ tự feature_cols
    # Giá trị mặc định khớp với SimpleImputer(strategy="constant", fill_value="__MISSING__")
    row: dict[str, Any] = {
        # ── OHE cols (6) ──────────────────────────────────────────────────────
        "property_type_name": _norm_lower(inp.property_type) or "__MISSING__",
        "province_name":      province_norm,
        "district_name":      district_norm  or "__MISSING__",
        "ward_name":          ward_norm      or "__MISSING__",
        "house_direction":    "__MISSING__",
        "balcony_direction":  "__MISSING__",
        # ── Freq cols (2) — truyền string thô, FrequencyEncoder tự lookup ─────
        "street_name":  street_norm,
        "project_name": "__MISSING__",
        # ── Numeric cols (5) — SimpleImputer(median) xử lý NaN ───────────────
        "area":           area,
        "log_area":       float(np.log1p(area)),
        "frontage_width": _extract_number(
            text_norm, [r"ngang[^0-9]{0,10}([\d.,]+)\s*m"], 1, 50
        ),  # NaN nếu không tìm thấy → imputer xử lý
        "bedroom_count":  bedrooms,
        "bathroom_count": bathrooms,
    }

    # Chỉ giữ đúng feature_cols theo thứ tự từ bundle
    df = pd.DataFrame([row])
    for col in feature_cols:
        if col not in df.columns:
            # Fallback an toàn — không nên xảy ra nếu row đã đủ
            df[col] = np.nan if col in numeric_cols else "__MISSING__"
            logger.warning(f"[FeatureBuilder] CanTho missing col {col}, using default")
    return df[feature_cols]


# ═══════════════════════════════════════════════════════════════════════════════
# ĐÀ NẴNG / HẢI PHÒNG
# ═══════════════════════════════════════════════════════════════════════════════

def _build_danang(inp: PredictInput) -> pd.DataFrame:
    """
    Target: log1p(price_per_m2) → predictor nhân × area.
    Feature list từ bundle nếu có, fallback hardcoded.
    """
    num_feats = list(registry.get_artifact(inp.model_key, "numeric_features") or [])
    cat_feats = list(registry.get_artifact(inp.model_key, "categorical_features") or [])
    if not num_feats or not cat_feats:
        num_feats = DN_LAND_BASE_NUMERIC  if inp.model_type == "land" else DN_NONLAND_BASE_NUMERIC
        cat_feats = DN_LAND_CATEGORICAL   if inp.model_type == "land" else DN_NONLAND_CATEGORICAL

    area      = float(inp.area)
    bedrooms  = float(inp.bedrooms  or 0)
    bathrooms = float(inp.bathrooms or 0)
    text_norm     = _normalize_description_text((inp.description or "") + " " + (inp.property_type or ""))
    district_norm = _norm_lower(inp.district)
    ward_norm     = _norm_lower(inp.ward)
    street_norm   = _norm_lower(inp.street) if inp.street else ""

    import datetime
    now = datetime.datetime.now()
    row: dict[str, Any] = {
        "area": area, "bedroom_count": bedrooms, "bathroom_count": bathrooms,
        "floor_count": np.nan, "house_depth": np.nan,
        "frontage_width": _extract_number(text_norm, [r"ngang[^0-9]{0,10}([\d.,]+)\s*m"], 1, 50),
        "road_width": _extract_number(text_norm, [r"(?:duong|mat duong|hem|kiet)[^0-9]{0,15}([\d.,]+)\s*m"], 0.5, 100),
        "published_year": now.year, "published_month": now.month,
    }

    freq_maps = _get_freq_maps(inp.model_key)
    row["district_name_freq"] = float(freq_maps.get("district_name", {}).get(district_norm, 0))
    row["ward_name_freq"]     = float(freq_maps.get("ward_name",     {}).get(ward_norm,     0))
    row["street_name_freq"]   = float(freq_maps.get("street_name",   {}).get(street_norm,   0))
    row["project_name_freq"]  = 0.0

    for col, pattern in DN_PATTERN_FEATURES.items():
        row[col] = int(bool(re.search(pattern, text_norm)))

    row.update({
        "desc_floor_count_text":      _extract_number(text_norm, [r"([\d]+)\s*(?:tang|lau)\b"], 1, 100),
        "desc_bedroom_count_text":    _extract_number(text_norm, [r"([\d]+)\s*(?:pn|phong ngu|ngu)\b"], 1, 50),
        "desc_bathroom_count_text":   _extract_number(text_norm, [r"([\d]+)\s*(?:wc|toilet|phong tam)\b"], 1, 50),
        "desc_road_width_text_m":     row["road_width"],
        "desc_frontage_width_text_m": row["frontage_width"],
        "desc_distance_beach_m":      _extract_distance_m(text_norm, r"bien"),
        "desc_distance_center_m":     _extract_distance_m(text_norm, r"trung tam"),
        "desc_signal_count":          float(sum(row.get(c, 0) for c in DN_PATTERN_FEATURES)),
        "district_name": district_norm, "ward_name": ward_norm,
        "street_name":   street_norm if street_norm else "__missing__",
        "project_name":  "__missing__", "house_direction": "__missing__",
        "balcony_direction": "__missing__",
        "property_type_name": _norm_lower(inp.property_type),
    })

    all_feats = list(num_feats) + list(cat_feats)
    df = pd.DataFrame([row])
    for col in all_feats:
        if col not in df.columns:
            df[col] = np.nan if col in num_feats else "__missing__"
    return df[all_feats]


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
    province_norm = CITY_PROVINCE_NORM["hanoi"]

    text          = _norm_lower(inp.description) + " " + _norm_lower(inp.property_type)
    district_norm = _norm_lower(inp.district)
    ward_norm     = _norm_lower(inp.ward)
    street_norm   = _norm_lower(inp.street) if inp.street else ""

    for feat, kws in {**COMMON_KW, "has_gan_trung_tam": HN_TRUNG_TAM_KW}.items():
        row[feat] = int(bool(re.search("|".join(re.escape(k) for k in kws), text)))
    for feat, kws in HN_LAND_KW.items():
        row[feat] = int(bool(re.search("|".join(re.escape(k) for k in kws), text)))
    for feat, kws in HN_NONLAND_KW.items():
        row[feat] = int(bool(re.search("|".join(re.escape(k) for k in kws), text)))

    row.update({
        "area_m2_raw": area, "area_m2_missing": int(area<=0), "log_area_m2": log_area,
        "bedroom_count": bedrooms, "bathroom_count": bathrooms,
        "bedroom_count_missing": int(inp.bedrooms is None),
        "bathroom_count_missing": int(inp.bathrooms is None),
        "bedroom_per_m2": bedrooms/(area+1), "bathroom_per_m2": bathrooms/(area+1),
        "bathroom_per_bedroom": bathrooms/(bedrooms+1),
        "name_len": len(inp.property_type), "description_len": len(inp.description),
        "description_word_count": len(inp.description.split()),
        "room_total": bedrooms+bathrooms, "bedroom_x_log_area": bedrooms*log_area,
        "bathroom_x_log_area": bathrooms*log_area,
        "is_studio_like": int(bedrooms<=1 and area<=45),
        "is_large_unit": int(area>=100 or bedrooms>=4),
        "is_family_unit": int(bedrooms>=3),
        "room_density_score": (bedrooms+bathrooms)/(area+1),
        "is_tiny_land": int(area<30), "is_small_land": int(30<=area<50),
        "is_medium_land": int(50<=area<100), "is_large_land": int(area>=100),
    })

    is_core  = int(district_norm in HANOI_CORE_DISTRICTS)
    is_urban = int(district_norm in HANOI_URBAN_DISTRICTS)
    is_suburban = int(is_core==0 and is_urban==0)
    row.update({"is_core_district": is_core, "is_urban_district": is_urban,
                "is_suburban_district": is_suburban})
    district_group = "core" if is_core else ("urban" if is_urban else "suburban")
    row["district_group"] = district_group
    row.update({
        "tiny_land_x_core": row["is_tiny_land"]*is_core,
        "large_land_x_suburban": row["is_large_land"]*is_suburban,
        "large_land_x_urban": row["is_large_land"]*is_urban,
    })

    row["district_address"]   = f"{district_norm}__{province_norm}"
    row["ward_address"]       = f"{ward_norm}__{district_norm}__{province_norm}"
    row["street_address"]     = (f"{street_norm}__{ward_norm}__{district_norm}__{province_norm}"
                                 if use_street else "unknown")
    row["property_type_name"] = _norm_lower(inp.property_type)

    freq_maps = _get_freq_maps(inp.model_key)
    _set_freq(row, "district_name_freq",    district_norm,          freq_maps, "district_name")
    _set_freq(row, "ward_name_freq",        ward_norm,              freq_maps, "ward_name")
    _set_freq(row, "district_address_freq", row["district_address"],freq_maps, "district_address")
    _set_freq(row, "ward_address_freq",     row["ward_address"],    freq_maps, "ward_address")
    _set_freq(row, "street_name_freq",    street_norm if use_street else "", freq_maps, "street_name")
    _set_freq(row, "street_address_freq", row["street_address"] if use_street else "", freq_maps, "street_address")

    area_bins = _get_area_bins(inp.model_key)
    area_bin  = _apply_area_bin(area, area_bins)
    row["area_bin"] = area_bin
    row["district_area_bin"] = f"{district_group}__{area_bin}"

    for fc in ["district_name_freq","ward_name_freq","district_address_freq","ward_address_freq"]:
        v = row.get(fc, 0.0)
        row[f"area_x_{fc}"] = area*v; row[f"log_area_x_{fc}"] = log_area*v
    if use_street:
        for fc in ["street_name_freq","street_address_freq"]:
            v = row.get(fc, 0.0)
            row[f"area_x_{fc}"] = area*v; row[f"log_area_x_{fc}"] = log_area*v

    row["land_frontage_score"]         = row.get("has_mat_tien",0)+row.get("has_goc_2_mat_tien",0)+row.get("land_kw_mat_tien_rong",0)
    row["land_accessibility_score"]    = row.get("land_kw_duong_rong",0)+row.get("land_kw_oto_tranh",0)+row.get("land_kw_ngo_oto",0)
    row["land_premium_location_score"] = row["land_frontage_score"]+row["land_accessibility_score"]+row.get("has_gan_trung_tam",0)+row.get("land_kw_gan_ho",0)
    row["land_legal_positive_score"]   = row.get("has_so_hong",0)+row.get("land_kw_khong_quy_hoach",0)
    row["land_planning_risk_score"]    = row.get("land_kw_quy_hoach_risk",0)
    row["land_shape_quality_score"]    = row.get("land_kw_no_hau",0)+row.get("land_kw_vuong_van",0)
    for s in ["land_frontage","land_accessibility","land_premium_location","land_legal_positive","land_planning_risk","land_shape_quality"]:
        row[f"{s}_x_log_area"] = row[f"{s}_score"] * log_area
    row["land_premium_x_core"]        = row["land_premium_location_score"]*is_core
    row["land_accessibility_x_urban"] = row["land_accessibility_score"]*is_urban

    row["nonland_luxury_score"]           = row.get("has_full_noi_that",0)+row.get("nonland_kw_chung_cu_cao_cap",0)+row.get("nonland_kw_view_dep",0)+row.get("nonland_kw_can_goc",0)
    row["nonland_convenience_score"]      = row.get("nonland_kw_gan_metro",0)+row.get("nonland_kw_gan_tien_ich",0)+row.get("has_gan_trung_tam",0)
    row["nonland_building_quality_score"] = row.get("nonland_kw_thang_may",0)+row.get("nonland_kw_nha_moi",0)+row.get("nonland_kw_san_thuong",0)
    row["nonland_business_score"]         = row.get("has_mat_tien",0)+row.get("has_hem_xe_hoi",0)+row.get("nonland_kw_kinh_doanh_cho_thue",0)
    for s in ["nonland_luxury","nonland_convenience","nonland_building_quality","nonland_business"]:
        row[f"{s}_x_log_area"] = row[f"{s}_score"]*log_area
    row["nonland_luxury_x_core"]   = row["nonland_luxury_score"]*is_core
    row["nonland_business_x_core"] = row["nonland_business_score"]*is_core
    row["full_noi_that_x_bedroom"]  = row.get("has_full_noi_that",0)*bedrooms
    row["full_noi_that_x_bathroom"] = row.get("has_full_noi_that",0)*bathrooms
    row["thang_may_x_area"]         = row.get("nonland_kw_thang_may",0)*area
    row["nha_moi_x_log_area"]       = row.get("nonland_kw_nha_moi",0)*log_area

    num_feats = HN_LAND_NUMERIC  if inp.model_type=="land" else HN_NONLAND_NUMERIC
    cat_feats = HN_LAND_CATEGORICAL if inp.model_type=="land" else HN_NONLAND_CATEGORICAL
    return _to_df(row, num_feats, cat_feats, use_street)


# ═══════════════════════════════════════════════════════════════════════════════
# HCM GROUP (hcm, dongnai, + fallback)
# ═══════════════════════════════════════════════════════════════════════════════

def _build_hcm_group(inp: PredictInput) -> pd.DataFrame:
    row: dict[str, Any] = {}
    area      = float(inp.area)
    bedrooms  = float(inp.bedrooms  or 0)
    bathrooms = float(inp.bathrooms or 0)
    log_area  = float(np.log1p(area))
    use_street = inp.city in STREET_CITIES and bool(inp.street)
    province_norm = CITY_PROVINCE_NORM.get(inp.city, inp.city)

    text          = _norm_lower(inp.description) + " " + _norm_lower(inp.property_type)
    district_norm = _norm_lower(inp.district)
    ward_norm     = _norm_lower(inp.ward)
    street_norm   = _norm_lower(inp.street) if inp.street else ""

    for feat, kws in {**COMMON_KW, "has_gan_trung_tam": HCM_TRUNG_TAM_KW}.items():
        row[feat] = int(bool(re.search("|".join(re.escape(k) for k in kws), text)))

    row.update({
        "area_m2_raw": area, "area_m2_missing": int(area<=0), "log_area_m2": log_area,
        "bedroom_count": bedrooms, "bathroom_count": bathrooms,
        "bedroom_count_missing": int(inp.bedrooms is None),
        "bathroom_count_missing": int(inp.bathrooms is None),
        "bedroom_per_m2": bedrooms/(area+1), "bathroom_per_m2": bathrooms/(area+1),
        "bathroom_per_bedroom": bathrooms/(bedrooms+1),
        "name_len": len(inp.property_type), "description_len": len(inp.description),
        "description_word_count": len(inp.description.split()),
        "room_total": bedrooms+bathrooms, "bedroom_x_log_area": bedrooms*log_area,
        "bathroom_x_log_area": bathrooms*log_area,
        "is_studio_like": int(bedrooms<=1 and area<=45),
        "is_large_unit": int(area>=100 or bedrooms>=4),
    })

    is_core  = int(district_norm in HCM_CORE_DISTRICTS)
    is_urban = int(district_norm in HCM_URBAN_DISTRICTS)
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

    for fc in ["district_name_freq","ward_name_eff_freq","district_address_freq","ward_address_freq"]:
        v = row.get(fc, 0.0)
        row[f"area_x_{fc}"] = area*v; row[f"log_area_x_{fc}"] = log_area*v
    if use_street:
        for fc in ["street_name_freq","street_address_freq"]:
            v = row.get(fc, 0.0)
            row[f"area_x_{fc}"] = area*v; row[f"log_area_x_{fc}"] = log_area*v

    for kw in ["has_mat_tien","has_goc_2_mat_tien","has_so_hong","has_gan_trung_tam"]:
        v = row.get(kw, 0)
        row[f"{kw}_x_log_area"] = v*log_area; row[f"{kw}_x_core"] = v*is_core
    row["hem_x_log_area"]        = row.get("has_hem_ngo",0)*log_area
    row["hem_x_core"]            = row.get("has_hem_ngo",0)*is_core
    row["full_noi_that_x_bedroom"]  = row.get("has_full_noi_that",0)*bedrooms
    row["full_noi_that_x_log_area"] = row.get("has_full_noi_that",0)*log_area
    row["hem_xe_hoi_x_log_area"]    = row.get("has_hem_xe_hoi",0)*log_area
    row["mat_tien_x_core"]          = row.get("has_mat_tien",0)*is_core
    row["full_noi_that_x_core"]     = row.get("has_full_noi_that",0)*is_core
    row["kdc_x_log_area"]           = row.get("has_kdc",0)*log_area
    row["penthouse_x_log_area"]     = row.get("has_penthouse_duplex",0)*log_area

    num_feats = HCM_LAND_NUMERIC  if inp.model_type=="land" else HCM_NONLAND_NUMERIC
    cat_feats = HCM_LAND_CATEGORICAL if inp.model_type=="land" else HCM_NONLAND_CATEGORICAL
    return _to_df(row, num_feats, cat_feats, use_street)


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _to_df(row: dict, num_feats: list[str], cat_feats: list[str],
           use_street: bool) -> pd.DataFrame:
    all_feats = num_feats + cat_feats
    if not use_street:
        street_cols = {"street_name_freq","street_address_freq",
                       "area_x_street_name_freq","area_x_street_address_freq",
                       "log_area_x_street_name_freq","log_area_x_street_address_freq",
                       "street_address"}
        all_feats = [c for c in all_feats if c not in street_cols]
    df = pd.DataFrame([row])
    for col in all_feats:
        if col not in df.columns:
            df[col] = 0 if col in num_feats else "unknown"
    return df[all_feats]


def _set_freq(row: dict, target: str, key: str, freq_maps: dict, map_key: str) -> None:
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
        idx = int(np.clip(np.searchsorted(bins, area, side="right")-1, 0, len(bins)-2))
        return f"({bins[idx]:.1f}, {bins[idx+1]:.1f}]"
    except Exception:
        return "unknown"


def _extract_number(text: str, patterns: list[str],
                    min_val: float | None = None, max_val: float | None = None) -> float:
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
    ]
    for pat in patterns:
        m = re.search(pat, text)
        if not m:
            continue
        try:
            v = float(m.group(1).replace(",", "."))
            if m.group(2) == "km":
                v *= 1000
            if 1 <= v <= 100000:
                return v
        except Exception:
            continue
    return np.nan
