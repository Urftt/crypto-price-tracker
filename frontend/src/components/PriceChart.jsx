import { useState, useEffect, useMemo } from 'react';
import {
  LineChart, Line, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid,
} from 'recharts';
import { Button } from './ui/Button';

function PriceChart({ symbol }) {
  const [candles, setCandles] = useState([]);
  const [period, setPeriod] = useState('7d');
  const [loading, setLoading] = useState(true);

  const colors = useMemo(() => {
    const get = (prop) =>
      getComputedStyle(document.documentElement).getPropertyValue(prop).trim();
    return {
      border: get('--color-border'),
      textMuted: get('--color-text-muted'),
      card: get('--color-card'),
      borderLight: get('--color-border-light'),
      text: get('--color-text'),
      accent: get('--color-accent'),
    };
  }, []);

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
        <Button
          onClick={() => setPeriod('7d')}
          variant={period === '7d' ? 'primary' : 'ghost'}
          size="sm"
          type="button"
          className={period !== '7d' ? 'bg-border' : ''}
        >
          7D
        </Button>
        <Button
          onClick={() => setPeriod('30d')}
          variant={period === '30d' ? 'primary' : 'ghost'}
          size="sm"
          type="button"
          className={period !== '30d' ? 'bg-border' : ''}
        >
          30D
        </Button>
      </div>

      {loading ? (
        <div className="text-text-muted text-sm h-[250px] flex items-center justify-center">
          Loading...
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={data} margin={{ top: 5, right: 10, left: 10, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={colors.border} />
            <XAxis
              dataKey="time"
              tick={{ fill: colors.textMuted, fontSize: 11 }}
              stroke={colors.border}
            />
            <YAxis
              tick={{ fill: colors.textMuted, fontSize: 11 }}
              stroke={colors.border}
              domain={['auto', 'auto']}
            />
            <Tooltip
              contentStyle={{
                background: colors.card,
                border: `1px solid ${colors.borderLight}`,
                color: colors.text,
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
              stroke={colors.accent}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, fill: colors.accent }}
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}

export default PriceChart;
