import { useEffect, useRef, useState, useCallback } from 'react';

export function useSSE(url) {
  const [data, setData] = useState(null);
  const [connected, setConnected] = useState(false);
  const esRef = useRef(null);

  const connect = useCallback(() => {
    const es = new EventSource(url);
    esRef.current = es;

    es.addEventListener('prices', (event) => {
      setData(JSON.parse(event.data));
    });

    es.onopen = () => setConnected(true);

    es.onerror = () => {
      setConnected(false);
      es.close();
      // Manual reconnect if readyState is CLOSED
      if (es.readyState === EventSource.CLOSED) {
        setTimeout(connect, 3000);
      }
    };

    return es;
  }, [url]);

  useEffect(() => {
    const es = connect();
    return () => {
      es.close();
      esRef.current = null;
    };
  }, [connect]);

  return { data, connected };
}
