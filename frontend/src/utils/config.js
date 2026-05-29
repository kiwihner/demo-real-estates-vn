// ─── Cities ───────────────────────────────────────────────────────────────────
export const CITIES = [
  { id: "hanoi",   label: "Tp.Hà Nội",   code: "HAN", hasStreet: true  },
  { id: "hcm",     label: "Tp.HCM",   code: "HCM", hasStreet: true  },
  { id: "danang",  label: "Tp.Đà Nẵng",  code: "DAN", hasStreet: true },
  { id: "hue",     label: "Tp.Huế",   code: "HUE", hasStreet: false },
  { id: "dongnai", label: "Tp,Đồng Nai", code: "DNI", hasStreet: false },
  { id: "cantho",  label: "Tp.Cần Thơ",  code: "CTO", hasStreet: false },
  { id: "haiphong", label: "Tp.Hải Phòng", code: "HP", hasStreet: false},
];

// ─── Models ───────────────────────────────────────────────────────────────────
export const MODELS = [
  {
    id: "land",
    label: "Đất (Land model)",
    shortLabel: "Land",
    description: "Đất thổ cư, nông nghiệp, thương mại",
  },
  {
    id: "non_land",
    label: "Nhà / Căn hộ (Non-land)",
    shortLabel: "Non-land",
    description: "Nhà phố, chung cư, biệt thự",
  },
];

// ─── Property Types ───────────────────────────────────────────────────────────
export const PROPERTY_TYPES = {
  land: [
    "Đất thổ cư"
  ],
  non_land: [
    "Căn hộ chung cư",
    "Nhà",
    "Biệt thự / Nhà liền kề",
    "Shophouse"
  ],
};

// ─── Required field keys ──────────────────────────────────────────────────────
export const REQUIRED_FIELDS = ["district", "ward", "area", "propertyType", "description"];

// ─── API base URL (overridden by env) ─────────────────────────────────────────
export const API_BASE = import.meta.env.VITE_API_URL || "/api";
