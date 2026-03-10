import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Skeleton } from '../Skeleton';

describe('Skeleton', () => {
  it('renders a div with animate-pulse class', () => {
    render(<Skeleton data-testid="skel" />);
    const el = screen.getByTestId('skel');
    expect(el.className).toContain('animate-pulse');
    expect(el.className).toContain('bg-border');
    expect(el.className).toContain('rounded');
  });

  it('appends custom className', () => {
    render(<Skeleton className="h-4 w-16" data-testid="skel" />);
    const el = screen.getByTestId('skel');
    expect(el.className).toContain('h-4');
    expect(el.className).toContain('w-16');
    expect(el.className).toContain('animate-pulse');
  });

  it('passes through additional props', () => {
    render(<Skeleton data-testid="skel" aria-hidden="true" />);
    const el = screen.getByTestId('skel');
    expect(el).toHaveAttribute('aria-hidden', 'true');
  });
});
