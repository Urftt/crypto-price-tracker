import { useState, useEffect } from 'react';
import { Button } from './ui/Button';

function Toast({ message, type = 'info', duration = 10000, onClose, style }) {
  const [dismissing, setDismissing] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setDismissing(true), duration);
    return () => clearTimeout(timer);
  }, [duration]);

  const handleAnimationEnd = () => {
    if (dismissing) onClose();
  };

  const colors = {
    info: 'border-accent text-accent',
    success: 'border-up text-up',
    error: 'border-down text-down',
  };

  return (
    <div
      className={`fixed right-4 z-50 bg-card border ${colors[type]} rounded px-4 py-3 font-mono text-sm shadow-lg ${
        dismissing ? 'animate-fade-out' : 'animate-slide-in-right'
      }`}
      style={style}
      onAnimationEnd={handleAnimationEnd}
    >
      {message}
      <Button variant="ghost" size="xs" onClick={() => setDismissing(true)} type="button" className="ml-3">
        x
      </Button>
    </div>
  );
}

export default Toast;
