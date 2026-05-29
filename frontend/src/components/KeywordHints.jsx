/**
 * KeywordHints.jsx
 * ─────────────────
 * Hiển thị keywords model đang detect được từ description,
 * relationships giữa features, và gợi ý features còn thiếu.
 * Render ngay bên dưới ô description input.
 */

// ── Keyword rules theo city (mirror từ feature_builder.py) ───────────────────
const KEYWORD_RULES = {
  hanoi: [
    { key: "has_mat_tien",        label: "Mặt tiền",         keywords: ["mặt tiền","mặt phố","mặt đường","kinh doanh"] },
    { key: "has_goc_2_mat_tien",  label: "Góc 2 mặt tiền",   keywords: ["góc 2 mặt tiền","2 mặt tiền","lô góc"] },
    { key: "has_so_hong",         label: "Sổ hồng / Sổ đỏ",  keywords: ["sổ hồng","sổ đỏ","pháp lý rõ","sổ riêng","chính chủ"] },
    { key: "has_gan_trung_tam",   label: "Gần trung tâm",    keywords: ["trung tâm","gần trung tâm","phố cổ","hoàn kiếm"] },
    { key: "has_hem_xe_hoi",      label: "Hẻm / Ngõ ô tô",  keywords: ["hẻm xe hơi","ngõ ô tô","ô tô vào","ngõ rộng"] },
    { key: "has_full_noi_that",   label: "Full nội thất",    keywords: ["full nội thất","đầy đủ nội thất","tặng nội thất"] },
    { key: "land_kw_duong_rong",  label: "Đường rộng",       keywords: ["đường rộng","đường lớn","đường kinh doanh"] },
    { key: "land_kw_so_hong",     label: "Không quy hoạch",  keywords: ["không quy hoạch","quy hoạch ổn định"] },
    { key: "land_kw_phan_lo",     label: "Phân lô / Liền kề",keywords: ["phân lô","liền kề","khu đô thị"] },
    { key: "land_kw_gan_ho",      label: "Gần hồ / View hồ", keywords: ["gần hồ","view hồ","ven hồ","hồ tây"] },
  ],
  hcm: [
    { key: "has_mat_tien",        label: "Mặt tiền",         keywords: ["mặt tiền","mặt phố","mặt đường","kinh doanh"] },
    { key: "has_goc_2_mat_tien",  label: "Góc 2 mặt tiền",   keywords: ["góc 2 mặt tiền","2 mặt tiền","lô góc"] },
    { key: "has_so_hong",         label: "Sổ hồng / Sổ đỏ",  keywords: ["sổ hồng","sổ đỏ","pháp lý rõ","chính chủ"] },
    { key: "has_hem_xe_hoi",      label: "Hẻm xe hơi",       keywords: ["hẻm xe hơi","hẻm ô tô","ô tô vào","hẻm rộng"] },
    { key: "has_hem_ngo",         label: "Hẻm / Ngõ",        keywords: ["hẻm","hem"] },
    { key: "has_kdc",             label: "Khu dân cư",       keywords: ["khu dân cư","kdc","khu đô thị"] },
    { key: "has_full_noi_that",   label: "Full nội thất",    keywords: ["full nội thất","đầy đủ nội thất"] },
    { key: "has_penthouse_duplex",label: "Penthouse/Duplex",  keywords: ["penthouse","duplex","căn góc"] },
  ],
  danang: [
    { key: "desc_has_legal_docs",    label: "Pháp lý đầy đủ",  keywords: ["sổ đỏ","sổ hồng","pháp lý","hoàn công"] },
    { key: "desc_has_car_access",    label: "Ô tô vào được",   keywords: ["ô tô","xe hơi","đậu xe","đường ô tô"] },
    { key: "desc_has_frontage",      label: "Mặt tiền",        keywords: ["mặt tiền","mặt phố","mặt đường"] },
    { key: "desc_has_alley",         label: "Hẻm / Kiệt",      keywords: ["hẻm","kiệt","ngõ"] },
    { key: "desc_has_sea_river_view",label: "View biển / sông",keywords: ["view biển","view sông","ven sông","gần biển"] },
    { key: "desc_has_near_beach",    label: "Gần biển",        keywords: ["gần biển","cách biển","đi bộ ra biển"] },
    { key: "desc_has_business",      label: "Kinh doanh",      keywords: ["kinh doanh","cho thuê","shophouse"] },
    { key: "desc_has_new_house",     label: "Nhà mới xây",     keywords: ["nhà mới","mới xây","xây mới"] },
  ],
  default: [
    { key: "has_mat_tien",  label: "Mặt tiền",        keywords: ["mặt tiền","mặt phố","kinh doanh"] },
    { key: "has_so_hong",   label: "Sổ hồng / Sổ đỏ", keywords: ["sổ hồng","sổ đỏ","pháp lý rõ","chính chủ"] },
    { key: "has_hem_xe_hoi",label: "Hẻm / Ngõ ô tô",  keywords: ["hẻm xe hơi","ô tô vào","ngõ rộng"] },
  ],
};

