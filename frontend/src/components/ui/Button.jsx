const variants = {
  primary: 'bg-accent text-bg font-bold hover:bg-accent/80',
  secondary: 'bg-card border border-border text-text hover:border-border-light',
  danger: 'text-down hover:text-down/80',
  ghost: 'text-text-muted hover:text-text',
};

const sizes = {
  xs: 'px-1 py-0.5 text-xs',
  sm: 'px-2.5 py-0.5 text-xs',
  md: 'px-4 py-1.5 text-sm',
};

const base = 'rounded cursor-pointer transition-colors disabled:opacity-50 disabled:cursor-not-allowed';

export function Button({
  variant = 'primary',
  size = 'md',
  loading = false,
  className = '',
  children,
  disabled,
  ...props
}) {
  return (
    <button
      className={`${base} ${variants[variant]} ${sizes[size]} ${className}`}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? 'Submitting...' : children}
    </button>
  );
}
