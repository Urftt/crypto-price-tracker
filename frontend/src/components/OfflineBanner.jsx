import { useOffline } from '../hooks/useOffline';

function OfflineBanner() {
  const isOffline = useOffline();

  if (!isOffline) return null;

  return (
    <div className="bg-down/20 border border-down/40 text-down text-sm text-center py-2 px-4">
      You're offline — showing last known data
    </div>
  );
}

export default OfflineBanner;