// ── Feature relationships ─────────────────────────────────────────────────────
const FEATURE_RELATIONSHIPS = [
  {
    condition: (d) => d.has_mat_tien && d.area >= 50,
    message: "✦ Mặt tiền + diện tích lớn → tăng đáng kể giá trị thương mại",
    type: "positive",
  },
  {
    condition: (d) => d.has_mat_tien && d.is_core,
    message: "✦ Mặt tiền quận trung tâm → premium cao nhất",
    type: "positive",
  },
  {
    condition: (d) => d.has_so_hong,
    message: "✦ Có sổ hồng / pháp lý rõ → model tin cậy hơn, giá chuẩn hơn",
    type: "positive",
  },
  {
    condition: (d) => !d.has_so_hong,
    message: "⚠ Chưa đề cập sổ hồng → model có thể đánh giá thấp hơn thực tế",
    type: "warning",
  },
  {
    condition: (d) => d.has_hem_xe_hoi,
    message: "✦ Ngõ / hẻm ô tô vào được → cộng điểm tiếp cận",
    type: "positive",
  },
  {
    condition: (d) => d.description_len < 50,
    message: "⚠ Mô tả quá ngắn → model thiếu context, độ chính xác giảm",
    type: "warning",
  },
  {
    condition: (d) => d.description_len >= 100,
    message: "✦ Mô tả đầy đủ → model đọc được nhiều tín hiệu hơn",
    type: "positive",
  },
];

// ── Missing features gợi ý ────────────────────────────────────────────────────
const SUGGESTIONS = [
  { check: (d) => !d.has_so_hong,      text: "Thêm: 'sổ hồng chính chủ' hoặc 'pháp lý rõ ràng'" },
  { check: (d) => !d.has_mat_tien && !d.has_hem_xe_hoi, text: "Thêm: tình trạng đường vào (mặt tiền / hẻm xe hơi / ngõ nhỏ)" },
  { check: (d) => d.description_len < 80, text: "Thêm: tiện ích xung quanh (gần chợ, trường, bệnh viện...)" },
  { check: (d) => !d.has_gan_trung_tam,   text: "Thêm: khoảng cách tới trung tâm hoặc điểm nổi bật gần đó" },
];

// ── Detect keywords từ description ───────────────────────────────────────────
function detectFeatures(description, city) {
  const text = (description || "").toLowerCase();
  const rules = KEYWORD_RULES[city] || KEYWORD_RULES.default;
  const detected = {};

  rules.forEach(({ key, keywords }) => {
    detected[key] = keywords.some((kw) => text.includes(kw.toLowerCase()));
  });

  detected.description_len = text.length;
  detected.area             = 0; // placeholder
  detected.is_core          = false;
  detected.has_mat_tien     = detected.has_mat_tien     || false;
  detected.has_so_hong      = detected.has_so_hong      || false;
  detected.has_hem_xe_hoi   = detected.has_hem_xe_hoi   || false;
  detected.has_gan_trung_tam= detected.has_gan_trung_tam|| false;

  return detected;
}

// ── Component ─────────────────────────────────────────────────────────────────
export default function KeywordHints({ description, city, area }) {
  if (!description || description.trim().length < 10) return null;

  const city_rules = KEYWORD_RULES[city] || KEYWORD_RULES.default;
  const text       = description.toLowerCase();

  // Detected keywords
  const detected  = city_rules.filter(({ keywords }) =>
    keywords.some((kw) => text.includes(kw.toLowerCase()))
  );
  const missing   = city_rules.filter(({ keywords }) =>
    !keywords.some((kw) => text.includes(kw.toLowerCase()))
  );

  // Feature signals for relationships
  const signals = detectFeatures(description, city);
  signals.area = parseFloat(area) || 0;

  const relationships = FEATURE_RELATIONSHIPS.filter(({ condition }) => {
    try { return condition(signals); } catch { return false; }
  });

  const suggestions = SUGGESTIONS.filter(({ check }) => {
    try { return check(signals); } catch { return false; }
  }).slice(0, 3);

  return (
    <div className="keyword-hints">

      {/* ── Detected ── */}
      {detected.length > 0 && (
        <div className="kh-section">
          <div className="kh-section-title">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
                 stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"
                 strokeLinejoin="round" aria-hidden="true">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
            Model đọc được {detected.length} tín hiệu từ mô tả
          </div>
          <div className="kh-chips">
            {detected.map(({ key, label }) => (
              <span key={key} className="kh-chip kh-chip--detected">{label}</span>
            ))}
          </div>
        </div>
      )}

      {/* ── Relationships ── */}
      {relationships.length > 0 && (
        <div className="kh-section">
          <div className="kh-section-title">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
                 stroke="currentColor" strokeWidth="2" strokeLinecap="round"
                 strokeLinejoin="round" aria-hidden="true">
              <path d="M18 20V10M12 20V4M6 20v-6"/>
            </svg>
            Ảnh hưởng tới giá dự đoán
          </div>
          <div className="kh-relationships">
            {relationships.map(({ message, type }, i) => (
              <div key={i} className={`kh-rel kh-rel--${type}`}>{message}</div>
            ))}
          </div>
        </div>
      )}

      {/* ── Suggestions ── */}
      {suggestions.length > 0 && (
        <div className="kh-section">
          <div className="kh-section-title">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
                 stroke="currentColor" strokeWidth="2" strokeLinecap="round"
                 strokeLinejoin="round" aria-hidden="true">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="8" x2="12" y2="12"/>
              <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            Gợi ý để tăng độ chính xác
          </div>
          <div className="kh-suggestions">
            {suggestions.map(({ text: t }, i) => (
              <div key={i} className="kh-suggestion">{t}</div>
            ))}
          </div>
        </div>
      )}

    </div>
  );
}
