// ─── HOW TO ADD YOUR LOGO PNG ──────────────────────────────────────────────
//
//  1. Copy your logo file to:  frontend/src/assets/logo.png
//
//  2. Uncomment the import below:
//     import logoImg from "../assets/logo.png";
//
//  3. Replace the <div className="logo-placeholder">P</div>
//     with:
//     <img src={logoImg} alt="PropVision logo"
//          style={{ width: "100%", height: "100%", objectFit: "contain", padding: "4px" }} />
//
// ───────────────────────────────────────────────────────────────────────────

 import logoImg from "../assets/logo_real_estate.png";

export default function Navbar() {
  return (
    <header className="navbar">
      {/* ── Brand ── */}
      <a href="/" className="nav-logo" aria-label="FPTVision — về trang chủ">
        <div className="logo-img-wrap" style={{width: "70px",height: "70px",}}>
          {/* ── LOGO SLOT: replace this div with <img> when ready ── */}
          <img src={logoImg} alt="FPTVision logo"
            style={{ width: "100%", height: "100%", objectFit: "contain", padding: "4px" }} />
        </div>
        <div className="logo-text">
          <div className="logo-name">FPT-RE</div>
          <div className="logo-tagline">AI Prediction for Real Estates</div>
        </div>
      </a>

      {/* ── Nav links ── */}
      <nav className="nav-links" aria-label="Điều hướng chính">
        <a href="/"         className="nav-link active">Định giá</a>
        <a href="/projects" className="nav-link">Dự án</a>
        <a href="/news"     className="nav-link">Tin tức</a>
        <a href="/contact"  className="nav-link">Liên hệ</a>
      </nav>

      {/* ── Account ── */}
      <div className="nav-actions">
        <button className="btn-account" type="button">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
               strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <circle cx="12" cy="8" r="4" />
            <path d="M4 20c0-4 3.6-7 8-7s8 3 8 7" />
          </svg>
          Tài khoản
        </button>
      </div>
    </header>
  );
}
