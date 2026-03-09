import { useEffect } from 'react';
import { Button } from './ui/Button';

function Toast({ message, type = 'info', duration = 10000, onClose, style }) {
  useEffect(() => {
    const timer = setTimeout(onClose, duration);
    return () => clearTimeout(timer);
  }, [duration, onClose]);

  const colors = {
    info: 'border-accent text-accent',
    success: 'border-up text-up',
    error: 'border-down text-down',
  };

  return (
    <div
      className={`fixed right-4 z-50 bg-card border ${colors[type]} rounded px-4 py-3 font-mono text-sm shadow-lg`}
      style={style}
    >
      {message}
      <Button variant="ghost" size="xs" onClick={onClose} type="button" className="ml-3">
        x
      </Button>
    </div>
  );
}

export default Toast;
