import { useState, useEffect } from 'react';
import { useSSE } from '../hooks/useSSE';
import PriceTable from '../components/PriceTable';
import CountdownTimer from '../components/CountdownTimer';
import CoinModal from '../components/CoinModal';

function PricesPage() {
  const { data: sseData } = useSSE('/api/prices/stream');
  const [prices, setPrices] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [selectedCoin, setSelectedCoin] = useState(null);

  // SSE updates
  useEffect(() => {
    if (sseData) {
      setPrices(sseData);
      setLastUpdate(new Date());
    }
  }, [sseData]);

  // Manual refresh
  const handleRefresh = async () => {
    const res = await fetch('/api/prices');
    const data = await res.json();
    setPrices(data);
    setLastUpdate(new Date());
  };

  return (
    <div>
      <div className="flex items-center gap-2 text-text-dim text-xs mb-4">
        <CountdownTimer lastUpdate={lastUpdate} interval={10} />
        <button
          onClick={handleRefresh}
          className="bg-border border border-border-light rounded px-2.5 py-0.5 text-text hover:border-accent hover:text-accent text-xs cursor-pointer"
        >
          Refresh
        </button>
      </div>
      {prices && <PriceTable coins={prices.coins} onSelectCoin={setSelectedCoin} />}
      {selectedCoin && <CoinModal coin={selectedCoin} onClose={() => setSelectedCoin(null)} />}
    </div>
  );
}

export default PricesPage;
