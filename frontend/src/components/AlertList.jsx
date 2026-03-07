import { formatEUR } from '../lib/format';

function AlertList({ alerts, title, onRemove }) {
  if (!alerts || alerts.length === 0) {
    return <p className="text-text-muted text-sm">No {title.toLowerCase()}</p>;
  }

  return (
    <div className="max-w-4xl">
      {alerts.map((alert) => (
        <div
          key={alert.id}
          className="bg-card border border-border rounded p-3 mb-2 flex justify-between items-center"
        >
          <div className="flex items-center gap-3">
            <span className="text-accent font-bold">{alert.symbol}</span>
            <span className="text-text text-sm">{formatEUR(alert.target_price)}</span>
            <span
              className={`rounded px-2 py-0.5 text-xs ${
                alert.direction === 'above'
                  ? 'text-up bg-up/10'
                  : 'text-down bg-down/10'
              }`}
            >
              {alert.direction}
            </span>
            {alert.triggered_at && (
              <span className="text-text-dim text-xs">
                triggered {new Date(alert.triggered_at).toLocaleString('nl-NL')}
              </span>
            )}
            {alert.created_at && !alert.triggered_at && (
              <span className="text-text-dim text-xs">
                created {new Date(alert.created_at).toLocaleString('nl-NL')}
              </span>
            )}
          </div>
          <button
            onClick={() => onRemove(alert.id)}
            className="text-down hover:text-down/80 text-sm cursor-pointer"
          >
            Remove
          </button>
        </div>
      ))}
    </div>
  );
}

export default AlertList;
