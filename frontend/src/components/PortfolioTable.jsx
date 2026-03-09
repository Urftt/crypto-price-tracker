import { useState } from 'react';
import { useApi } from '../hooks/useApi';
import { formatEUR, formatPct } from '../lib/format';
import { Table, Th, Td } from './ui/Table';
import { Button } from './ui/Button';

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
      <Table>
        <thead>
          <tr>
            <Th>Symbol</Th>
            <Th align="right">Amount</Th>
            <Th align="right">Avg Buy</Th>
            <Th align="right">Current</Th>
            <Th align="right">Value</Th>
            <Th align="right">P&L EUR</Th>
            <Th align="right">P&L %</Th>
            <Th align="right">Alloc %</Th>
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
                <Td className="text-accent font-bold">
                  {row.symbol}
                  <span className="text-text-dim text-xs ml-1">({row.num_lots} lot{row.num_lots !== 1 ? 's' : ''})</span>
                </Td>
                <Td align="right" className="text-sm">{row.total_amount}</Td>
                <Td align="right" className="text-sm">{formatEUR(row.avg_buy_price)}</Td>
                <Td align="right" className="text-sm">{row.current_price != null ? formatEUR(row.current_price) : 'N/A'}</Td>
                <Td align="right" className="text-sm">{row.current_value != null ? formatEUR(row.current_value) : 'N/A'}</Td>
                <Td align="right" className={`text-sm ${row.pnl_eur != null ? pnlColor(row.pnl_eur) : 'text-text-dim'}`}>{row.pnl_eur != null ? formatEUR(row.pnl_eur) : 'N/A'}</Td>
                <Td align="right" className={`text-sm ${row.pnl_pct != null ? pnlColor(row.pnl_pct) : 'text-text-dim'}`}>{row.pnl_pct != null ? formatPct(row.pnl_pct) : 'N/A'}</Td>
                <Td align="right" className="text-sm">{row.allocation_pct != null ? `${row.allocation_pct.toFixed(1)}%` : 'N/A'}</Td>
              </tr>
              {expandedSymbol === row.symbol && (
                lotsLoading ? (
                  <tr key={`${row.symbol}-loading`}>
                    <Td colSpan={8} className="py-1 px-6 text-text-dim text-xs">Loading lots...</Td>
                  </tr>
                ) : (
                  lots.map((lot) => (
                    <tr key={`lot-${lot.id}`} className="bg-bg/50 border-b border-border/30">
                      <Td className="py-1 px-6 text-text-dim text-xs">Lot #{lot.id}</Td>
                      <Td align="right" className="py-1 text-text-muted text-xs">
                        {editingLotId === lot.id ? (
                          <input
                            type="number"
                            step="any"
                            value={editAmount}
                            onChange={(e) => setEditAmount(e.target.value)}
                            onKeyDown={(e) => { if (e.key === 'Enter') handleEditLot(lot.id); if (e.key === 'Escape') { setEditingLotId(null); setEditAmount(''); } }}
                            onClick={(e) => e.stopPropagation()}
                            aria-label="Edit amount"
                            className="bg-bg border border-border rounded px-1 py-0.5 text-text text-xs w-20 focus:border-accent focus:outline-none"
                            autoFocus
                          />
                        ) : lot.amount}
                      </Td>
                      <Td align="right" className="py-1 text-text-muted text-xs">{formatEUR(lot.buy_price)}</Td>
                      <Td align="right" className="py-1 text-text-muted text-xs">{lot.buy_date || '--'}</Td>
                      <Td colSpan={3}></Td>
                      <Td align="right" className="py-1">
                        <div className="flex gap-2 justify-end">
                          {editingLotId === lot.id ? (
                            <>
                              <Button variant="ghost" size="sm" className="text-up hover:text-up/80" onClick={(e) => { e.stopPropagation(); handleEditLot(lot.id); }} type="button">
                                Save
                              </Button>
                              <Button variant="ghost" size="sm" onClick={(e) => { e.stopPropagation(); setEditingLotId(null); setEditAmount(''); }} type="button">
                                Cancel
                              </Button>
                            </>
                          ) : (
                            <>
                              <Button variant="ghost" size="sm" className="text-accent hover:text-accent/80" onClick={(e) => { e.stopPropagation(); setEditingLotId(lot.id); setEditAmount(String(lot.amount)); }} type="button">
                                Edit
                              </Button>
                              <Button variant="danger" size="sm" onClick={(e) => { e.stopPropagation(); handleDeleteLot(lot.id); }} type="button">
                                Delete
                              </Button>
                            </>
                          )}
                        </div>
                      </Td>
                    </tr>
                  ))
                )
              )}
            </>
          ))}
        </tbody>
      </Table>
    </div>
  );
}

export default PortfolioTable;
