const alignMap = { left: 'text-left', right: 'text-right', center: 'text-center' };

export function Table({ className, ...props }) {
  return <table className={`w-full ${className || ''}`} {...props} />;
}

export function Th({ align = 'left', className = '', ...props }) {
  return (
    <th
      className={`text-text-muted text-xs uppercase py-1.5 px-3 border-b border-border ${alignMap[align]} ${className}`}
      {...props}
    />
  );
}

export function Td({ align = 'left', className = '', ...props }) {
  return (
    <td
      className={`py-1.5 px-3 ${alignMap[align]} ${className}`}
      {...props}
    />
  );
}
