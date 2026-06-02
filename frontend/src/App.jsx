import Navbar      from "./components/Navbar";
import ValuationForm from "./components/ValuationForm";
import ResultCard   from "./components/ResultCard";
import { useValuation } from "./hooks/useValuation";

// ── Toast notification ────────────────────────────────────────────────────────
function Toast({ toast }) {
  if (!toast) return null;
  const isError = toast.type === "error";
  return (
    <div className="toast-container" aria-live="assertive" aria-atomic="true">
      <div className={`toast${isError ? " error" : ""}`}>
        {isError ? (
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none"
               stroke="currentColor" strokeWidth="2" strokeLinecap="round"
               strokeLinejoin="round" aria-hidden="true">
            <circle cx="12" cy="12" r="10" />
            <line x1="15" y1="9" x2="9" y2="15" />
            <line x1="9" y1="9" x2="15" y2="15" />
          </svg>
        ) : (
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none"
               stroke="currentColor" strokeWidth="2" strokeLinecap="round"
               strokeLinejoin="round" aria-hidden="true">
            <polyline points="20 6 9 17 4 12" />
          </svg>
        )}
        {toast.message}
      </div>
    </div>
  );
}

// ── App ───────────────────────────────────────────────────────────────────────
export default function App() {
  const valuation = useValuation();

  return (
    <div className="app-root">
      {/* Background decoration */}
      <div className="bg-decoration" aria-hidden="true" />

      {/* Navigation */}
      <Navbar />

      {/* Main content */}
      <main className="main-content">

        {/* Hero */}
        <section className="hero" aria-labelledby="hero-title">
          <div className="hero-badge">
            <span className="pulse-dot" aria-hidden="true" />
            Multi-model AI · 5 thành phố
          </div>
          <h1 className="hero-title" id="hero-title">
            Định giá bất động sản<br />
            <span className="accent">thông minh</span>
          </h1>
          <p className="hero-subtitle">
            Dự báo giá chính xác dựa trên dữ liệu thị trường thực tế Việt Nam.
            Hỗ trợ đất và nhà ở tại 5 thành phố lớn.
          </p>
        </section>

        {/* Form */}
        <ValuationForm
          city={valuation.city}
          switchCity={valuation.switchCity}
          model={valuation.model}
          switchModel={valuation.switchModel}
          form={valuation.form}
          updateField={valuation.updateField}
          errors={valuation.errors}
          loading={valuation.loading}
          onSubmit={valuation.handleSubmit}
        />

        {/* Result */}
        {valuation.result && (
          <ResultCard result={valuation.result} />
        )}

      </main>

      {/* Footer */}
      <footer className="footer">
        <span className="footer-left">
          © 2026 FPT-RE AI · Kết quả chỉ mang tính tham khảo
        </span>
        {/* <nav className="footer-right" aria-label="Liên kết footer">
          <a href="/privacy" className="footer-link">Chính sách</a>
          <a href="/terms"   className="footer-link">Điều khoản</a>
          <a href="/contact" className="footer-link">Liên hệ</a>
        </nav> */}
      </footer>

      {/* Toast notification */}
      <Toast toast={valuation.toast} />
    </div>
  );
}
