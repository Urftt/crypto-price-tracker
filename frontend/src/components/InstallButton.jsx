import { useInstallPrompt } from '../hooks/useInstallPrompt';

function InstallButton() {
  const { isInstallable, install } = useInstallPrompt();

  if (!isInstallable) return null;

  return (
    <button
      onClick={install}
      className="px-3 py-1.5 bg-accent/20 border border-accent/40 rounded text-sm text-accent hover:bg-accent/30 cursor-pointer"
    >
      Install App
    </button>
  );
}

export default InstallButton;
