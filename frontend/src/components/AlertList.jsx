import { formatEUR } from '../lib/format';
import { Button } from './ui/Button';
import { Badge } from './ui/Badge';
import { EmptyState } from './ui/EmptyState';

function AlertList({ alerts, title, onRemove }) {
  if (!alerts || alerts.length === 0) {
    const isTriggered = title.toLowerCase().includes('triggered');
    return (
      <EmptyState
        title={isTriggered ? 'No triggered alerts' : 'No active alerts'}
        description={
          isTriggered
            ? 'Your alerts will appear here when target prices are reached.'
            : 'Set up a price alert using the form above to get notified when prices move.'
        }
        className="max-w-4xl"
      />
    );
  }

  return (
    <div className="max-w-4xl space-y-3">
      {alerts.map((alert) => (
        <div
          key={alert.id}
          className="bg-card border border-border rounded p-3 flex flex-col gap-2 sm:flex-row sm:justify-between sm:items-center"
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
