import { useState, useEffect } from 'react';

function CountdownTimer({ lastUpdate, interval = 10 }) {
  const [countdown, setCountdown] = useState(interval);

  // Reset countdown when lastUpdate changes
  useEffect(() => {
    setCountdown(interval);
  }, [lastUpdate, interval]);

  // Tick every second
  useEffect(() => {
    const id = setInterval(() => {
      if (lastUpdate) {
        const elapsed = Math.floor((Date.now() - lastUpdate.getTime()) / 1000);
        setCountdown(Math.max(0, interval - elapsed));
      }
    }, 1000);
    return () => clearInterval(id);
  }, [lastUpdate, interval]);

  return (
    <span>
      Next update in <span className="text-accent font-bold">{countdown}s</span>
    </span>
  );
}

export default CountdownTimer;
