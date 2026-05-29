/**
 * Format a raw VND number to a human-readable string.
 * e.g. 3_200_000_000 → "3,2 tỷ"
 *      450_000_000   → "450 triệu"
 */
export function formatVND(value) {
  if (!value && value !== 0) return "—";

  const billion = 1_000_000_000;
  const million  = 1_000_000;

  if (value >= billion) {
    const v = value / billion;
    // Show 1 decimal if not a whole number
    const formatted = v % 1 === 0 ? v.toFixed(0) : v.toFixed(1);
    return `${formatted} tỷ`;
  }

  if (value >= million) {
    const v = value / million;
    const formatted = v % 1 === 0 ? v.toFixed(0) : v.toFixed(0);
    return `${formatted} triệu`;
  }

  return new Intl.NumberFormat("vi-VN").format(value) + " đ";
}

/**
 * Format a price range object { low, high } to readable string.
 * e.g. { low: 3_200_000_000, high: 4_800_000_000 } → "3,2 tỷ – 4,8 tỷ"
 */
export function formatRange(low, high) {
  return `${formatVND(low)} – ${formatVND(high)}`;
}

/**
 * Format price per m² from total price and area.
 * e.g. (3_200_000_000, 85) → "37,6 triệu/m²"
 */
export function formatPricePerSqm(totalPrice, area) {
  if (!totalPrice || !area || area === 0) return "—";
  const perSqm = totalPrice / area;
  return `${formatVND(perSqm)}/m²`;
}
