import { useState, useEffect, useCallback } from 'react';
import { useApi } from '../hooks/useApi';
import { formatEUR, formatEURCompact, formatPct } from '../lib/format';

const TAG_COLORS = {
  Layer1: 'bg-blue-900/50 text-blue-300 border-blue-700',
  Layer2: 'bg-purple-900/50 text-purple-300 border-purple-700',
  DeFi: 'bg-green-900/50 text-green-300 border-green-700',
  Meme: 'bg-yellow-900/50 text-yellow-300 border-yellow-700',
  Exchange: 'bg-orange-900/50 text-orange-300 border-orange-700',
  Privacy: 'bg-red-900/50 text-red-300 border-red-700',
};

function WatchlistPage() {
  const api = useApi();
  const [entries, setEntries] = useState([]);
  const [allTags, setAllTags] = useState([]);
  const [activeTags, setActiveTags] = useState([]);
  const [loading, setLoading] = useState(true);
  const [symbol, setSymbol] = useState('');
  const [selectedTags, setSelectedTags] = useState([]);
  const [error, setError] = useState(null);

  const loadWatchlist = useCallback(async () => {
    try {
      // If tags are active, fetch filtered for each tag (OR logic)
      // Simplest: fetch all and filter client-side for OR logic
      const data = await api.get('/api/watchlist');
      setEntries(data);
    } catch {
      // Keep previous state on error
    }
    setLoading(false);
  }, [api]);

  const loadTags = useCallback(async () => {
    try {
      const data = await api.get('/api/watchlist/tags');
      setAllTags(data.tags);
    } catch {
      // Ignore
    }
  }, [api]);

  useEffect(() => {
    loadWatchlist();
    loadTags();
  }, [loadWatchlist, loadTags]);

  const handleAdd = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      await api.post('/api/watchlist', {
        symbol: symbol.toUpperCase(),
        tags: selectedTags,
      });
      setSymbol('');
      setSelectedTags([]);
      loadWatchlist();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleRemove = async (sym) => {
    try {
      await api.del(`/api/watchlist/${sym}`);
      loadWatchlist();
    } catch {
      // Ignore
    }
  };

  const handleTagToggle = (tag) => {
    setActiveTags((prev) =>
      prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag]
    );
  };

  const handleFormTagToggle = (tag) => {
    setSelectedTags((prev) =>
      prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag]
    );
  };

  // Filter entries by active tags (OR logic: show entries that have ANY active tag)
  const filteredEntries = activeTags.length === 0
    ? entries
    : entries.filter((entry) => {
        const entryTags = entry.tags ? entry.tags.split(',') : [];
        return activeTags.some((t) => entryTags.includes(t));
      });

  const inputClass = 'bg-bg border border-border rounded px-3 py-1.5 text-text text-sm focus:border-accent focus:outline-none';

  if (loading) {
    return <p className="text-text-muted text-sm">Loading watchlist...</p>;
  }

  return (
    <div>
      <h2 className="text-lg font-bold text-text mb-4">Watchlist</h2>

      {/* Add to watchlist form */}
      <form onSubmit={handleAdd} className="max-w-4xl mb-4">
        <div className="flex flex-wrap items-end gap-2">
          <input
            type="text"
            placeholder="Symbol"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value)}
            className={`${inputClass} w-24 uppercase`}
            required
          />
          <div className="flex gap-1 items-center">
            {allTags.map((tag) => (
              <button
                key={tag}
                type="button"
                onClick={() => handleFormTagToggle(tag)}
                className={`px-2 py-0.5 rounded text-xs border cursor-pointer transition-opacity ${
                  TAG_COLORS[tag] || 'bg-border text-text-muted border-border'
                } ${selectedTags.includes(tag) ? 'opacity-100 ring-1 ring-accent' : 'opacity-50'}`}
              >
                {tag}
              </button>
            ))}
          </div>
          <button
            type="submit"
            className="bg-accent text-bg font-bold rounded px-4 py-1.5 text-sm hover:bg-accent/80 cursor-pointer"
          >
            Add to Watchlist
          </button>
        </div>
        {error && <p className="text-down text-xs mt-1">{error}</p>}
      </form>

      {/* Tag filter pills */}
      {allTags.length > 0 && (
        <div className="flex gap-1.5 mb-4 flex-wrap">
          <span className="text-text-muted text-xs py-1">Filter:</span>
          {allTags.map((tag) => (
            <button
              key={tag}
              onClick={() => handleTagToggle(tag)}
              className={`px-2.5 py-1 rounded-full text-xs border cursor-pointer transition-all ${
                TAG_COLORS[tag] || 'bg-border text-text-muted border-border'
              } ${activeTags.includes(tag) ? 'opacity-100 ring-1 ring-accent' : 'opacity-40 hover:opacity-70'}`}
            >
              {tag}
            </button>
          ))}
          {activeTags.length > 0 && (
            <button
              onClick={() => setActiveTags([])}
              className="text-text-muted text-xs hover:text-text cursor-pointer px-2 py-1"
            >
              Clear
            </button>
          )}
        </div>
      )}

      {/* Watchlist table */}
      {filteredEntries.length === 0 ? (
        <p className="text-text-muted text-sm">
          {activeTags.length > 0
            ? 'No entries match the selected tags.'
            : 'Watchlist is empty. Add coins using the form above or star them on the Prices tab.'}
        </p>
      ) : (
        <table className="w-full max-w-4xl">
          <thead>
            <tr>
              <th className="text-text-muted text-left text-xs uppercase py-1.5 px-3 border-b border-border">Symbol</th>
              <th className="text-text-muted text-left text-xs uppercase py-1.5 px-3 border-b border-border">Name</th>
              <th className="text-text-muted text-left text-xs uppercase py-1.5 px-3 border-b border-border">Tags</th>
              <th className="text-text-muted text-right text-xs uppercase py-1.5 px-3 border-b border-border">Price (EUR)</th>
              <th className="text-text-muted text-right text-xs uppercase py-1.5 px-3 border-b border-border">24h %</th>
              <th className="text-text-muted text-right text-xs uppercase py-1.5 px-3 border-b border-border">Volume (EUR)</th>
              <th className="text-text-muted text-center text-xs uppercase py-1.5 px-3 border-b border-border"></th>
            </tr>
          </thead>
          <tbody>
            {filteredEntries.map((entry) => (
              <tr key={entry.symbol} className="border-b border-border/50">
                <td className="py-1.5 px-3 text-accent font-bold">{entry.symbol}</td>
                <td className="py-1.5 px-3 text-text-muted text-sm">{entry.name || '-'}</td>
                <td className="py-1.5 px-3">
                  <div className="flex gap-1 flex-wrap">
                    {entry.tags
                      ? entry.tags.split(',').map((tag) => (
                          <span
                            key={tag}
                            className={`px-1.5 py-0.5 rounded text-xs border ${
                              TAG_COLORS[tag] || 'bg-border text-text-muted border-border'
                            }`}
                          >
                            {tag}
                          </span>
                        ))
                      : <span className="text-text-dim text-xs">-</span>}
                  </div>
                </td>
                <td className="py-1.5 px-3 text-right">
                  {entry.price != null ? formatEUR(entry.price) : <span className="text-text-dim">N/A</span>}
                </td>
                <td className={`py-1.5 px-3 text-right ${
                  entry.change_24h > 0 ? 'text-up' : entry.change_24h < 0 ? 'text-down' : 'text-text-muted'
                }`}>
                  {entry.change_24h != null ? formatPct(entry.change_24h) : <span className="text-text-dim">N/A</span>}
                </td>
                <td className="py-1.5 px-3 text-right text-text-muted">
                  {entry.volume_eur != null ? formatEURCompact(entry.volume_eur) : <span className="text-text-dim">N/A</span>}
                </td>
                <td className="py-1.5 px-3 text-center">
                  <button
                    onClick={() => handleRemove(entry.symbol)}
                    className="text-down text-xs hover:text-down/80 cursor-pointer"
                    title={`Remove ${entry.symbol} from watchlist`}
                  >
                    Remove
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default WatchlistPage;
