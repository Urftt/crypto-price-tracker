import { formatEUR, formatEURCompact, formatPct } from '../lib/format';

function PriceTable({ coins, onSelectCoin }) {
  return (
    <table className="w-full max-w-4xl">
      <thead>
        <tr>
          <th className="text-text-muted text-left text-xs uppercase py-1.5 px-3 border-b border-border">#</th>
          <th className="text-text-muted text-left text-xs uppercase py-1.5 px-3 border-b border-border">Symbol</th>
          <th className="text-text-muted text-left text-xs uppercase py-1.5 px-3 border-b border-border">Name</th>
          <th className="text-text-muted text-right text-xs uppercase py-1.5 px-3 border-b border-border">Price (EUR)</th>
          <th className="text-text-muted text-right text-xs uppercase py-1.5 px-3 border-b border-border">24h %</th>
          <th className="text-text-muted text-right text-xs uppercase py-1.5 px-3 border-b border-border">Volume (EUR)</th>
        </tr>
      </thead>
      <tbody>
        {coins.map((coin, i) => (
          <tr
            key={coin.symbol}
            onClick={() => onSelectCoin(coin)}
            className="cursor-pointer hover:bg-card border-b border-border/50"
          >
            <td className="py-1.5 px-3 text-text-dim text-sm">{i + 1}</td>
            <td className="py-1.5 px-3 text-accent font-bold">{coin.symbol}</td>
            <td className="py-1.5 px-3 text-text-muted text-sm">{coin.name}</td>
            <td className="py-1.5 px-3 text-right">{formatEUR(coin.price)}</td>
            <td className={`py-1.5 px-3 text-right ${coin.change_24h > 0 ? 'text-up' : coin.change_24h < 0 ? 'text-down' : 'text-text-muted'}`}>
              {formatPct(coin.change_24h)}
            </td>
            <td className="py-1.5 px-3 text-right text-text-muted">{formatEURCompact(coin.volume_eur)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default PriceTable;
