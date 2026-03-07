import { useState, useEffect } from 'react';
import {
  LineChart, Line, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid,
} from 'recharts';

function PriceChart({ symbol }) {
  const [candles, setCandles] = useState([]);
  const [period, setPeriod] = useState('7d');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    const params = period === '7d'
      ? 'interval=4h&limit=42'
      : 'interval=1d&limit=30';

    fetch(`/api/candles/${symbol}?${params}`)
      .then((res) => res.json())
      .then((data) => {
        setCandles(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [symbol, period]);

  const data = candles.map((c) => ({
    time: new Date(c.timestamp).toLocaleDateString('nl-NL', {
      day: 'numeric',
      month: 'short',
    }),
    price: c.close,
  }));

  return (
    <div>
      <div className="flex gap-1 mb-3">
        <button
          onClick={() => setPeriod('7d')}
          className={`px-2.5 py-0.5 rounded text-xs cursor-pointer ${
            period === '7d'
              ? 'bg-accent text-bg'
              : 'bg-border text-text-muted hover:text-text'
          }`}
        >
          7D
        </button>
        <button
          onClick={() => setPeriod('30d')}
          className={`px-2.5 py-0.5 rounded text-xs cursor-pointer ${
            period === '30d'
              ? 'bg-accent text-bg'
              : 'bg-border text-text-muted hover:text-text'
          }`}
        >
          30D
        </button>
      </div>

      {loading ? (
        <div className="text-text-muted text-sm h-[250px] flex items-center justify-center">
          Loading...
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={data} margin={{ top: 5, right: 10, left: 10, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
            <XAxis
              dataKey="time"
              tick={{ fill: '#8b949e', fontSize: 11 }}
              stroke="#21262d"
            />
            <YAxis
              tick={{ fill: '#8b949e', fontSize: 11 }}
              stroke="#21262d"
              domain={['auto', 'auto']}
            />
            <Tooltip
              contentStyle={{
                background: '#161b22',
                border: '1px solid #30363d',
                color: '#c9d1d9',
                fontFamily: 'monospace',
              }}
              formatter={(value) =>
                new Intl.NumberFormat('nl-NL', {
                  style: 'currency',
                  currency: 'EUR',
                }).format(value)
              }
            />
            <Line
              type="monotone"
              dataKey="price"
              stroke="#58a6ff"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, fill: '#58a6ff' }}
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}

export default PriceChart;
