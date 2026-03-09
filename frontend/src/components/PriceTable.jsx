import { useState, useEffect, useCallback } from 'react';
import { useApi } from '../hooks/useApi';
import { formatEUR, formatEURCompact, formatPct } from '../lib/format';
import { Table, Th, Td } from './ui/Table';
import { Button } from './ui/Button';

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
    <Table className="max-w-4xl">
      <thead>
        <tr>
          <Th align="center" className="w-8 px-1"></Th>
          <Th>#</Th>
          <Th>Symbol</Th>
          <Th>Name</Th>
          <Th align="right">Price (EUR)</Th>
          <Th align="right">24h %</Th>
          <Th align="right">Volume (EUR)</Th>
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
              <Td align="center" className="px-1">
                <Button
                  variant="ghost"
                  size="xs"
                  onClick={(e) => toggleWatchlist(e, coin.symbol)}
                  type="button"
                  className={`text-sm ${isWatched ? 'text-yellow-400' : 'text-text-dim hover:text-yellow-400/60'}`}
                  title={isWatched ? 'Remove from watchlist' : 'Add to watchlist'}
                >
                  {isWatched ? '\u2605' : '\u2606'}
                </Button>
              </Td>
              <Td className="text-text-dim text-sm">{i + 1}</Td>
              <Td className="text-accent font-bold">{coin.symbol}</Td>
              <Td className="text-text-muted text-sm">{coin.name}</Td>
              <Td align="right">{formatEUR(coin.price)}</Td>
              <Td align="right" className={coin.change_24h > 0 ? 'text-up' : coin.change_24h < 0 ? 'text-down' : 'text-text-muted'}>
                {formatPct(coin.change_24h)}
              </Td>
              <Td align="right" className="text-text-muted">{formatEURCompact(coin.volume_eur)}</Td>
            </tr>
          );
        })}
      </tbody>
    </Table>
  );
}

export default PriceTable;
