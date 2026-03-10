export function Skeleton({ className = '', ...props }) {
  return (
    <div
      className={`animate-pulse bg-border rounded ${className}`}
      {...props}
    />
  );
}
