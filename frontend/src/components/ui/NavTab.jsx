import { NavLink } from 'react-router';

export function NavTab({ to, end, children }) {
  return (
    <NavLink
      to={to}
      end={end}
      className={({ isActive }) =>
        `px-4 py-1.5 rounded-t border text-sm ${
          isActive
            ? 'bg-card border-border-light text-text'
            : 'bg-border border-border text-text-muted hover:text-text'
        }`
      }
    >
      {children}
    </NavLink>
  );
}
