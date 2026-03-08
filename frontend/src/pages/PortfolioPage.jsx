import { useState, useEffect, useCallback } from 'react';
import { useApi } from '../hooks/useApi';
import { formatEUR, formatPct } from '../lib/format';
import AddHoldingForm from '../components/AddHoldingForm';
import DownloadReport from '../components/DownloadReport';
import PortfolioTable from '../components/PortfolioTable';

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
    return <p className="text-text-muted text-sm">Loading portfolio...</p>;
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-bold text-text">Portfolio</h2>
        <DownloadReport />
      </div>
      <AddHoldingForm onAdded={loadPortfolio} />
      <PortfolioTable rows={portfolio.rows} onDelete={loadPortfolio} />
      {portfolio.rows.length > 0 && (
        <div className="max-w-4xl mt-4 p-3 bg-card border border-border rounded flex justify-between text-sm">
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
