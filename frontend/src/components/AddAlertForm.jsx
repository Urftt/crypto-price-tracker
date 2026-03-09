import { useState, useEffect } from 'react';
import { useApi } from '../hooks/useApi';
import { Button } from './ui/Button';
import { Input } from './ui/Input';

function AddAlertForm({ defaultSymbol, onAdded }) {
  const api = useApi();
  const [symbol, setSymbol] = useState(defaultSymbol || '');
  const [targetPrice, setTargetPrice] = useState('');
  const [direction, setDirection] = useState('above');
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (defaultSymbol) {
      setSymbol(defaultSymbol);
    }
  }, [defaultSymbol]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
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
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-4xl mb-4">
      <div className="flex flex-wrap items-end gap-2">
        <Input
          label="Symbol"
          type="text"
          placeholder="BTC"
          value={symbol}
          onChange={(e) => setSymbol(e.target.value)}
          className="w-24"
          style={{ textTransform: 'uppercase' }}
          required
        />
        <Input
          label="Target Price EUR"
          type="number"
          placeholder="50000"
          value={targetPrice}
          onChange={(e) => setTargetPrice(e.target.value)}
          className="w-36"
          step="any"
          min="0"
          required
        />
        <div>
          <label htmlFor="alert-direction" className="text-text-muted text-xs mb-0.5 block">Direction</label>
          <select
            id="alert-direction"
            value={direction}
            onChange={(e) => setDirection(e.target.value)}
            className="bg-bg border border-border rounded px-3 py-1.5 text-text text-sm focus:border-accent focus:outline-none"
          >
            <option value="above">above</option>
            <option value="below">below</option>
          </select>
        </div>
        <Button type="submit" loading={submitting}>
          Add Alert
        </Button>
      </div>
      {error && <p className="text-down text-xs mt-1">{error}</p>}
    </form>
  );
}

export default AddAlertForm;
