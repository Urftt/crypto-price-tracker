import { useState } from 'react';
import { useApi } from '../hooks/useApi';
import { formatEUR, formatPct } from '../lib/format';

function PortfolioTable({ rows, onDelete }) {
  const api = useApi();
  const [expandedSymbol, setExpandedSymbol] = useState(null);
  const [lots, setLots] = useState([]);
  const [lotsLoading, setLotsLoading] = useState(false);
  const [editingLotId, setEditingLotId] = useState(null);
  const [editAmount, setEditAmount] = useState('');

  const toggleLots = async (symbol) => {
    if (expandedSymbol === symbol) {
      setExpandedSymbol(null);
      setLots([]);
      return;
    }
    setExpandedSymbol(symbol);
    setLotsLoading(true);
    try {
      const data = await api.get(`/api/portfolio/lots/${symbol}`);
      setLots(data);
    } catch {
      setLots([]);
    }
    setLotsLoading(false);
  };

  const handleDeleteLot = async (lotId) => {
    try {
      await api.del(`/api/portfolio/${lotId}`);
      onDelete();
      // Refresh lots for the expanded symbol
      if (expandedSymbol) {
        const data = await api.get(`/api/portfolio/lots/${expandedSymbol}`);
        setLots(data);
        if (data.length === 0) {
          setExpandedSymbol(null);
        }
      }
    } catch {
      // Ignore delete errors silently
    }
  };

  const handleEditLot = async (lotId) => {
    const amount = parseFloat(editAmount);
    if (isNaN(amount) || amount <= 0) return;
    try {
      await api.put(`/api/portfolio/${lotId}`, { amount });
      setEditingLotId(null);
      setEditAmount('');
      onDelete(); // refresh portfolio
      if (expandedSymbol) {
        const data = await api.get(`/api/portfolio/lots/${expandedSymbol}`);
        setLots(data);
      }
    } catch {
      // Ignore edit errors
    }
  };

  if (!rows || rows.length === 0) {
    return <p className="text-text-muted text-sm max-w-4xl">No holdings yet. Add one above.</p>;
  }

  const pnlColor = (val) => val > 0 ? 'text-up' : val < 0 ? 'text-down' : 'text-text-muted';

  return (
    <div className="max-w-4xl overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr>
            <th className="text-text-muted text-left text-xs uppercase py-1.5 px-3 border-b border-border">Symbol</th>
            <th className="text-text-muted text-right text-xs uppercase py-1.5 px-3 border-b border-border">Amount</th>
            <th className="text-text-muted text-right text-xs uppercase py-1.5 px-3 border-b border-border">Avg Buy</th>
            <th className="text-text-muted text-right text-xs uppercase py-1.5 px-3 border-b border-border">Current</th>
            <th className="text-text-muted text-right text-xs uppercase py-1.5 px-3 border-b border-border">Value</th>
            <th className="text-text-muted text-right text-xs uppercase py-1.5 px-3 border-b border-border">P&L EUR</th>
            <th className="text-text-muted text-right text-xs uppercase py-1.5 px-3 border-b border-border">P&L %</th>
            <th className="text-text-muted text-right text-xs uppercase py-1.5 px-3 border-b border-border">Alloc %</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <>
              <tr
                key={row.symbol}
                onClick={() => toggleLots(row.symbol)}
                className="cursor-pointer hover:bg-card border-b border-border/50"
              >
                <td className="py-1.5 px-3 text-accent font-bold">
                  {row.symbol}
                  <span className="text-text-dim text-xs ml-1">({row.num_lots} lot{row.num_lots !== 1 ? 's' : ''})</span>
                </td>
                <td className="py-1.5 px-3 text-right text-sm">{row.total_amount}</td>
                <td className="py-1.5 px-3 text-right text-sm">{formatEUR(row.avg_buy_price)}</td>
                <td className="py-1.5 px-3 text-right text-sm">{row.current_price != null ? formatEUR(row.current_price) : 'N/A'}</td>
                <td className="py-1.5 px-3 text-right text-sm">{row.current_value != null ? formatEUR(row.current_value) : 'N/A'}</td>
                <td className={`py-1.5 px-3 text-right text-sm ${row.pnl_eur != null ? pnlColor(row.pnl_eur) : 'text-text-dim'}`}>{row.pnl_eur != null ? formatEUR(row.pnl_eur) : 'N/A'}</td>
                <td className={`py-1.5 px-3 text-right text-sm ${row.pnl_pct != null ? pnlColor(row.pnl_pct) : 'text-text-dim'}`}>{row.pnl_pct != null ? formatPct(row.pnl_pct) : 'N/A'}</td>
                <td className="py-1.5 px-3 text-right text-sm">{row.allocation_pct != null ? `${row.allocation_pct.toFixed(1)}%` : 'N/A'}</td>
              </tr>
              {expandedSymbol === row.symbol && (
                lotsLoading ? (
                  <tr key={`${row.symbol}-loading`}>
                    <td colSpan={8} className="py-1 px-6 text-text-dim text-xs">Loading lots...</td>
                  </tr>
                ) : (
                  lots.map((lot) => (
                    <tr key={`lot-${lot.id}`} className="bg-bg/50 border-b border-border/30">
                      <td className="py-1 px-6 text-text-dim text-xs">Lot #{lot.id}</td>
                      <td className="py-1 px-3 text-right text-text-muted text-xs">
                        {editingLotId === lot.id ? (
                          <input
                            type="number"
                            step="any"
                            value={editAmount}
                            onChange={(e) => setEditAmount(e.target.value)}
                            onKeyDown={(e) => { if (e.key === 'Enter') handleEditLot(lot.id); if (e.key === 'Escape') { setEditingLotId(null); setEditAmount(''); } }}
                            onClick={(e) => e.stopPropagation()}
                            className="bg-bg border border-border rounded px-1 py-0.5 text-text text-xs w-20 focus:border-accent focus:outline-none"
                            autoFocus
                          />
                        ) : lot.amount}
                      </td>
                      <td className="py-1 px-3 text-right text-text-muted text-xs">{formatEUR(lot.buy_price)}</td>
                      <td className="py-1 px-3 text-right text-text-muted text-xs">{lot.buy_date || '--'}</td>
                      <td colSpan={3}></td>
                      <td className="py-1 px-3 text-right">
                        <div className="flex gap-2 justify-end">
                          {editingLotId === lot.id ? (
                            <>
                              <button
                                onClick={(e) => { e.stopPropagation(); handleEditLot(lot.id); }}
                                className="text-up hover:text-up/80 text-xs cursor-pointer"
                              >
                                Save
                              </button>
                              <button
                                onClick={(e) => { e.stopPropagation(); setEditingLotId(null); setEditAmount(''); }}
                                className="text-text-muted hover:text-text text-xs cursor-pointer"
                              >
                                Cancel
                              </button>
                            </>
                          ) : (
                            <>
                              <button
                                onClick={(e) => { e.stopPropagation(); setEditingLotId(lot.id); setEditAmount(String(lot.amount)); }}
                                className="text-accent hover:text-accent/80 text-xs cursor-pointer"
                              >
                                Edit
                              </button>
                              <button
                                onClick={(e) => { e.stopPropagation(); handleDeleteLot(lot.id); }}
                                className="text-down hover:text-down/80 text-xs cursor-pointer"
                              >
                                Delete
                              </button>
                            </>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))
                )
              )}
            </>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default PortfolioTable;
