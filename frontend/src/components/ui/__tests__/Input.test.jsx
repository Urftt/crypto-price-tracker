import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { Input } from '../Input';

describe('Input', () => {
  it('renders a visible label when label prop provided', () => {
    render(<Input label="Symbol" />);
    expect(screen.getByText('Symbol')).toBeInTheDocument();
  });

  it('links label to input via htmlFor/id (auto-generated from label text)', () => {
    render(<Input label="Symbol" />);
    const input = screen.getByLabelText('Symbol');
    expect(input).toBeInTheDocument();
    expect(input.tagName).toBe('INPUT');
    expect(input.id).toBe('symbol');
  });

  it('uses custom id when id prop provided', () => {
    render(<Input label="Symbol" id="custom-id" />);
    const input = screen.getByLabelText('Symbol');
    expect(input.id).toBe('custom-id');
  });

  it('renders error message when error prop provided', () => {
    render(<Input error="Required field" />);
    expect(screen.getByText('Required field')).toBeInTheDocument();
  });

  it('applies border-down class when error prop provided', () => {
    const { container } = render(<Input error="Invalid" />);
    const input = container.querySelector('input');
    expect(input.className).toContain('border-down');
  });

  it('does NOT render label when label is omitted', () => {
    const { container } = render(<Input placeholder="Enter..." />);
    expect(container.querySelector('label')).toBeNull();
  });

  it('passes aria-label through via ...props', () => {
    render(<Input aria-label="Search coins" />);
    const input = screen.getByLabelText('Search coins');
    expect(input).toBeInTheDocument();
  });

  it('passes through type, placeholder, value, onChange via ...props', () => {
    const handleChange = vi.fn();
    render(
      <Input
        type="number"
        placeholder="Amount"
        value="42"
        onChange={handleChange}
      />
    );
    const input = screen.getByPlaceholderText('Amount');
    expect(input.type).toBe('number');
    expect(input.value).toBe('42');

    fireEvent.change(input, { target: { value: '100' } });
    expect(handleChange).toHaveBeenCalled();
  });
});
