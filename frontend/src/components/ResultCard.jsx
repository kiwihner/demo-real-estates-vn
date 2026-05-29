import { CITIES, MODELS } from "../utils/config";
import { formatVND } from "../utils/formatPrice";

function Icon({ d, size = 14 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
         stroke="currentColor" strokeWidth="2"
         strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d={d} />
    </svg>
  );
}

export default function ResultCard({ result }) {
  if (!result) return null;

  const {
    price_low, price_mid, price_high,
    // confidence, confidence_label,
    model_used, is_fallback,
    price_range_label, price_per_sqm,
    property_info,
  } = result;

  const cityObj  = CITIES.find((c) => c.id === property_info?.city);
  const modelObj = MODELS.find((m) => m.id === property_info?.modelType);

  return (
    <div className="result-card" aria-live="polite" aria-atomic="true">
      <div className="result-glow" aria-hidden="true" />

      {/* ── Header ── */}
      <div className="result-header">
        <div className="result-icon-wrap">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none"
               stroke="currentColor" strokeWidth="2"
               strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
          </svg>
        </div>
        <div className="result-header-text">
          <p className="result-label">Kết quả định giá AI</p>
          <span className="result-model-tag">
            {cityObj?.label ?? property_info?.city}
            {" · "}
            {modelObj?.shortLabel ?? property_info?.modelType}
            {" · "}
            {model_used}
            {is_fallback && (
              <span style={{ color: "rgba(255,200,80,0.9)", marginLeft: 4 }}>
                · demo
              </span>
            )}
          </span>
        </div>
      </div>

      {/* ── Price range ── */}
      <div className="result-price-section">
        <div className="result-price"
             aria-label={`Khoảng giá ${price_range_label}`}>
          {price_range_label}
        </div>
        <div className="result-unit">VNĐ · Giá ước tính</div>

        <div className="result-midpoint">
          Giá trung bình:{" "}
          <strong>{formatVND(price_mid)}</strong>
          {/* {"  ·  "}
          Độ chính xác:{" "}
          <strong>{confidence_label}</strong> */}
          {price_per_sqm && (
            <>
              {"  ·  "}
              <strong>{formatVND(price_per_sqm)}/m²</strong>
            </>
          )}
        </div>
      </div>

      {/* ── Confidence bar ── */}
      {/* <ConfidenceBar value={confidence} /> */}

      {/* ── Property info tags ── */}
      {property_info && (
        <div className="result-tags">
          <span className="result-tag">
            <Icon d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z" />
            {cityObj?.label}
          </span>
          <span className="result-tag">
            <Icon d="M3 9l9-7 9 7v11H3V9z" />
            {property_info.district}{property_info.ward ? `, ${property_info.ward}` : ""}
          </span>
          <span className="result-tag">
            <Icon d="M3 3h18v18H3z" />
            {property_info.area} m²
          </span>
          <span className="result-tag">
            <Icon d="M4 6h16M4 10h16M4 14h16M4 18h7" />
            {property_info.propertyType}
          </span>
          {property_info.street && (
            <span className="result-tag">
              <Icon d="M5 12h14" />
              {property_info.street}
            </span>
          )}
          {property_info.bedrooms != null && (
            <span className="result-tag">
              <Icon d="M3 9l9-7 9 7v11H3V9z" />
              {property_info.bedrooms} phòng ngủ
            </span>
          )}
          {property_info.bathrooms != null && (
            <span className="result-tag">
              <Icon d="M8 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h3M16 3h3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-3" />
              {property_info.bathrooms} phòng tắm
            </span>
          )}
        </div>
      )}

      {/* ── Disclaimer ── */}
      <div className="result-note">
        <Icon d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" size={14} />
        <span>
          Kết quả được tạo bởi mô hình AI và chỉ mang tính tham khảo.
          Giá thực tế phụ thuộc vào tình trạng pháp lý, thị trường và yếu tố thực địa.
        </span>
      </div>
    </div>
  );
}

// ── Confidence bar ────────────────────────────────────────────────────────────
// function ConfidenceBar({ value }) {
//   const pct   = Math.round((value ?? 0) * 100);
//   const color = pct >= 80 ? "#00e897" : pct >= 65 ? "#f5a623" : "#ff5c5c";
//   const label = pct >= 80 ? "Cao" : pct >= 65 ? "Trung bình" : "Thấp";

//   return (
//     <div style={{ margin: "16px 0 4px" }}>
//       <div style={{
//         display: "flex", justifyContent: "space-between",
//         fontSize: 11, color: "var(--text-muted)", marginBottom: 6,
//       }}>
//         <span>Độ chính xác model</span>
//         <span style={{ color, fontWeight: 500 }}>{pct}% · {label}</span>
//       </div>
//       <div style={{
//         height: 4, borderRadius: 99,
//         background: "rgba(255,255,255,0.07)",
//       }}>
//         <div style={{
//           height: "100%", borderRadius: 99,
//           width: `${pct}%`,
//           background: color,
//           transition: "width 0.6s cubic-bezier(0.4,0,0.2,1)",
//         }} />
//       </div>
//     </div>
//   );
// }
