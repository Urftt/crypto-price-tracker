export function Input({ label, error, className = '', id, ...props }) {
  const inputId = id || label?.toLowerCase().replace(/\s+/g, '-');

  return (
    <div className={className}>
      {label && (
        <label htmlFor={inputId} className="text-text-muted text-xs mb-0.5 block">
          {label}
        </label>
      )}
      <input
        id={inputId}
        className={`bg-bg border rounded px-3 py-1.5 text-text text-sm focus:border-accent focus:outline-none w-full ${error ? 'border-down' : 'border-border'}`}
        {...props}
      />
      {error && <p className="text-down text-xs mt-0.5">{error}</p>}
    </div>
  );
}
