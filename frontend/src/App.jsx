import { useState } from 'react';
import { Routes, Route, useLocation } from 'react-router';
import PricesPage from './pages/PricesPage';
import WatchlistPage from './pages/WatchlistPage';
import PortfolioPage from './pages/PortfolioPage';
import AlertsPage from './pages/AlertsPage';
import ExchangeDropdown from './components/ExchangeDropdown';
import OfflineBanner from './components/OfflineBanner';
import InstallButton from './components/InstallButton';
import { NavTab } from './components/ui/NavTab';
import { BottomNav } from './components/ui/BottomNav';

function App() {
  const [exchange, setExchange] = useState('bitvavo');
  const location = useLocation();

  return (
    <div className="min-h-screen bg-bg font-mono text-text">
      <OfflineBanner />
      <header className="p-5 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <h1 className="text-accent text-2xl font-bold">Crypto Prices -- EUR</h1>
        <div className="flex items-center gap-3">
          <InstallButton />
          <ExchangeDropdown value={exchange} onChange={setExchange} />
        </div>
      </header>
      <nav className="hidden md:flex gap-1 px-5 mb-4">
        <NavTab to="/" end>Prices</NavTab>
        <NavTab to="/watchlist">Watchlist</NavTab>
        <NavTab to="/portfolio">Portfolio</NavTab>
        <NavTab to="/alerts">Alerts</NavTab>
      </nav>
      <main className="px-5 pb-20 md:pb-0">
        <div key={location.pathname} className="animate-fade-in">
          <Routes location={location}>
            <Route index element={<PricesPage exchange={exchange} />} />
            <Route path="watchlist" element={<WatchlistPage />} />
            <Route path="portfolio" element={<PortfolioPage />} />
            <Route path="alerts" element={<AlertsPage />} />
          </Routes>
        </div>
      </main>
      <BottomNav />
    </div>
  );
}

export default App;
