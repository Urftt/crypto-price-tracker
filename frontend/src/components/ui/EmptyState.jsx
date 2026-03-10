export function EmptyState({ title, description, className = '' }) {
  return (
    <div className={`text-center py-8 ${className}`}>
      <p className="text-text-muted text-lg mb-1">{title}</p>
      {description && (
        <p className="text-text-dim text-sm">{description}</p>
      )}
    </div>
  );
}
