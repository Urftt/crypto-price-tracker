import { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router';
import { useApi } from '../hooks/useApi';
import AddAlertForm from '../components/AddAlertForm';
import AlertList from '../components/AlertList';

function AlertsPage() {
  const api = useApi();
  const [searchParams, setSearchParams] = useSearchParams();
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  // Read symbol from URL query param (from CoinModal "Set Alert" button)
  const defaultSymbol = searchParams.get('symbol') || '';

  // Clear the search param after reading it
  useEffect(() => {
    if (searchParams.has('symbol')) {
      setSearchParams({}, { replace: true });
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const loadAlerts = useCallback(async () => {
    try {
      const data = await api.get('/api/alerts');
      setAlerts(data);
    } catch {
      // Keep previous state on error
    }
    setLoading(false);
  }, [api]);

  useEffect(() => {
    loadAlerts();
  }, [loadAlerts]);

  const handleRemove = async (alertId) => {
    try {
      await api.del(`/api/alerts/${alertId}`);
      loadAlerts();
    } catch {
      // Ignore
    }
  };

  const handleClearTriggered = async () => {
    try {
      await api.del('/api/alerts/triggered');
      loadAlerts();
    } catch {
      // Ignore
    }
  };

  const activeAlerts = alerts.filter((a) => a.status === 'active');
  const triggeredAlerts = alerts.filter((a) => a.status === 'triggered');

  if (loading) {
    return <p className="text-text-muted text-sm">Loading alerts...</p>;
  }

  return (
    <div>
      <h2 className="text-lg font-bold text-text mb-4">Price Alerts</h2>
      <AddAlertForm defaultSymbol={defaultSymbol} onAdded={loadAlerts} />
      <div className="mt-6">
        <h3 className="text-sm font-bold text-text-muted uppercase mb-2">Active Alerts</h3>
        <AlertList alerts={activeAlerts} title="Active alerts" onRemove={handleRemove} />
      </div>
      <div className="mt-6">
        <div className="flex items-center justify-between mb-2 max-w-4xl">
          <h3 className="text-sm font-bold text-text-muted uppercase">Triggered Alerts</h3>
          {triggeredAlerts.length > 0 && (
            <button
              onClick={handleClearTriggered}
              className="text-down text-xs hover:text-down/80 cursor-pointer"
            >
              Clear All
            </button>
          )}
        </div>
        <AlertList alerts={triggeredAlerts} title="Triggered alerts" onRemove={handleRemove} />
      </div>
    </div>
  );
}

export default AlertsPage;
