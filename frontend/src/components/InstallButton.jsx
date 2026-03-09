import { useInstallPrompt } from '../hooks/useInstallPrompt';
import { Button } from './ui/Button';

function InstallButton() {
  const { isInstallable, install } = useInstallPrompt();

  if (!isInstallable) return null;

  return (
    <Button
      onClick={install}
      variant="ghost"
      size="md"
      className="bg-accent/20 border border-accent/40 text-accent hover:bg-accent/30"
    >
      Install App
    </Button>
  );
}

export default InstallButton;
