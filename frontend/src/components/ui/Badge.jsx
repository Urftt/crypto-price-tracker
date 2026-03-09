const colorSchemes = {
  blue: 'bg-blue-900/50 text-blue-300 border-blue-700',
  purple: 'bg-purple-900/50 text-purple-300 border-purple-700',
  green: 'bg-green-900/50 text-green-300 border-green-700',
  yellow: 'bg-yellow-900/50 text-yellow-300 border-yellow-700',
  orange: 'bg-orange-900/50 text-orange-300 border-orange-700',
  red: 'bg-red-900/50 text-red-300 border-red-700',
  gray: 'bg-border text-text-muted border-border',
};

const variants = {
  up: 'text-up bg-up/10',
  down: 'text-down bg-down/10',
};

export function Badge({ colorScheme, variant, className = '', children, ...props }) {
  let base = 'rounded px-2 py-0.5 text-xs';
  let colorClasses;

  if (colorScheme) {
    base += ' border';
    colorClasses = colorSchemes[colorScheme];
  } else if (variant) {
    colorClasses = variants[variant];
  } else {
    base += ' border';
    colorClasses = colorSchemes.gray;
  }

  return (
    <span className={`${base} ${colorClasses} ${className}`} {...props}>
      {children}
    </span>
  );
}
