import { useState } from 'react';
import { Button } from './ui/Button';

function DownloadReport() {
  const [loading, setLoading] = useState(false);

  const handleDownload = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/export/pdf');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'crypto-report.pdf';
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Download failed:', err);
    }
    setLoading(false);
  };

  return (
    <Button
      onClick={handleDownload}
      disabled={loading}
      variant="secondary"
      size="md"
    >
      {loading ? 'Generating...' : 'Download Report'}
    </Button>
  );
}

export default DownloadReport;
