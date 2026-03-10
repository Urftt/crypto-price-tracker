import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { EmptyState } from '../EmptyState';

describe('EmptyState', () => {
  it('renders the title', () => {
    render(<EmptyState title="No items" />);
    expect(screen.getByText('No items')).toBeInTheDocument();
  });

  it('renders description when provided', () => {
    render(<EmptyState title="Empty" description="Add items to get started." />);
    expect(screen.getByText('Add items to get started.')).toBeInTheDocument();
  });

  it('does not render description paragraph when omitted', () => {
    const { container } = render(<EmptyState title="Empty" />);
    const paragraphs = container.querySelectorAll('p');
    expect(paragraphs).toHaveLength(1);
  });

  it('applies custom className to wrapper', () => {
    const { container } = render(<EmptyState title="Empty" className="max-w-4xl" />);
    expect(container.firstChild.className).toContain('max-w-4xl');
    expect(container.firstChild.className).toContain('text-center');
    expect(container.firstChild.className).toContain('py-8');
  });
});
