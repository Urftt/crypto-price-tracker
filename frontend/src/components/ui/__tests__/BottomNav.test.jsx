import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router';
import { describe, it, expect } from 'vitest';
import { BottomNav } from '../BottomNav';

describe('BottomNav', () => {
  it('renders 4 navigation links', () => {
    render(<MemoryRouter><BottomNav /></MemoryRouter>);
    expect(screen.getByText('Prices')).toBeInTheDocument();
    expect(screen.getByText('Watchlist')).toBeInTheDocument();
    expect(screen.getByText('Portfolio')).toBeInTheDocument();
    expect(screen.getByText('Alerts')).toBeInTheDocument();
  });

  it('renders all links as anchor elements', () => {
    render(<MemoryRouter><BottomNav /></MemoryRouter>);
    const links = screen.getAllByRole('link');
    expect(links).toHaveLength(4);
  });

  it('has md:hidden class for mobile-only display', () => {
    const { container } = render(<MemoryRouter><BottomNav /></MemoryRouter>);
    const nav = container.querySelector('nav');
    expect(nav.className).toContain('md:hidden');
  });

  it('has fixed positioning classes', () => {
    const { container } = render(<MemoryRouter><BottomNav /></MemoryRouter>);
    const nav = container.querySelector('nav');
    expect(nav.className).toContain('fixed');
    expect(nav.className).toContain('bottom-0');
  });

  it('links have min-h-11 for 44px touch targets', () => {
    render(<MemoryRouter><BottomNav /></MemoryRouter>);
    const links = screen.getAllByRole('link');
    links.forEach((link) => {
      expect(link.className).toContain('min-h-11');
    });
  });
});
