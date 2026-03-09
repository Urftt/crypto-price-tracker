import { useState } from 'react';
import { Routes, Route } from 'react-router';
import PricesPage from './pages/PricesPage';
import WatchlistPage from './pages/WatchlistPage';
import PortfolioPage from './pages/PortfolioPage';
import AlertsPage from './pages/AlertsPage';
import ExchangeDropdown from './components/ExchangeDropdown';
import OfflineBanner from './components/OfflineBanner';
import InstallButton from './components/InstallButton';
import { NavTab } from './components/ui/NavTab';

function App() {
  const [exchange, setExchange] = useState('bitvavo');

  return (
    <div className="min-h-screen bg-bg font-mono text-text">
      <OfflineBanner />
      <header className="p-5 flex items-center justify-between">
        <h1 className="text-accent text-2xl font-bold">Crypto Prices -- EUR</h1>
        <div className="flex items-center gap-3">
          <InstallButton />
          <ExchangeDropdown value={exchange} onChange={setExchange} />
        </div>
      </header>
      <nav className="flex gap-1 px-5 mb-4">
        <NavTab to="/" end>Prices</NavTab>
        <NavTab to="/watchlist">Watchlist</NavTab>
        <NavTab to="/portfolio">Portfolio</NavTab>
        <NavTab to="/alerts">Alerts</NavTab>
      </nav>
      <main className="px-5">
        <Routes>
          <Route index element={<PricesPage exchange={exchange} />} />
          <Route path="watchlist" element={<WatchlistPage />} />
          <Route path="portfolio" element={<PortfolioPage />} />
          <Route path="alerts" element={<AlertsPage />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
