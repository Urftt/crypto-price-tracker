import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { Modal } from '../Modal';

describe('Modal', () => {
  it('returns null when open=false', () => {
    const { container } = render(
      <Modal open={false} onClose={() => {}}>
        <p>hidden content</p>
      </Modal>
    );
    expect(container.innerHTML).toBe('');
  });

  it('renders children when open=true', () => {
    render(
      <Modal open={true} onClose={() => {}}>
        <p>visible content</p>
      </Modal>
    );
    expect(screen.getByText('visible content')).toBeInTheDocument();
  });

  it('calls onClose when Escape is pressed', () => {
    const onClose = vi.fn();
    render(
      <Modal open={true} onClose={onClose}>
        <p>modal content</p>
      </Modal>
    );
    fireEvent.keyDown(document, { key: 'Escape' });
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('calls onClose when backdrop is clicked', () => {
    const onClose = vi.fn();
    const { container } = render(
      <Modal open={true} onClose={onClose}>
        <p>modal content</p>
      </Modal>
    );
    // Click on the backdrop (outermost div)
    const backdrop = container.firstChild;
    fireEvent.click(backdrop);
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('does NOT call onClose when content area is clicked', () => {
    const onClose = vi.fn();
    render(
      <Modal open={true} onClose={onClose}>
        <p>modal content</p>
      </Modal>
    );
    fireEvent.click(screen.getByText('modal content'));
    expect(onClose).not.toHaveBeenCalled();
  });

  it('renders with correct z-40 backdrop and z-50 content classes', () => {
    const { container } = render(
      <Modal open={true} onClose={() => {}}>
        <p>content</p>
      </Modal>
    );
    const backdrop = container.firstChild;
    expect(backdrop.className).toContain('z-40');

    const content = backdrop.firstChild;
    expect(content.className).toContain('z-50');
  });
});
