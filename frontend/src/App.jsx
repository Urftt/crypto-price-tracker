import { useState } from 'react';
import { Routes, Route, NavLink } from 'react-router';
import PricesPage from './pages/PricesPage';
import PortfolioPage from './pages/PortfolioPage';
import AlertsPage from './pages/AlertsPage';
import ExchangeDropdown from './components/ExchangeDropdown';

function App() {
  const [exchange, setExchange] = useState('bitvavo');

  return (
    <div className="min-h-screen bg-bg font-mono text-text">
      <header className="p-5 flex items-center justify-between">
        <h1 className="text-accent text-2xl font-bold">Crypto Prices -- EUR</h1>
        <ExchangeDropdown value={exchange} onChange={setExchange} />
      </header>
      <nav className="flex gap-1 px-5 mb-4">
        <NavLink to="/" end className={({isActive}) => `px-4 py-1.5 rounded-t border text-sm ${isActive ? 'bg-card border-border-light text-text' : 'bg-border border-border text-text-muted hover:text-text'}`}>Prices</NavLink>
        <NavLink to="/portfolio" className={({isActive}) => `px-4 py-1.5 rounded-t border text-sm ${isActive ? 'bg-card border-border-light text-text' : 'bg-border border-border text-text-muted hover:text-text'}`}>Portfolio</NavLink>
        <NavLink to="/alerts" className={({isActive}) => `px-4 py-1.5 rounded-t border text-sm ${isActive ? 'bg-card border-border-light text-text' : 'bg-border border-border text-text-muted hover:text-text'}`}>Alerts</NavLink>
      </nav>
      <main className="px-5">
        <Routes>
          <Route index element={<PricesPage exchange={exchange} />} />
          <Route path="portfolio" element={<PortfolioPage />} />
          <Route path="alerts" element={<AlertsPage />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
