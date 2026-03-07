function ExchangeDropdown({ value, onChange }) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="bg-border border border-border-light rounded px-2 py-1 text-text text-xs font-mono cursor-pointer hover:border-accent focus:border-accent focus:outline-none"
    >
      <option value="bitvavo">Bitvavo</option>
      <option value="binance">Binance</option>
    </select>
  );
}

export default ExchangeDropdown;
