import { useState, useEffect } from 'react';
import { useApi } from '../hooks/useApi';

function AddAlertForm({ defaultSymbol, onAdded }) {
  const api = useApi();
  const [symbol, setSymbol] = useState(defaultSymbol || '');
  const [targetPrice, setTargetPrice] = useState('');
  const [direction, setDirection] = useState('above');
  const [error, setError] = useState(null);

  useEffect(() => {
    if (defaultSymbol) {
      setSymbol(defaultSymbol);
    }
  }, [defaultSymbol]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      await api.post('/api/alerts', {
        symbol: symbol.toUpperCase(),
        target_price: parseFloat(targetPrice),
        direction,
      });
      setSymbol('');
      setTargetPrice('');
      setDirection('above');
      onAdded();
    } catch (err) {
      setError(err.message);
    }
  };

  const inputClass = 'bg-bg border border-border rounded px-3 py-1.5 text-text text-sm focus:border-accent focus:outline-none';

  return (
    <form onSubmit={handleSubmit} className="max-w-4xl mb-4">
      <div className="flex flex-wrap items-end gap-2">
        <input
          type="text"
          placeholder="Symbol"
          value={symbol}
          onChange={(e) => setSymbol(e.target.value)}
          className={`${inputClass} w-24 uppercase`}
          required
        />
        <input
          type="number"
          placeholder="Target Price EUR"
          value={targetPrice}
          onChange={(e) => setTargetPrice(e.target.value)}
          className={`${inputClass} w-36`}
          step="any"
          min="0"
          required
        />
        <select
          value={direction}
          onChange={(e) => setDirection(e.target.value)}
          className={`${inputClass}`}
        >
          <option value="above">above</option>
          <option value="below">below</option>
        </select>
        <button
          type="submit"
          className="bg-accent text-bg font-bold rounded px-4 py-1.5 text-sm hover:bg-accent/80 cursor-pointer"
        >
          Add Alert
        </button>
      </div>
      {error && <p className="text-down text-xs mt-1">{error}</p>}
    </form>
  );
}

export default AddAlertForm;
