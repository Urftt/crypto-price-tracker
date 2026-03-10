import { useEffect, useRef } from 'react';

export function Modal({ open, onClose, children }) {
  const modalRef = useRef(null);

  // Escape key handler
  useEffect(() => {
    if (!open) return;

    function handleKeyDown(e) {
      if (e.key === 'Escape') {
        onClose();
      }
    }

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [open, onClose]);

  // Focus trap
  useEffect(() => {
    if (!open || !modalRef.current) return;

    const focusableSelector =
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';

    const focusable = modalRef.current.querySelectorAll(focusableSelector);
    if (focusable.length > 0) {
      focusable[0].focus();
    }

    function handleTab(e) {
      if (e.key !== 'Tab') return;

      const currentFocusable = modalRef.current.querySelectorAll(focusableSelector);
      if (currentFocusable.length === 0) return;

      const first = currentFocusable[0];
      const last = currentFocusable[currentFocusable.length - 1];

      if (e.shiftKey) {
        if (document.activeElement === first) {
          e.preventDefault();
          last.focus();
        }
      } else {
        if (document.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      }
    }

    document.addEventListener('keydown', handleTab);
    return () => document.removeEventListener('keydown', handleTab);
  }, [open]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 bg-black/70 z-40 flex items-center justify-center"
      onClick={onClose}
    >
      <div
        ref={modalRef}
        className="bg-card border-border-light w-full h-full sm:border sm:rounded-lg sm:p-6 sm:max-w-xl sm:h-auto sm:mx-4 p-4 relative z-50 overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {children}
      </div>
    </div>
  );
}
