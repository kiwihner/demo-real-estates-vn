import { useState, useRef, useEffect, useCallback } from "react";

/**
 * AutocompleteInput
 * ──────────────────
 * Input field với dropdown gợi ý kiểu Google Search.
 *
 * Props:
 *   id, value, onChange, onSelect, placeholder
 *   suggestions: string[]  — danh sách để filter
 *   label, required, error, icon (JSX)
 *   disabled
 */
export default function AutocompleteInput({
  id,
  value,
  onChange,
  onSelect,
  placeholder,
  suggestions = [],
  label,
  required = false,
  error,
  icon,
  disabled = false,
}) {
  const [open,      setOpen]      = useState(false);
  const [highlight, setHighlight] = useState(-1);
  const wrapRef   = useRef(null);
  const inputRef  = useRef(null);
  const listRef   = useRef(null);

  // Filter suggestions theo input
  const filtered = useCallback(() => {
    if (!value || value.trim().length < 1) return suggestions.slice(0, 8);
    const q = value.toLowerCase().trim();
    const exact  = suggestions.filter((s) => s.toLowerCase().startsWith(q));
    const others = suggestions.filter(
      (s) => !s.toLowerCase().startsWith(q) && s.toLowerCase().includes(q)
    );
    return [...exact, ...others].slice(0, 8);
  }, [value, suggestions]);

  const items = filtered();

  // Close khi click ra ngoài
  useEffect(() => {
    function handleClick(e) {
      if (wrapRef.current && !wrapRef.current.contains(e.target)) {
        setOpen(false);
        setHighlight(-1);
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  // Scroll item được highlight vào view
  useEffect(() => {
    if (highlight >= 0 && listRef.current) {
      const item = listRef.current.children[highlight];
      item?.scrollIntoView({ block: "nearest" });
    }
  }, [highlight]);

  function handleInputChange(e) {
    onChange(e.target.value);
    setOpen(true);
    setHighlight(-1);
  }

  function handleKeyDown(e) {
    if (!open || items.length === 0) {
      if (e.key === "ArrowDown") { setOpen(true); setHighlight(0); }
      return;
    }
    switch (e.key) {
      case "ArrowDown":
        e.preventDefault();
        setHighlight((h) => Math.min(h + 1, items.length - 1));
        break;
      case "ArrowUp":
        e.preventDefault();
        setHighlight((h) => Math.max(h - 1, -1));
        break;
      case "Enter":
        e.preventDefault();
        if (highlight >= 0 && items[highlight]) {
          handleSelect(items[highlight]);
        }
        break;
      case "Escape":
        setOpen(false);
        setHighlight(-1);
        inputRef.current?.blur();
        break;
      default:
        break;
    }
  }

  function handleSelect(item) {
    onSelect ? onSelect(item) : onChange(item);
    setOpen(false);
    setHighlight(-1);
    inputRef.current?.blur();
  }

  function handleFocus() {
    if (!disabled) setOpen(true);
  }

  // Highlight matching text
  function renderLabel(text) {
    if (!value || value.trim().length < 1) return text;
    const q   = value.trim();
    const idx = text.toLowerCase().indexOf(q.toLowerCase());
    if (idx === -1) return text;
    return (
      <>
        {text.slice(0, idx)}
        <mark style={{
          background: "rgba(0,232,151,0.25)",
          color: "var(--accent)",
          borderRadius: "2px",
          padding: "0 1px",
        }}>
          {text.slice(idx, idx + q.length)}
        </mark>
        {text.slice(idx + q.length)}
      </>
    );
  }

  const showDropdown = open && items.length > 0 && !disabled;

  return (
    <div className="field-group" ref={wrapRef}>
      {label && (
        <label className="field-label" htmlFor={id}>
          {icon}
          {label}
          {required && <span className="req-star">*</span>}
        </label>
      )}

      <div className="ac-wrapper">
        <input
          ref={inputRef}
          id={id}
          type="text"
          autoComplete="off"
          spellCheck="false"
          className={`field-input ac-input${error ? " error" : ""}${disabled ? " ac-disabled" : ""}`}
          placeholder={placeholder}
          value={value}
          onChange={handleInputChange}
          onFocus={handleFocus}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          aria-autocomplete="list"
          aria-expanded={showDropdown}
          aria-controls={`${id}-list`}
          aria-activedescendant={highlight >= 0 ? `${id}-opt-${highlight}` : undefined}
        />

        {/* Clear button */}
        {value && !disabled && (
          <button
            type="button"
            className="ac-clear"
            onClick={() => { onChange(""); onSelect?.(""); setOpen(false); inputRef.current?.focus(); }}
            tabIndex={-1}
            aria-label="Xóa"
          >
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none"
                 stroke="currentColor" strokeWidth="2.5"
                 strokeLinecap="round" aria-hidden="true">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        )}

        {/* Dropdown */}
        {showDropdown && (
          <ul
            ref={listRef}
            id={`${id}-list`}
            role="listbox"
            className="ac-dropdown"
            aria-label={label}
          >
            {items.map((item, idx) => (
              <li
                key={item}
                id={`${id}-opt-${idx}`}
                role="option"
                aria-selected={idx === highlight}
                className={`ac-option${idx === highlight ? " ac-option--highlighted" : ""}`}
                onMouseDown={(e) => { e.preventDefault(); handleSelect(item); }}
                onMouseEnter={() => setHighlight(idx)}
              >
                {/* Search icon */}
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
                     stroke="currentColor" strokeWidth="2"
                     strokeLinecap="round" strokeLinejoin="round"
                     className="ac-option-icon" aria-hidden="true">
                  <circle cx="11" cy="11" r="8"/>
                  <line x1="21" y1="21" x2="16.65" y2="16.65"/>
                </svg>
                <span className="ac-option-text">{renderLabel(item)}</span>
                {/* Arrow to fill icon */}
                <svg width="11" height="11" viewBox="0 0 24 24" fill="none"
                     stroke="currentColor" strokeWidth="2"
                     strokeLinecap="round" strokeLinejoin="round"
                     className="ac-option-arrow" aria-hidden="true">
                  <polyline points="15 3 21 3 21 9"/>
                  <path d="M10 14L21 3"/>
                </svg>
              </li>
            ))}
          </ul>
        )}
      </div>

      {error && (
        <span className="field-error" role="alert">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none"
               stroke="currentColor" strokeWidth="2" strokeLinecap="round"
               strokeLinejoin="round" aria-hidden="true">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          {error}
        </span>
      )}
    </div>
  );
}
