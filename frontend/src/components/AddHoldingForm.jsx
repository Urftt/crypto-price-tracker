import { useState } from 'react';
import { useApi } from '../hooks/useApi';

function AddHoldingForm({ onAdded }) {
  const api = useApi();
  const [symbol, setSymbol] = useState('');
  const [amount, setAmount] = useState('');
  const [buyPrice, setBuyPrice] = useState('');
  const [buyDate, setBuyDate] = useState('');
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      await api.post('/api/portfolio', {
        symbol: symbol.toUpperCase(),
        amount: parseFloat(amount),
        buy_price: parseFloat(buyPrice),
        buy_date: buyDate || null,
      });
      setSymbol('');
      setAmount('');
      setBuyPrice('');
      setBuyDate('');
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
          placeholder="Amount"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          className={`${inputClass} w-28`}
          step="any"
          min="0"
          required
        />
        <input
          type="number"
          placeholder="Buy Price EUR"
          value={buyPrice}
          onChange={(e) => setBuyPrice(e.target.value)}
          className={`${inputClass} w-32`}
          step="any"
          min="0"
          required
        />
        <input
          type="date"
          value={buyDate}
          onChange={(e) => setBuyDate(e.target.value)}
          className={`${inputClass} w-36`}
        />
        <button
          type="submit"
          className="bg-accent text-bg font-bold rounded px-4 py-1.5 text-sm hover:bg-accent/80 cursor-pointer"
        >
          Add Holding
        </button>
      </div>
      {error && <p className="text-down text-xs mt-1">{error}</p>}
    </form>
  );
}

export default AddHoldingForm;
