import { useState, useEffect, useCallback } from 'react';
import { useApi } from '../hooks/useApi';
import { formatEUR, formatEURCompact, formatPct } from '../lib/format';

function PriceTable({ coins, onSelectCoin }) {
  const api = useApi();
  const [watchlistSymbols, setWatchlistSymbols] = useState(new Set());

  const loadWatchlist = useCallback(async () => {
    try {
      const data = await api.get('/api/watchlist/symbols');
      setWatchlistSymbols(new Set(data.symbols));
    } catch {
      // Ignore - stars just won't show
    }
  }, [api]);

  useEffect(() => {
    loadWatchlist();
  }, [loadWatchlist]);

  const toggleWatchlist = async (e, symbol) => {
    e.stopPropagation(); // Don't trigger row click (coin modal)
    try {
      if (watchlistSymbols.has(symbol)) {
        await api.del(`/api/watchlist/${symbol}`);
        setWatchlistSymbols((prev) => {
          const next = new Set(prev);
          next.delete(symbol);
          return next;
        });
      } else {
        await api.post('/api/watchlist', { symbol, tags: [] });
        setWatchlistSymbols((prev) => new Set(prev).add(symbol));
      }
    } catch {
      // Ignore errors silently
    }
  };

  return (
    <table className="w-full max-w-4xl">
      <thead>
        <tr>
          <th className="text-text-muted text-center text-xs uppercase py-1.5 px-1 border-b border-border w-8"></th>
          <th className="text-text-muted text-left text-xs uppercase py-1.5 px-3 border-b border-border">#</th>
          <th className="text-text-muted text-left text-xs uppercase py-1.5 px-3 border-b border-border">Symbol</th>
          <th className="text-text-muted text-left text-xs uppercase py-1.5 px-3 border-b border-border">Name</th>
          <th className="text-text-muted text-right text-xs uppercase py-1.5 px-3 border-b border-border">Price (EUR)</th>
          <th className="text-text-muted text-right text-xs uppercase py-1.5 px-3 border-b border-border">24h %</th>
          <th className="text-text-muted text-right text-xs uppercase py-1.5 px-3 border-b border-border">Volume (EUR)</th>
        </tr>
      </thead>
      <tbody>
        {coins.map((coin, i) => {
          const isWatched = watchlistSymbols.has(coin.symbol);
          return (
            <tr
              key={coin.symbol}
              onClick={() => onSelectCoin(coin)}
              className="cursor-pointer hover:bg-card border-b border-border/50"
            >
              <td className="py-1.5 px-1 text-center">
                <button
                  onClick={(e) => toggleWatchlist(e, coin.symbol)}
                  className={`cursor-pointer text-sm transition-colors ${
                    isWatched ? 'text-yellow-400' : 'text-text-dim hover:text-yellow-400/60'
                  }`}
                  title={isWatched ? 'Remove from watchlist' : 'Add to watchlist'}
                >
                  {isWatched ? '\u2605' : '\u2606'}
                </button>
              </td>
              <td className="py-1.5 px-3 text-text-dim text-sm">{i + 1}</td>
              <td className="py-1.5 px-3 text-accent font-bold">{coin.symbol}</td>
              <td className="py-1.5 px-3 text-text-muted text-sm">{coin.name}</td>
              <td className="py-1.5 px-3 text-right">{formatEUR(coin.price)}</td>
              <td className={`py-1.5 px-3 text-right ${coin.change_24h > 0 ? 'text-up' : coin.change_24h < 0 ? 'text-down' : 'text-text-muted'}`}>
                {formatPct(coin.change_24h)}
              </td>
              <td className="py-1.5 px-3 text-right text-text-muted">{formatEURCompact(coin.volume_eur)}</td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}

export default PriceTable;
