import { render } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Table, Th, Td } from '../Table';

describe('Table', () => {
  it('renders a table element with w-full class', () => {
    const { container } = render(<Table />);
    const table = container.querySelector('table');
    expect(table).toBeInTheDocument();
    expect(table.className).toContain('w-full');
  });
});

describe('Th', () => {
  it('renders with text-left by default', () => {
    const { container } = render(
      <table><thead><tr><Th>Header</Th></tr></thead></table>
    );
    const th = container.querySelector('th');
    expect(th.className).toContain('text-left');
  });

  it('renders with text-right when align="right"', () => {
    const { container } = render(
      <table><thead><tr><Th align="right">Price</Th></tr></thead></table>
    );
    const th = container.querySelector('th');
    expect(th.className).toContain('text-right');
  });

  it('renders with text-center when align="center"', () => {
    const { container } = render(
      <table><thead><tr><Th align="center">Status</Th></tr></thead></table>
    );
    const th = container.querySelector('th');
    expect(th.className).toContain('text-center');
  });

  it('includes text-text-muted, text-xs, uppercase, border-b, border-border classes', () => {
    const { container } = render(
      <table><thead><tr><Th>Header</Th></tr></thead></table>
    );
    const th = container.querySelector('th');
    expect(th.className).toContain('text-text-muted');
    expect(th.className).toContain('text-xs');
    expect(th.className).toContain('uppercase');
    expect(th.className).toContain('border-b');
    expect(th.className).toContain('border-border');
  });

  it('appends custom className', () => {
    const { container } = render(
      <table><thead><tr><Th className="w-32">Header</Th></tr></thead></table>
    );
    const th = container.querySelector('th');
    expect(th.className).toContain('w-32');
  });
});

describe('Td', () => {
  it('renders with text-left by default', () => {
    const { container } = render(
      <table><tbody><tr><Td>Data</Td></tr></tbody></table>
    );
    const td = container.querySelector('td');
    expect(td.className).toContain('text-left');
  });

  it('renders with text-right when align="right"', () => {
    const { container } = render(
      <table><tbody><tr><Td align="right">$100</Td></tr></tbody></table>
    );
    const td = container.querySelector('td');
    expect(td.className).toContain('text-right');
  });

  it('includes py-1.5 and px-3 classes', () => {
    const { container } = render(
      <table><tbody><tr><Td>Data</Td></tr></tbody></table>
    );
    const td = container.querySelector('td');
    expect(td.className).toContain('py-1.5');
    expect(td.className).toContain('px-3');
  });

  it('appends custom className', () => {
    const { container } = render(
      <table><tbody><tr><Td className="font-mono">Data</Td></tr></tbody></table>
    );
    const td = container.querySelector('td');
    expect(td.className).toContain('font-mono');
  });
});
