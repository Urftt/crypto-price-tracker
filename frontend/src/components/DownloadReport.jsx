import { useState } from 'react';

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
    <button
      onClick={handleDownload}
      disabled={loading}
      className="px-3 py-1.5 bg-card border border-border rounded text-sm text-text hover:border-border-light disabled:opacity-50 cursor-pointer"
    >
      {loading ? 'Generating...' : 'Download Report'}
    </button>
  );
}

export default DownloadReport;
