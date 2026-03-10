import { useState, useEffect, useCallback } from 'react';
import { useApi } from '../hooks/useApi';
import { formatEUR, formatPct } from '../lib/format';
import AddHoldingForm from '../components/AddHoldingForm';
import DownloadReport from '../components/DownloadReport';
import PortfolioTable from '../components/PortfolioTable';
import { Skeleton } from '../components/ui/Skeleton';
import { Table, Th, Td } from '../components/ui/Table';

function PortfolioPage() {
  const api = useApi();
  const [portfolio, setPortfolio] = useState({ rows: [], total_value: 0, total_cost: 0, total_pnl_eur: 0, total_pnl_pct: 0 });
  const [loading, setLoading] = useState(true);

  const loadPortfolio = useCallback(async () => {
    try {
      const data = await api.get('/api/portfolio');
      setPortfolio(data);
    } catch {
      // Keep previous state on error
    }
    setLoading(false);
  }, [api]);

  useEffect(() => {
    loadPortfolio();
  }, [loadPortfolio]);

  if (loading) {
    return (
      <div>
        {/* Mobile card skeletons */}
        <div className="sm:hidden space-y-2">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="bg-card border border-border rounded p-3">
              <div className="flex justify-between mb-2">
                <Skeleton className="h-4 w-12" />
                <Skeleton className="h-4 w-16" />
              </div>
              <div className="flex justify-between">
                <Skeleton className="h-5 w-20" />
                <Skeleton className="h-4 w-14" />
              </div>
            </div>
          ))}
        </div>
        {/* Desktop table skeletons */}
        <div className="hidden sm:block max-w-4xl overflow-x-auto">
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
              {[...Array(5)].map((_, i) => (
                <tr key={i} className="border-b border-border/50">
                  <Td><Skeleton className="h-4 w-12" /></Td>
                  <Td align="right"><Skeleton className="h-4 w-10" /></Td>
                  <Td align="right"><Skeleton className="h-4 w-16" /></Td>
                  <Td align="right"><Skeleton className="h-4 w-16" /></Td>
                  <Td align="right"><Skeleton className="h-4 w-16" /></Td>
                  <Td align="right"><Skeleton className="h-4 w-14" /></Td>
                  <Td align="right"><Skeleton className="h-4 w-10" /></Td>
                  <Td align="right"><Skeleton className="h-4 w-10" /></Td>
                </tr>
              ))}
            </tbody>
          </Table>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex flex-wrap items-center justify-between gap-2 mb-4">
        <h2 className="text-lg font-bold text-text">Portfolio</h2>
        <DownloadReport />
      </div>
      <AddHoldingForm onAdded={loadPortfolio} />
      <PortfolioTable rows={portfolio.rows} onDelete={loadPortfolio} />
      {portfolio.rows.length > 0 && (
        <div className="max-w-4xl mt-6 p-3 bg-card border border-border rounded flex flex-col gap-2 text-sm sm:flex-row sm:justify-between">
          <span>
            Total Value: <span className="text-accent font-bold">{formatEUR(portfolio.total_value)}</span>
          </span>
          <span>
            Total P&L:{' '}
            <span className={portfolio.total_pnl_eur >= 0 ? 'text-up' : 'text-down'}>
              {formatEUR(portfolio.total_pnl_eur)} ({formatPct(portfolio.total_pnl_pct)})
            </span>
          </span>
        </div>
      )}
    </div>
  );
}

export default PortfolioPage;
