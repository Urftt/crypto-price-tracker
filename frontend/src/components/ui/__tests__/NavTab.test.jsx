import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { MemoryRouter } from 'react-router';
import { NavTab } from '../NavTab';

describe('NavTab', () => {
  it('renders an anchor element with correct text', () => {
    render(
      <MemoryRouter>
        <NavTab to="/prices">Prices</NavTab>
      </MemoryRouter>
    );
    const link = screen.getByText('Prices');
    expect(link).toBeInTheDocument();
    expect(link.tagName).toBe('A');
  });

  it('passes to prop to NavLink', () => {
    render(
      <MemoryRouter>
        <NavTab to="/portfolio">Portfolio</NavTab>
      </MemoryRouter>
    );
    const link = screen.getByText('Portfolio');
    expect(link.getAttribute('href')).toBe('/portfolio');
  });

  it('passes end prop to NavLink when provided', () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <NavTab to="/" end>Home</NavTab>
        <NavTab to="/other">Other</NavTab>
      </MemoryRouter>
    );
    // With end prop on "/" and current route "/", only Home should be active
    const homeLink = screen.getByText('Home');
    expect(homeLink.className).toContain('bg-card');
    expect(homeLink.className).toContain('border-border-light');

    const otherLink = screen.getByText('Other');
    expect(otherLink.className).toContain('bg-border');
    expect(otherLink.className).toContain('text-text-muted');
  });
});
