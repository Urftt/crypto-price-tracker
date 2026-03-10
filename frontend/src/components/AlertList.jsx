import { formatEUR } from '../lib/format';
import { Button } from './ui/Button';
import { Badge } from './ui/Badge';

function AlertList({ alerts, title, onRemove }) {
  if (!alerts || alerts.length === 0) {
    return <p className="text-text-muted text-sm">No {title.toLowerCase()}</p>;
  }

  return (
    <div className="max-w-4xl">
      {alerts.map((alert) => (
        <div
          key={alert.id}
          className="bg-card border border-border rounded p-3 mb-2 flex flex-col gap-2 sm:flex-row sm:justify-between sm:items-center"
        >
          <div className="flex items-center gap-3">
            <span className="text-accent font-bold">{alert.symbol}</span>
            <span className="text-text text-sm">{formatEUR(alert.target_price)}</span>
            <Badge variant={alert.direction === 'above' ? 'up' : 'down'}>
              {alert.direction}
            </Badge>
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
          <Button variant="danger" size="sm" onClick={() => onRemove(alert.id)} type="button">
            Remove
          </Button>
        </div>
      ))}
    </div>
  );
}

export default AlertList;
