import { CITY_OPTIONS } from "../utils/locationData";

/**
 * CitySelector — dropdown chọn thành phố
 * Props:
 *   selectedCity  — id đang chọn
 *   onSelect      — callback(cityId)
 */
export default function CitySelector({ selectedCity, onSelect }) {
  const selected = CITY_OPTIONS.find((c) => c.id === selectedCity);

  return (
    <div>
      <div className="section-header">
        <span className="section-dot" aria-hidden="true" />
        <span className="section-title">Chọn thành phố</span>
      </div>

      <div className="select-wrapper">
        <svg className="select-icon" viewBox="0 0 24 24" fill="none"
             stroke="currentColor" strokeWidth="2" strokeLinecap="round"
             strokeLinejoin="round" aria-hidden="true">
          <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z" />
        </svg>
        <select
          className="field-select select-with-icon"
          value={selectedCity}
          onChange={(e) => onSelect(e.target.value)}
          aria-label="Chọn thành phố"
        >
          {CITY_OPTIONS.map((c) => (
            <option key={c.id} value={c.id}>{c.label}</option>
          ))}
        </select>
      </div>

      {selected && (
        <p className="select-hint">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none"
               stroke="currentColor" strokeWidth="2" strokeLinecap="round"
               strokeLinejoin="round" aria-hidden="true">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          {selected.label}
          {selected.hasStreet
            ? " · Hỗ trợ tên đường (tùy chọn)"
            : " · Không có dữ liệu tên đường"}
        </p>
      )}
    </div>
  );
}
