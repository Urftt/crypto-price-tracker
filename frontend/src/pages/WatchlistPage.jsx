import { useState, useEffect, useCallback } from 'react';
import { useApi } from '../hooks/useApi';
import { formatEUR, formatEURCompact, formatPct } from '../lib/format';
import { Table, Th, Td } from '../components/ui/Table';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Badge } from '../components/ui/Badge';

const TAG_COLORS = {
  Layer1: 'bg-blue-900/50 text-blue-300 border-blue-700',
  Layer2: 'bg-purple-900/50 text-purple-300 border-purple-700',
  DeFi: 'bg-green-900/50 text-green-300 border-green-700',
  Meme: 'bg-yellow-900/50 text-yellow-300 border-yellow-700',
  Exchange: 'bg-orange-900/50 text-orange-300 border-orange-700',
  Privacy: 'bg-red-900/50 text-red-300 border-red-700',
};

const TAG_COLOR_MAP = {
  Layer1: 'blue',
  Layer2: 'purple',
  DeFi: 'green',
  Meme: 'yellow',
  Exchange: 'orange',
  Privacy: 'red',
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
  const [editingSymbol, setEditingSymbol] = useState(null);
  const [editTags, setEditTags] = useState([]);
  const [submitting, setSubmitting] = useState(false);

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
    setSubmitting(true);
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
    } finally {
      setSubmitting(false);
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

  const handleStartEditTags = (entry) => {
    setEditingSymbol(entry.symbol);
    setEditTags(entry.tags ? entry.tags.split(',') : []);
  };

  const handleEditTagToggle = (tag) => {
    setEditTags((prev) =>
      prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag]
    );
  };

  const handleSaveTags = async (sym) => {
    try {
      await api.put(`/api/watchlist/${sym}/tags`, { tags: editTags });
      setEditingSymbol(null);
      setEditTags([]);
      loadWatchlist();
    } catch {
      // Ignore
    }
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

  if (loading) {
    return <p className="text-text-muted text-sm">Loading watchlist...</p>;
  }

  return (
    <div>
      <h2 className="text-lg font-bold text-text mb-4">Watchlist</h2>

      {/* Add to watchlist form */}
      <form onSubmit={handleAdd} className="mb-4 md:max-w-4xl">
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
          <div className="flex gap-1 items-center">
            {allTags.map((tag) => (
              <button
                key={tag}
                type="button"
                onClick={() => handleFormTagToggle(tag)}
                className={`px-2 py-0.5 rounded text-xs border cursor-pointer transition-opacity min-h-11 md:min-h-0 ${
                  TAG_COLORS[tag] || 'bg-border text-text-muted border-border'
                } ${selectedTags.includes(tag) ? 'opacity-100 ring-1 ring-accent' : 'opacity-50'}`}
              >
                {tag}
              </button>
            ))}
          </div>
          <Button type="submit" variant="primary" size="md" loading={submitting} className="w-full md:w-auto">
            Add to Watchlist
          </Button>
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
              className={`px-2.5 py-1 rounded-full text-xs border cursor-pointer transition-all min-h-11 md:min-h-0 ${
                TAG_COLORS[tag] || 'bg-border text-text-muted border-border'
              } ${activeTags.includes(tag) ? 'opacity-100 ring-1 ring-accent' : 'opacity-40 hover:opacity-70'}`}
            >
              {tag}
            </button>
          ))}
          {activeTags.length > 0 && (
            <Button variant="ghost" size="sm" onClick={() => setActiveTags([])} type="button" className="px-2 py-1">
              Clear
            </Button>
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
        <>
          {/* Mobile card layout */}
          <div className="sm:hidden space-y-2">
            {filteredEntries.map((entry) => (
              <div
                key={entry.symbol}
                className="bg-card border border-border rounded p-3"
              >
                {/* Header: symbol + name */}
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <span className="text-accent font-bold">{entry.symbol}</span>
                    <span className="text-text-muted text-sm ml-2">{entry.name || '-'}</span>
                  </div>
                </div>

                {/* Tags */}
                <div className="mb-2">
                  {editingSymbol === entry.symbol ? (
                    <div className="flex gap-1 flex-wrap items-center">
                      {allTags.map((tag) => (
                        <button
                          key={tag}
                          type="button"
                          onClick={() => handleEditTagToggle(tag)}
                          className={`px-1.5 py-0.5 rounded text-xs border cursor-pointer transition-opacity min-h-11 md:min-h-0 ${
                            TAG_COLORS[tag] || 'bg-border text-text-muted border-border'
                          } ${editTags.includes(tag) ? 'opacity-100 ring-1 ring-accent' : 'opacity-40'}`}
                        >
                          {tag}
                        </button>
                      ))}
                      <Button variant="ghost" size="sm" className="text-up hover:text-up/80 ml-1" onClick={() => handleSaveTags(entry.symbol)} type="button">
                        Save
                      </Button>
                      <Button variant="ghost" size="sm" onClick={() => { setEditingSymbol(null); setEditTags([]); }} type="button">
                        Cancel
                      </Button>
                    </div>
                  ) : (
                    <div className="flex gap-1 flex-wrap">
                      {entry.tags
                        ? entry.tags.split(',').map((tag) => (
                            <Badge key={tag} colorScheme={TAG_COLOR_MAP[tag] || 'gray'} className="px-1.5 py-0.5">
                              {tag}
                            </Badge>
                          ))
                        : <span className="text-text-dim text-xs">No tags</span>}
                    </div>
                  )}
                </div>

                {/* Price + change */}
                <div className="flex justify-between items-baseline mb-2">
                  <span className="text-text text-sm">
                    {entry.price != null ? formatEUR(entry.price) : <span className="text-text-dim">N/A</span>}
                  </span>
                  <span className={`text-sm ${
                    entry.change_24h > 0 ? 'text-up' : entry.change_24h < 0 ? 'text-down' : 'text-text-muted'
                  }`}>
                    {entry.change_24h != null ? formatPct(entry.change_24h) : <span className="text-text-dim">N/A</span>}
                  </span>
                </div>

                {/* Actions */}
                <div className="flex gap-2 pt-1 border-t border-border/30">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-accent hover:text-accent/80"
                    onClick={() => handleStartEditTags(entry)}
                    type="button"
                    title={`Edit tags for ${entry.symbol}`}
                  >
                    Edit Tags
                  </Button>
                  <Button
                    variant="danger"
                    size="sm"
                    onClick={() => handleRemove(entry.symbol)}
                    type="button"
                    title={`Remove ${entry.symbol} from watchlist`}
                  >
                    Remove
                  </Button>
                </div>
              </div>
            ))}
          </div>
          {/* Desktop table */}
          <div className="hidden sm:block overflow-x-auto">
            <Table className="max-w-4xl">
              <thead>
                <tr>
                  <Th>Symbol</Th>
                  <Th>Name</Th>
                  <Th>Tags</Th>
                  <Th align="right">Price (EUR)</Th>
                  <Th align="right">24h %</Th>
                  <Th align="right">Volume (EUR)</Th>
                  <Th align="center"></Th>
                </tr>
              </thead>
              <tbody>
                {filteredEntries.map((entry) => (
                  <tr key={entry.symbol} className="border-b border-border/50">
                    <Td className="text-accent font-bold">{entry.symbol}</Td>
                    <Td className="text-text-muted text-sm">{entry.name || '-'}</Td>
                    <Td>
                      {editingSymbol === entry.symbol ? (
                        <div className="flex gap-1 flex-wrap items-center">
                          {allTags.map((tag) => (
                            <button
                              key={tag}
                              type="button"
                              onClick={() => handleEditTagToggle(tag)}
                              className={`px-1.5 py-0.5 rounded text-xs border cursor-pointer transition-opacity min-h-11 md:min-h-0 ${
                                TAG_COLORS[tag] || 'bg-border text-text-muted border-border'
                              } ${editTags.includes(tag) ? 'opacity-100 ring-1 ring-accent' : 'opacity-40'}`}
                            >
                              {tag}
                            </button>
                          ))}
                          <Button variant="ghost" size="sm" className="text-up hover:text-up/80 ml-1" onClick={() => handleSaveTags(entry.symbol)} type="button">
                            Save
                          </Button>
                          <Button variant="ghost" size="sm" onClick={() => { setEditingSymbol(null); setEditTags([]); }} type="button">
                            Cancel
                          </Button>
                        </div>
                      ) : (
                        <div className="flex gap-1 flex-wrap">
                          {entry.tags
                            ? entry.tags.split(',').map((tag) => (
                                <Badge key={tag} colorScheme={TAG_COLOR_MAP[tag] || 'gray'} className="px-1.5 py-0.5">
                                  {tag}
                                </Badge>
                              ))
                            : <span className="text-text-dim text-xs">-</span>}
                        </div>
                      )}
                    </Td>
                    <Td align="right">
                      {entry.price != null ? formatEUR(entry.price) : <span className="text-text-dim">N/A</span>}
                    </Td>
                    <Td align="right" className={
                      entry.change_24h > 0 ? 'text-up' : entry.change_24h < 0 ? 'text-down' : 'text-text-muted'
                    }>
                      {entry.change_24h != null ? formatPct(entry.change_24h) : <span className="text-text-dim">N/A</span>}
                    </Td>
                    <Td align="right" className="text-text-muted">
                      {entry.volume_eur != null ? formatEURCompact(entry.volume_eur) : <span className="text-text-dim">N/A</span>}
                    </Td>
                    <Td align="center">
                      <div className="flex gap-2 justify-center">
                        <Button
                          variant="ghost"
                          size="sm"
                          className="text-accent hover:text-accent/80"
                          onClick={() => handleStartEditTags(entry)}
                          type="button"
                          title={`Edit tags for ${entry.symbol}`}
                        >
                          Edit Tags
                        </Button>
                        <Button
                          variant="danger"
                          size="sm"
                          onClick={() => handleRemove(entry.symbol)}
                          type="button"
                          title={`Remove ${entry.symbol} from watchlist`}
                        >
                          Remove
                        </Button>
                      </div>
                    </Td>
                  </tr>
                ))}
              </tbody>
            </Table>
          </div>
        </>
      )}
    </div>
  );
}

export default WatchlistPage;
