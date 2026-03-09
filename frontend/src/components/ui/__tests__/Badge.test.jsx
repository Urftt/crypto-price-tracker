import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Badge } from '../Badge';

describe('Badge', () => {
  it('renders children text', () => {
    render(<Badge>Active</Badge>);
    expect(screen.getByText('Active')).toBeInTheDocument();
  });

  it('applies blue colorScheme classes', () => {
    render(<Badge colorScheme="blue">Tag</Badge>);
    const badge = screen.getByText('Tag');
    expect(badge.className).toContain('bg-blue-900/50');
    expect(badge.className).toContain('text-blue-300');
    expect(badge.className).toContain('border-blue-700');
  });

  it('applies up variant classes', () => {
    render(<Badge variant="up">+5%</Badge>);
    const badge = screen.getByText('+5%');
    expect(badge.className).toContain('text-up');
    expect(badge.className).toContain('bg-up/10');
  });

  it('applies down variant classes', () => {
    render(<Badge variant="down">-3%</Badge>);
    const badge = screen.getByText('-3%');
    expect(badge.className).toContain('text-down');
    expect(badge.className).toContain('bg-down/10');
  });

  it('has border class when using colorScheme', () => {
    render(<Badge colorScheme="green">Label</Badge>);
    const badge = screen.getByText('Label');
    expect(badge.className).toContain('border');
  });

  it('falls back to gray colorScheme when neither colorScheme nor variant provided', () => {
    render(<Badge>Default</Badge>);
    const badge = screen.getByText('Default');
    expect(badge.className).toContain('bg-border');
    expect(badge.className).toContain('text-text-muted');
    expect(badge.className).toContain('border-border');
    expect(badge.className).toContain('border');
  });

  it('appends custom className', () => {
    render(<Badge className="ml-2">Styled</Badge>);
    const badge = screen.getByText('Styled');
    expect(badge.className).toContain('ml-2');
  });
});
