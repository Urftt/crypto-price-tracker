import { useState } from 'react';
import { useApi } from '../hooks/useApi';
import { Button } from './ui/Button';
import { Input } from './ui/Input';

function AddHoldingForm({ onAdded }) {
  const api = useApi();
  const [symbol, setSymbol] = useState('');
  const [amount, setAmount] = useState('');
  const [buyPrice, setBuyPrice] = useState('');
  const [buyDate, setBuyDate] = useState('');
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
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
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="mb-4 md:max-w-4xl">
      <div className="flex flex-col gap-3 md:flex-row md:flex-wrap md:items-end md:gap-2">
        <Input
          label="Symbol"
          type="text"
          placeholder="BTC"
          value={symbol}
          onChange={(e) => setSymbol(e.target.value)}
          className="w-full md:w-24"
          style={{ textTransform: 'uppercase' }}
          required
        />
        <Input
          label="Amount"
          type="number"
          placeholder="0.5"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          className="w-full md:w-28"
          step="any"
          min="0"
          required
        />
        <Input
          label="Buy Price EUR"
          type="number"
          placeholder="50000"
          value={buyPrice}
          onChange={(e) => setBuyPrice(e.target.value)}
          className="w-full md:w-32"
          step="any"
          min="0"
          required
        />
        <Input
          label="Buy Date"
          type="date"
          value={buyDate}
          onChange={(e) => setBuyDate(e.target.value)}
          className="w-full md:w-36"
        />
        <Button type="submit" loading={submitting} className="w-full md:w-auto">
          Add Holding
        </Button>
      </div>
      {error && <p className="text-down text-xs mt-1">{error}</p>}
    </form>
  );
}

export default AddHoldingForm;
