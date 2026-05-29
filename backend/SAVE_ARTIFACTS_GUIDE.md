# Hướng dẫn Save Artifacts để Backend Hoạt Động Đúng

## Vấn đề cốt lõi

Feature engineering ở `feature_builder.py` cần 2 artifact được **fit trên training data**:
- `freq_maps` — frequency encoding per column
- `area_bins` — quantile bins của diện tích

Nếu thiếu → tất cả frequency features = 0.0, area_bin = fallback → kết quả kém chính xác.

---

## 1. HCM / Bình Dương / BRVT — Đã có bundle sẵn ✅

Notebook HCM đã save `inference_bundle.pkl` gồm cả `freq_maps` và `area_bins`.
Chỉ cần đặt file đúng tên vào `pkl_models/`:

```
pkl_models/
├── hcm_land_inference_bundle.pkl       ← land_inference_bundle.pkl từ notebook
└── hcm_non_land_inference_bundle.pkl   ← non_land_inference_bundle.pkl từ notebook
```

**Đổi tên file** khi copy vào:
```bash
cp /content/multi_province_inference/land_inference_bundle.pkl     pkl_models/hcm_land_inference_bundle.pkl
cp /content/multi_province_inference/non_land_inference_bundle.pkl pkl_models/hcm_non_land_inference_bundle.pkl
```

---

## 2. Hà Nội — Cần save thêm artifacts ⚠️

Notebook HN chỉ dump pipeline `.pkl`, **không** save `freq_maps` / `area_bins` riêng.
Cần thêm đoạn code vào cuối notebook để export:

```python
import joblib, os

HANOI_ARTIFACTS_DIR = "/content/hanoi_artifacts"
os.makedirs(HANOI_ARTIFACTS_DIR, exist_ok=True)

# ── Freq maps (fit từ train set) ──────────────────────────────────────────────
# FREQ_COLS_V4 = ["district_name", "ward_name", "district_address", "ward_address"]
# + ["street_name", "street_address"] nếu USE_STREET_KNOWN_ONLY=True

def extract_freq_maps(train_df, freq_cols):
    freq_maps = {}
    for col in freq_cols:
        if col in train_df.columns:
            freq_maps[col] = train_df[col].astype(str).value_counts(normalize=True).to_dict()
    return freq_maps

hanoi_land_freq_maps = extract_freq_maps(train_hanoi_land, FREQ_COLS_V4)
hanoi_non_land_freq_maps = extract_freq_maps(train_hanoi_non_land, FREQ_COLS_V4)

joblib.dump(hanoi_land_freq_maps,     f"{HANOI_ARTIFACTS_DIR}/hanoi_land_freq_maps.pkl")
joblib.dump(hanoi_non_land_freq_maps, f"{HANOI_ARTIFACTS_DIR}/hanoi_non_land_freq_maps.pkl")

# ── Area bins ─────────────────────────────────────────────────────────────────
hanoi_land_area_bins_arr     = fit_area_bins(train_hanoi_land)
hanoi_non_land_area_bins_arr = fit_area_bins(train_hanoi_non_land)

joblib.dump(hanoi_land_area_bins_arr,     f"{HANOI_ARTIFACTS_DIR}/hanoi_land_area_bins.pkl")
joblib.dump(hanoi_non_land_area_bins_arr, f"{HANOI_ARTIFACTS_DIR}/hanoi_non_land_area_bins.pkl")

# ── Best model pipeline ───────────────────────────────────────────────────────
# Đổi tên biến cho đúng với model bạn chọn (lgbm / xgboost / catboost)
joblib.dump(hanoi_land_model_v4_opt,     f"{HANOI_ARTIFACTS_DIR}/hanoi_land.pkl")
joblib.dump(hanoi_non_land_model_v4_opt, f"{HANOI_ARTIFACTS_DIR}/hanoi_non_land.pkl")

print("Saved Hanoi artifacts:")
for f in os.listdir(HANOI_ARTIFACTS_DIR):
    print(f"  {f}")
```

Sau đó copy vào `pkl_models/`:
```bash
cp /content/hanoi_artifacts/hanoi_land.pkl             pkl_models/hanoi_land.pkl
cp /content/hanoi_artifacts/hanoi_non_land.pkl         pkl_models/hanoi_non_land.pkl
cp /content/hanoi_artifacts/hanoi_land_freq_maps.pkl   pkl_models/hanoi_land_freq_maps.pkl
cp /content/hanoi_artifacts/hanoi_non_land_freq_maps.pkl pkl_models/hanoi_non_land_freq_maps.pkl
cp /content/hanoi_artifacts/hanoi_land_area_bins.pkl   pkl_models/hanoi_land_area_bins.pkl
cp /content/hanoi_artifacts/hanoi_non_land_area_bins.pkl pkl_models/hanoi_non_land_area_bins.pkl
```

---

## 3. Cấu trúc pkl_models/ đầy đủ

```
pkl_models/
├── hcm_land_inference_bundle.pkl        ← FORMAT A (bundle)
├── hcm_non_land_inference_bundle.pkl    ← FORMAT A (bundle)
├── hanoi_land.pkl                       ← FORMAT B (pipeline)
├── hanoi_non_land.pkl                   ← FORMAT B (pipeline)
├── hanoi_land_freq_maps.pkl             ← Artifact riêng cho HN
├── hanoi_non_land_freq_maps.pkl
├── hanoi_land_area_bins.pkl
├── hanoi_non_land_area_bins.pkl
├── danang_land.pkl                      ← FORMAT C (city khác, nếu có)
├── danang_non_land.pkl
└── ...
```

---

## 4. Verify sau khi đặt file

Chạy script kiểm tra nhanh:

```python
# scripts/verify_registry.py
from app.ml.registry import registry
from app.ml.schemas import ModelKey

for city, mtype in [("hcm", "land"), ("hcm", "non_land"), ("hanoi", "land"), ("hanoi", "non_land")]:
    key   = ModelKey(city=city, model_type=mtype)
    model = registry.get(key)
    fmaps = registry.get_artifact(key, "freq_maps")
    abins = registry.get_artifact(key, "area_bins")
    print(f"{key}: model={'✅' if model else '❌'} | freq_maps={'✅' if fmaps else '⚠️ (=0)'} | area_bins={'✅' if abins else '⚠️ (fallback)'}")
```

---

## 5. Feature mismatch check

Nếu predict raise lỗi sau khi có model, kiểm tra:

```python
from app.ml.feature_builder import build_features, HCM_LAND_NUMERIC, HCM_LAND_CATEGORICAL
from app.ml.schemas import PredictInput

inp = PredictInput(city="hcm", model_type="land", district="Bình Thạnh",
                   ward="Phường 13", area=75, property_type="Nhà mặt phố",
                   description="Nhà mặt tiền sổ hồng gần trung tâm")

X = build_features(inp)
print("Built columns:", X.columns.tolist())
print("Expected numeric:", HCM_LAND_NUMERIC)
print("Expected categorical:", HCM_LAND_CATEGORICAL)
```

Nếu model raise `ValueError: feature names mismatch` → pipeline đã được train
với feature list khác → cần cập nhật `HCM_LAND_NUMERIC` / `HCM_LAND_CATEGORICAL`
trong `feature_builder.py` cho khớp với `numeric_features` / `categorical_features`
trong bundle (đọc từ `bundle["numeric_features"]`).
