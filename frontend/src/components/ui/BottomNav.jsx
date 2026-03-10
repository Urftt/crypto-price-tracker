import { NavLink } from 'react-router';

const tabs = [
  { to: '/', end: true, label: 'Prices' },
  { to: '/watchlist', label: 'Watchlist' },
  { to: '/portfolio', label: 'Portfolio' },
  { to: '/alerts', label: 'Alerts' },
];

export function BottomNav() {
  return (
    <nav className="fixed bottom-0 left-0 right-0 z-30 bg-card border-t border-border flex md:hidden">
      {tabs.map((tab) => (
        <NavLink
          key={tab.to}
          to={tab.to}
          end={tab.end}
          className={({ isActive }) =>
            `flex-1 flex items-center justify-center min-h-11 py-3 text-xs font-medium transition-colors ${
              isActive
                ? 'text-accent border-t-2 border-accent -mt-px'
                : 'text-text-muted hover:text-text'
            }`
          }
        >
          {tab.label}
        </NavLink>
      ))}
    </nav>
  );
}
