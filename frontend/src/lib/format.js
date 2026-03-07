const eurFormatter = new Intl.NumberFormat('nl-NL', {
  style: 'currency',
  currency: 'EUR',
});

const eurCompactFormatter = new Intl.NumberFormat('nl-NL', {
  style: 'currency',
  currency: 'EUR',
  notation: 'compact',
  maximumFractionDigits: 1,
});

const pctFormatter = new Intl.NumberFormat('nl-NL', {
  style: 'percent',
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
  signDisplay: 'always',
});

export function formatEUR(value) {
  return eurFormatter.format(value);
}

export function formatEURCompact(value) {
  return eurCompactFormatter.format(value);
}

export function formatPct(value) {
  // value is already a percentage number (e.g., 2.5 for 2.5%)
  return pctFormatter.format(value / 100);
}
