import { useNavigate } from 'react-router';
import { formatEUR, formatEURCompact, formatPct } from '../lib/format';
import PriceChart from './PriceChart';
import { Modal } from './ui/Modal';
import { Button } from './ui/Button';

function CoinModal({ coin, open, onClose }) {
  const navigate = useNavigate();

  const handleSetAlert = () => {
    navigate(`/alerts?symbol=${coin?.symbol}`);
    onClose();
  };

  return (
    <Modal open={open} onClose={onClose}>
      <Button variant="ghost" size="sm" onClick={onClose} type="button" className="absolute top-3 right-4 text-xl">
        x
      </Button>
      {coin && (
        <>
          <div className="mb-4">
            <span className="text-accent text-2xl font-bold mr-2">{coin.symbol}</span>
            <span className="text-text-muted">{coin.name}</span>
          </div>

          <div className="grid grid-cols-2 gap-3 mb-5 text-sm">
            <div>
              <span className="text-text-muted">Price</span>
              <div className="text-text">{formatEUR(coin.price)}</div>
            </div>
            <div>
              <span className="text-text-muted">24h Change</span>
              <div className={coin.change_24h > 0 ? 'text-up' : coin.change_24h < 0 ? 'text-down' : 'text-text-muted'}>
                {formatPct(coin.change_24h)}
              </div>
            </div>
            <div>
              <span className="text-text-muted">Volume</span>
              <div className="text-text">{coin.volume.toLocaleString('nl-NL')}</div>
            </div>
            <div>
              <span className="text-text-muted">Volume EUR</span>
              <div className="text-text">{formatEURCompact(coin.volume_eur)}</div>
            </div>
          </div>

          <PriceChart symbol={coin.symbol} />

          <div className="mt-4 flex justify-end">
            <Button
              onClick={handleSetAlert}
              variant="secondary"
              size="md"
              type="button"
              className="bg-accent/20 text-accent border-accent/30 hover:bg-accent/30"
            >
              Set Alert
            </Button>
          </div>
        </>
      )}
    </Modal>
  );
}

export default CoinModal;
