import { useState, useEffect, useRef, useCallback } from 'react';
import { useSSE } from '../hooks/useSSE';
import { formatEUR } from '../lib/format';
import PriceTable from '../components/PriceTable';
import CountdownTimer from '../components/CountdownTimer';
import CoinModal from '../components/CoinModal';
import Toast from '../components/Toast';
import { ErrorBoundary } from '../components/ErrorBoundary';
import { Button } from '../components/ui/Button';

let toastIdCounter = 0;

function PricesPage({ exchange }) {
  const sseUrl = `/api/prices/stream?exchange=${exchange}`;
  const { data: sseData } = useSSE(sseUrl);
  const [prices, setPrices] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [selectedCoin, setSelectedCoin] = useState(null);
  const [toasts, setToasts] = useState([]);
  const seenAlertIds = useRef(new Set());

  // SSE updates
  useEffect(() => {
    if (sseData) {
      setPrices(sseData);
      setLastUpdate(new Date());

      // Check for triggered alerts and create toasts
      if (sseData.triggered_alerts && sseData.triggered_alerts.length > 0) {
        const newToasts = [];
        for (const alert of sseData.triggered_alerts) {
          if (!seenAlertIds.current.has(alert.id)) {
            seenAlertIds.current.add(alert.id);
            newToasts.push({
              id: ++toastIdCounter,
              message: `Alert triggered: ${alert.symbol} ${alert.direction} ${formatEUR(alert.target_price)}`,
              type: 'success',
            });
          }
        }
        if (newToasts.length > 0) {
          setToasts((prev) => [...prev, ...newToasts]);
        }
      }
    }
  }, [sseData]);

  const removeToast = useCallback((toastId) => {
    setToasts((prev) => prev.filter((t) => t.id !== toastId));
  }, []);

  // Manual refresh
  const handleRefresh = async () => {
    const res = await fetch(`/api/prices?exchange=${exchange}`);
    const data = await res.json();
    setPrices(data);
    setLastUpdate(new Date());
  };

  return (
    <div>
      <div className="flex flex-wrap items-center gap-2 text-text-dim text-xs mb-4">
        <CountdownTimer lastUpdate={lastUpdate} interval={10} />
        <Button variant="secondary" size="sm" onClick={handleRefresh} type="button" className="bg-border border-border-light hover:border-accent hover:text-accent">
          Refresh
        </Button>
        {prices?.exchange && (
          <span className="text-text-muted">via {prices.exchange}</span>
        )}
      </div>
      {prices && <ErrorBoundary><PriceTable coins={prices.coins} onSelectCoin={setSelectedCoin} /></ErrorBoundary>}
      <CoinModal coin={selectedCoin} open={!!selectedCoin} onClose={() => setSelectedCoin(null)} />
      {toasts.map((toast, index) => (
        <Toast
          key={toast.id}
          message={toast.message}
          type={toast.type}
          onClose={() => removeToast(toast.id)}
          style={{ top: `${1 + index * 4}rem` }}
        />
      ))}
    </div>
  );
}

export default PricesPage;
