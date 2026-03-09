import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Button } from '../Button';

describe('Button', () => {
  it('renders children text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('applies primary variant classes by default', () => {
    render(<Button>Primary</Button>);
    const button = screen.getByText('Primary');
    expect(button.className).toContain('bg-accent');
    expect(button.className).toContain('text-bg');
    expect(button.className).toContain('font-bold');
  });

  it('applies danger variant classes when variant="danger"', () => {
    render(<Button variant="danger">Delete</Button>);
    const button = screen.getByText('Delete');
    expect(button.className).toContain('text-down');
  });

  it('applies ghost variant classes when variant="ghost"', () => {
    render(<Button variant="ghost">Ghost</Button>);
    const button = screen.getByText('Ghost');
    expect(button.className).toContain('text-text-muted');
  });

  it('applies secondary variant classes when variant="secondary"', () => {
    render(<Button variant="secondary">Secondary</Button>);
    const button = screen.getByText('Secondary');
    expect(button.className).toContain('bg-card');
  });

  it('applies md size classes by default', () => {
    render(<Button>Default Size</Button>);
    const button = screen.getByText('Default Size');
    expect(button.className).toContain('px-4');
    expect(button.className).toContain('py-1.5');
    expect(button.className).toContain('text-sm');
  });

  it('applies sm size classes when size="sm"', () => {
    render(<Button size="sm">Small</Button>);
    const button = screen.getByText('Small');
    expect(button.className).toContain('px-2.5');
    expect(button.className).toContain('py-0.5');
    expect(button.className).toContain('text-xs');
  });

  it('applies xs size classes when size="xs"', () => {
    render(<Button size="xs">Tiny</Button>);
    const button = screen.getByText('Tiny');
    expect(button.className).toContain('px-1');
    expect(button.className).toContain('py-0.5');
    expect(button.className).toContain('text-xs');
  });

  it('shows "Submitting..." and is disabled when loading=true', () => {
    render(<Button loading>Save</Button>);
    const button = screen.getByText('Submitting...');
    expect(button).toBeDisabled();
    expect(screen.queryByText('Save')).not.toBeInTheDocument();
  });

  it('does NOT set a type attribute by default', () => {
    const { container } = render(<Button>No Type</Button>);
    const button = container.querySelector('button');
    expect(button.getAttribute('type')).toBeNull();
  });

  it('passes type="submit" through when explicitly set', () => {
    const { container } = render(<Button type="submit">Submit</Button>);
    const button = container.querySelector('button');
    expect(button.getAttribute('type')).toBe('submit');
  });

  it('passes type="button" through when explicitly set', () => {
    const { container } = render(<Button type="button">Click</Button>);
    const button = container.querySelector('button');
    expect(button.getAttribute('type')).toBe('button');
  });

  it('appends custom className', () => {
    render(<Button className="mt-4">Styled</Button>);
    const button = screen.getByText('Styled');
    expect(button.className).toContain('mt-4');
  });

  it('applies disabled:opacity-50 class when disabled', () => {
    render(<Button disabled>Disabled</Button>);
    const button = screen.getByText('Disabled');
    expect(button.className).toContain('disabled:opacity-50');
    expect(button).toBeDisabled();
  });
});
