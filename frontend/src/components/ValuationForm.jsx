import { useMemo } from "react";
import { CITIES, MODELS, PROPERTY_TYPES }   from "../utils/config";
import { getDistricts, getWards }            from "../utils/locationData";
import CitySelector    from "./CitySelector";
import AutocompleteInput from "./AutocompleteInput";
import KeywordHints    from "./KeywordHints";

function Icon({ d, size = 13 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
         stroke="currentColor" strokeWidth="2"
         strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d={d} />
    </svg>
  );
}

function FieldError({ message }) {
  if (!message) return null;
  return (
    <span className="field-error" role="alert">
      <Icon d="M12 8v4m0 4h.01M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
      {message}
    </span>
  );
}

export default function ValuationForm({
  city, switchCity,
  model, switchModel,
  form, updateField,
  errors,
  loading,
  onSubmit,
}) {
  const cityObj       = CITIES.find((c) => c.id === city);
  const showStreet    = cityObj?.hasStreet ?? false;
  const showRooms     = model === "non_land";
  const propertyTypes = PROPERTY_TYPES[model] ?? [];

  // Suggestion lists cho autocomplete
  const districtSuggestions = useMemo(() => getDistricts(city), [city]);
  const wardSuggestions     = useMemo(
    () => getWards(city, form.district),
    [city, form.district]
  );

  function handleCitySwitch(newCity) {
    switchCity(newCity);
    updateField("district", "");
    updateField("ward", "");
  }

  function handleDistrictSelect(val) {
    updateField("district", val);
    updateField("ward", ""); // reset ward khi đổi district
  }

  return (
    <div className="form-card" role="main">

      {/* ── City dropdown ─────────────────────────────────── */}
      <CitySelector selectedCity={city} onSelect={handleCitySwitch} />

      <div className="form-divider" style={{ margin: "20px 0 22px" }} />

      {/* ── Model toggle ──────────────────────────────────── */}
      <div className="section-header">
        <span className="section-dot" aria-hidden="true" />
        <span className="section-title">Loại hình bất động sản</span>
      </div>
      <div className="model-toggle">
        {MODELS.map((m) => (
          <button key={m.id} type="button"
            className={`model-btn${model === m.id ? " selected" : ""}`}
            onClick={() => switchModel(m.id)}
            aria-pressed={model === m.id}
            title={m.description}
          >
            {m.id === "land" ? (
              <svg width="17" height="17" viewBox="0 0 24 24" fill="none"
                   stroke="currentColor" strokeWidth="2"
                   strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21"/>
              </svg>
            ) : (
              <svg width="17" height="17" viewBox="0 0 24 24" fill="none"
                   stroke="currentColor" strokeWidth="2"
                   strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
              </svg>
            )}
            {m.label}
          </button>
        ))}
      </div>

      <div className="form-divider" />

      {/* ── Required fields ───────────────────────────────── */}
      <div className="fields-grid">

        {/* Quận / Huyện — autocomplete search */}
        <AutocompleteInput
          id="district"
          label="Quận / Huyện"
          required
          placeholder="Nhập để tìm quận/huyện..."
          value={form.district}
          onChange={(v) => updateField("district", v)}
          onSelect={handleDistrictSelect}
          suggestions={districtSuggestions}
          error={errors.district}
          icon={<Icon d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z" />}
        />

        {/* Phường / Xã — autocomplete, cascade từ district */}
        <AutocompleteInput
          id="ward"
          label="Phường / Xã"
          required
          placeholder={form.district ? "Nhập để tìm phường/xã..." : "Chọn quận/huyện trước"}
          value={form.ward}
          onChange={(v) => updateField("ward", v)}
          onSelect={(v) => updateField("ward", v)}
          suggestions={wardSuggestions}
          error={errors.ward}
          disabled={!form.district}
          icon={<Icon d="M17.657 16.657L13.414 20.9a1.998 1.998 0 0 1-2.827 0l-4.244-4.243a8 8 0 1 1 11.314 0z" />}
        />

        {/* Diện tích */}
        <div className="field-group">
          <label className="field-label" htmlFor="area">
            <Icon d="M3 3h18v18H3z" />
            Diện tích (m²) <span className="req-star">*</span>
          </label>
          <input id="area" type="number" min="1" step="0.1"
            className={`field-input${errors.area ? " error" : ""}`}
            placeholder="VD: 85"
            value={form.area}
            onChange={(e) => updateField("area", e.target.value)}
          />
          <FieldError message={errors.area} />
        </div>

        {/* Loại hình BĐS */}
        <div className="field-group">
          <label className="field-label" htmlFor="propertyType">
            <Icon d="M4 6h16M4 10h16M4 14h16M4 18h7" />
            Loại hình BĐS <span className="req-star">*</span>
          </label>
          <select id="propertyType"
            className={`field-select${errors.propertyType ? " error" : ""}`}
            value={form.propertyType}
            onChange={(e) => updateField("propertyType", e.target.value)}
          >
            <option value="">-- Chọn loại hình --</option>
            {propertyTypes.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
          <FieldError message={errors.propertyType} />
        </div>

        {/* Description + KeywordHints */}
        <div className="field-group field-span2">
          <label className="field-label" htmlFor="description">
            <Icon d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            Mô tả bất động sản <span className="req-star">*</span>
          </label>
          <textarea id="description" rows={3}
            className={`field-textarea${errors.description ? " error" : ""}`}
            placeholder="Mô tả chi tiết: tình trạng pháp lý (sổ hồng/sổ đỏ), đường vào (mặt tiền/hẻm xe hơi), tiện ích xung quanh, đặc điểm nổi bật..."
            value={form.description}
            onChange={(e) => updateField("description", e.target.value)}
          />
          <FieldError message={errors.description} />

          {/* Keyword hints hiện ngay dưới textarea */}
          <KeywordHints
            description={form.description}
            city={city}
            area={form.area}
          />
        </div>

      </div>

      {/* ── Optional fields ───────────────────────────────── */}
      <div className="form-divider" />
      <div className="optional-header">
        <div className="section-header" style={{ margin: 0 }}>
          <span className="section-dot" aria-hidden="true" />
          <span className="section-title">Thông tin bổ sung</span>
        </div>
        <span className="optional-badge">Tùy chọn · tăng độ chính xác</span>
      </div>

      <div className="optional-grid">
        {showStreet && (
          <div className="field-group">
            <label className="field-label" htmlFor="street">
              <Icon d="M5 12h14" /> Tên đường
            </label>
            <input id="street" type="text" className="field-input"
              placeholder="VD: Nguyễn Trãi, Lê Lợi..."
              value={form.street}
              onChange={(e) => updateField("street", e.target.value)}
            />
          </div>
        )}
        {showRooms && (
          <>
            <div className="field-group">
              <label className="field-label" htmlFor="bedrooms">
                <Icon d="M3 9l9-7 9 7v11H3V9z" /> Số phòng ngủ
              </label>
              <input id="bedrooms" type="number" min="0" max="20"
                className="field-input" placeholder="VD: 3"
                value={form.bedrooms}
                onChange={(e) => updateField("bedrooms", e.target.value)}
              />
            </div>
            <div className="field-group">
              <label className="field-label" htmlFor="bathrooms">
                <Icon d="M8 3H5a2 2 0 0 0-2 2v14h3M16 3h3a2 2 0 0 1 2 2v14h-3" />
                Số phòng tắm
              </label>
              <input id="bathrooms" type="number" min="0" max="10"
                className="field-input" placeholder="VD: 2"
                value={form.bathrooms}
                onChange={(e) => updateField("bathrooms", e.target.value)}
              />
            </div>
          </>
        )}
        {!showStreet && !showRooms && (
          <p className="optional-empty">
            Không có trường tùy chọn cho {cityObj?.label} / {model === "land" ? "Land" : "Non-land"}.
          </p>
        )}
      </div>

      {/* ── Submit ────────────────────────────────────────── */}
      <div className="form-divider" />
      <button type="button" className="submit-btn"
        onClick={onSubmit} disabled={loading} aria-busy={loading}>
        {loading ? (
          <>
            <svg className="spinner" width="18" height="18" viewBox="0 0 24 24"
                 fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
              <line x1="12" y1="2" x2="12" y2="6"/><line x1="12" y1="18" x2="12" y2="22"/>
              <line x1="4.93" y1="4.93" x2="7.76" y2="7.76"/><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"/>
              <line x1="2" y1="12" x2="6" y2="12"/><line x1="18" y1="12" x2="22" y2="12"/>
              <line x1="4.93" y1="19.07" x2="7.76" y2="16.24"/><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"/>
            </svg>
            Đang xử lý...
          </>
        ) : (
          <>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
                 stroke="currentColor" strokeWidth="2"
                 strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
            </svg>
            Nhận báo giá AI
          </>
        )}
      </button>
    </div>
  );
}
