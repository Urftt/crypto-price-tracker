# Phase 12: Export & Reporting - Research

**Researched:** 2026-03-08
**Domain:** PDF report generation, notification channels (Telegram/email), CLI export commands
**Confidence:** HIGH

## Summary

Phase 12 adds two capabilities: (1) rich PDF report export combining portfolio P&L, live prices, watchlist, and alerts into a single document accessible via CLI (`crypto export --format pdf`) and web (`/api/export/pdf`), and (2) notification delivery of portfolio summaries via Telegram Bot API and SMTP email. The existing `crypto portfolio export` (csv/json) remains unchanged.

The key technical decision is the HTML-to-PDF library. **xhtml2pdf** is the clear choice over weasyprint: it is pure Python with zero system-level dependencies (no cairo/pango/libffi), installs with a simple `pip install`, and provides adequate CSS table rendering for clean report layouts. Weasyprint produces better CSS3 output but requires system packages that add deployment friction and are unnecessary for structured table reports.

**Primary recommendation:** Use xhtml2pdf 0.2.17 for HTML-to-PDF conversion. Use httpx (existing dependency) for Telegram Bot API. Use stdlib smtplib/email.mime for SMTP email. Split into two plans: Plan 1 covers backend report/notify modules + CLI + tests; Plan 2 covers web API endpoint + React download button + web tests.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Command structure: Both -- keep `crypto portfolio export` for raw data (csv/json), add new top-level `crypto export` for rich reports (pdf)
- Data scope: Full report -- portfolio P&L + current top-N price table + watchlist + active alerts
- Price data: Live fetch at export time
- PDF library: HTML-to-PDF approach (generate HTML tables, convert with lightweight library)
- Styling: Minimal with color -- clean tables with green/red P&L coloring matching CLI/web theme
- Web download: Yes -- add `/api/export/pdf` endpoint with Download Report button
- Notification channels: Both Telegram and email via SMTP
- Summary data: Portfolio P&L changes -- total portfolio value, week-over-week change, top gainers/losers
- Scheduling: Manual `crypto summary send` command (cron-schedulable externally)
- Config: Environment variables for Telegram and SMTP credentials
- New files: `report.py` and `notify.py` in `src/crypto_price_tracker/`
- Modified files: `cli.py` (export + summary subcommands), `web.py` (/api/export/pdf), `frontend/src/` (Download button)

### Claude's Discretion
None explicitly stated -- all major decisions are locked.

### Deferred Ideas (OUT OF SCOPE)
None raised during discussion.
</user_constraints>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| xhtml2pdf | 0.2.17 | HTML-to-PDF conversion | Pure Python, no system deps, adequate table rendering, actively maintained |
| httpx | >=0.27 (existing) | Telegram Bot API calls | Already a project dependency, async-capable, clean API |
| smtplib | stdlib | SMTP email sending | No new dependency, Python built-in, well-documented |
| email.mime | stdlib | MIME message construction | No new dependency, MIMEMultipart for HTML emails |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| io.BytesIO | stdlib | In-memory PDF buffer | Generate PDF without temp files for web endpoint |
| ssl | stdlib | TLS context for SMTP | Secure SMTP connections with STARTTLS |
| dataclasses.asdict | stdlib | Serialize models for templates | Already used project-wide |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| xhtml2pdf | weasyprint | Better CSS3 but requires system packages (cairo, pango, libffi) -- deployment friction |
| xhtml2pdf | fpdf2 | No HTML templating -- must build PDF programmatically, harder to iterate on layout |
| xhtml2pdf | reportlab direct | Low-level API, no HTML/CSS, tedious table construction |
| smtplib | third-party (sendgrid, mailgun) | Adds dependency and API key requirement for simple SMTP |

**Installation:**
```bash
uv add xhtml2pdf
```

This is the **only new dependency**. All other functionality uses existing deps (httpx) or stdlib (smtplib, email, ssl, io).

## Architecture Patterns

### Recommended Project Structure
```
src/crypto_price_tracker/
    report.py          # HTML template generation, PDF conversion, summary aggregation
    notify.py          # Telegram and email notification channels
    cli.py             # + export subcommand, + summary send subcommand
    web.py             # + /api/export/pdf endpoint
frontend/src/
    components/
        DownloadReport.jsx  # Download Report button component
    pages/
        PortfolioPage.jsx   # + DownloadReport button in portfolio view
```

### Pattern 1: Report Module (report.py)
**What:** Single module with three responsibilities: HTML template generation, PDF conversion, summary data aggregation.
**When to use:** All export and reporting operations.
**Example:**
```python
# Source: xhtml2pdf quickstart + project patterns
import io
from datetime import datetime
from xhtml2pdf import pisa
from crypto_price_tracker.portfolio import aggregate_portfolio, PortfolioSummary
from crypto_price_tracker.models import CoinData, WatchlistEntry, PriceAlert


def generate_report_html(
    portfolio: PortfolioSummary,
    coins: list[CoinData],
    watchlist: list[WatchlistEntry],
    alerts: list[PriceAlert],
) -> str:
    """Build a complete HTML report string with inline CSS styling."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Build HTML tables with inline styles for P&L coloring
    # Green (#3fb950) for positive, red (#f85149) for negative -- matches project theme
    ...
    return html_string


def html_to_pdf(html: str) -> bytes:
    """Convert an HTML string to PDF bytes using xhtml2pdf."""
    buffer = io.BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=buffer)
    if pisa_status.err:
        raise RuntimeError(f"PDF generation failed with {pisa_status.err} errors")
    return buffer.getvalue()


def build_summary_text(portfolio: PortfolioSummary) -> str:
    """Build a plain-text summary of portfolio performance for notifications."""
    ...
```

### Pattern 2: Notification Channels (notify.py)
**What:** Two independent channel implementations (Telegram, email) with auto-detection of configured channels.
**When to use:** `crypto summary send` command.
**Example:**
```python
# Source: Telegram Bot API docs + Python smtplib docs
import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import httpx


def send_telegram(message: str) -> bool:
    """Send a message via Telegram Bot API. Returns True on success."""
    token = os.environ.get("CRYPTO_TELEGRAM_TOKEN")
    chat_id = os.environ.get("CRYPTO_TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    response = httpx.post(url, json={
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
    })
    response.raise_for_status()
    return True


def send_email(subject: str, html_body: str, text_body: str) -> bool:
    """Send an HTML email via SMTP with STARTTLS. Returns True on success."""
    host = os.environ.get("CRYPTO_SMTP_HOST")
    if not host:
        return False
    port = int(os.environ.get("CRYPTO_SMTP_PORT", "587"))
    user = os.environ.get("CRYPTO_SMTP_USER", "")
    password = os.environ.get("CRYPTO_SMTP_PASS", "")
    from_addr = os.environ.get("CRYPTO_SMTP_FROM", "")
    to_addr = os.environ.get("CRYPTO_SMTP_TO", "")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    context = ssl.create_default_context()
    with smtplib.SMTP(host, port) as server:
        server.starttls(context=context)
        if user and password:
            server.login(user, password)
        server.sendmail(from_addr, to_addr, msg.as_string())
    return True


def send_summary(message: str, html_message: str) -> list[str]:
    """Send summary to all configured channels. Returns list of channels sent to."""
    sent = []
    if send_telegram(message):
        sent.append("telegram")
    if send_email("Crypto Portfolio Summary", html_message, message):
        sent.append("email")
    return sent
```

### Pattern 3: FastAPI PDF Endpoint
**What:** Generate PDF in-memory, return as StreamingResponse.
**When to use:** Web download endpoint.
**Example:**
```python
# Source: FastAPI custom response docs
from fastapi.responses import StreamingResponse

@app.get("/api/export/pdf")
def api_export_pdf():
    """Generate and return a PDF portfolio report."""
    # Gather data (same as report.py pattern)
    html = generate_report_html(portfolio, coins, watchlist, alerts)
    pdf_bytes = html_to_pdf(html)
    buffer = io.BytesIO(pdf_bytes)
    headers = {
        "Content-Disposition": f"attachment; filename=crypto-report-{date}.pdf"
    }
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers=headers,
    )
```

### Pattern 4: CLI Subcommand Registration (follows existing argparse pattern)
**What:** Add `export` and `summary` as new top-level subcommands alongside existing `prices`, `watch`, etc.
**When to use:** CLI entry point in cli.py.
**Example:**
```python
# Follows existing argparse pattern in cli.py -- NOT click/typer

# export subcommand
export_parser = subparsers.add_parser("export", help="Generate rich PDF report")
export_parser.add_argument(
    "--format", choices=["pdf"], default="pdf",
    dest="export_format", help="Report format (default: pdf)",
)
export_parser.add_argument(
    "--output", "-o", type=str, default=None,
    help="Output file path (default: auto-named)",
)

# summary subcommand group
summary_parser = subparsers.add_parser("summary", help="Portfolio summary notifications")
summary_sub = summary_parser.add_subparsers(dest="summary_command")
summary_sub.add_parser("send", help="Send portfolio summary to configured channels")
```

### Anti-Patterns to Avoid
- **Generating temporary files for web PDF:** Use io.BytesIO for in-memory generation. No temp files needed.
- **Importing weasyprint/cairo:** Requires system-level package installation. xhtml2pdf is pure Python.
- **Complex Jinja2 templating:** The HTML report is simple enough to build with f-strings or string.Template. No need for a template engine dependency.
- **Storing notification credentials in config files:** Use environment variables per the 12-factor convention already established.
- **Sending raw P&L numbers without formatting:** Match the EUR formatting convention used elsewhere (nl-NL locale, green/red coloring).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| HTML-to-PDF conversion | Custom PDF rendering with reportlab | xhtml2pdf.pisa.CreatePDF() | HTML/CSS is far easier to iterate on than programmatic PDF layout |
| Telegram message sending | Custom HTTP client wrapper | httpx.post() to Bot API | httpx is already a dependency, Telegram API is a single POST call |
| HTML email construction | Manual MIME string building | email.mime.multipart.MIMEMultipart | stdlib handles encoding, headers, multipart boundaries correctly |
| TLS/SSL for SMTP | Manual socket handling | smtplib.SMTP + starttls() + ssl.create_default_context() | stdlib handles certificate validation, protocol negotiation |
| EUR number formatting in HTML | Custom format strings | Match existing f"EUR {value:,.2f}" pattern | Consistent with CLI display module formatting |

**Key insight:** Every component in this phase has a well-tested stdlib or single-dependency solution. The only new pip dependency is xhtml2pdf.

## Common Pitfalls

### Pitfall 1: xhtml2pdf CSS Layout Limitations
**What goes wrong:** Developers assume full CSS3 support (flexbox, grid, complex margins) and get broken layouts.
**Why it happens:** xhtml2pdf supports CSS 2.1 only. Padding, margin, and display properties work but complex layouts do not.
**How to avoid:** Use simple HTML tables with inline styles. Stick to: background-color, color, font-size, font-weight, border properties, padding, text-align, width. Avoid: flexbox, grid, float, position.
**Warning signs:** Tables not rendering, elements overlapping, styles being ignored silently.

### Pitfall 2: Telegram Message Length Limit
**What goes wrong:** Sending a full portfolio summary exceeds the 4096 character limit and the API returns an error.
**Why it happens:** Telegram messages are capped at 4096 UTF-8 characters.
**How to avoid:** Keep summary text concise. Show top 5 gainers/losers, total value, and overall P&L. If the portfolio has many holdings, truncate with "... and N more". For full reports, consider using sendDocument to send the PDF file directly.
**Warning signs:** HTTP 400 from Telegram API with "message is too long" error.

### Pitfall 3: SMTP Connection Failures Silently Swallowed
**What goes wrong:** Email sending fails (wrong credentials, blocked port, TLS error) and the user gets no feedback.
**Why it happens:** Catching broad exceptions without re-raising or logging.
**How to avoid:** Let SMTP exceptions propagate to the CLI handler. Print clear error messages: "Failed to send email: [error]". Only catch and suppress in `send_summary()` when one channel fails but others should still be attempted.
**Warning signs:** `crypto summary send` reports success but no email arrives.

### Pitfall 4: xhtml2pdf and ReportLab Import Errors
**What goes wrong:** Import errors or missing font warnings when xhtml2pdf is first used.
**Why it happens:** xhtml2pdf depends on reportlab which may log font warnings. Some environments have issues with the arabic_reshaper optional dependency.
**How to avoid:** Install xhtml2pdf cleanly via `uv add xhtml2pdf`. The core functionality (HTML tables to PDF) works without optional extras.
**Warning signs:** ImportWarning about fonts, but PDF still generates correctly -- these are non-fatal.

### Pitfall 5: BytesIO Position After Write
**What goes wrong:** StreamingResponse returns empty PDF because BytesIO cursor is at end after write.
**Why it happens:** After `pisa.CreatePDF(html, dest=buffer)`, the buffer position is at the end.
**How to avoid:** Use `buffer.getvalue()` to get bytes (creates new bytes object from full buffer content), then wrap in a new BytesIO for StreamingResponse. Alternatively, call `buffer.seek(0)` before passing to StreamingResponse.
**Warning signs:** PDF download produces 0-byte or corrupted file.

### Pitfall 6: Email HTML vs Plain Text
**What goes wrong:** Email client shows raw HTML tags instead of rendered content.
**Why it happens:** Only attaching HTML part without setting MIMEMultipart("alternative") correctly, or attaching in wrong order.
**How to avoid:** Always use MIMEMultipart("alternative"). Attach plain text FIRST, then HTML. Email clients render the last compatible subpart.
**Warning signs:** Email arrives with visible `<table>` tags.

## Code Examples

Verified patterns from official sources:

### xhtml2pdf In-Memory PDF Generation
```python
# Source: https://xhtml2pdf.readthedocs.io/en/latest/quickstart.html
import io
from xhtml2pdf import pisa

def html_to_pdf(html: str) -> bytes:
    """Convert HTML string to PDF bytes."""
    buffer = io.BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=buffer)
    if pisa_status.err:
        raise RuntimeError(f"PDF generation failed with {pisa_status.err} errors")
    return buffer.getvalue()
```

### Telegram Bot API sendMessage with HTML Formatting
```python
# Source: https://core.telegram.org/bots/api#sendmessage
import httpx

def send_telegram(token: str, chat_id: str, message: str) -> None:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    response = httpx.post(url, json={
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
    })
    response.raise_for_status()
```

Telegram HTML parse_mode supports: `<b>bold</b>`, `<i>italic</i>`, `<code>monospace</code>`, `<pre>preformatted</pre>`. For table-like formatting in Telegram, use `<pre>` with fixed-width text alignment since Telegram does not render HTML tables.

### SMTP HTML Email with STARTTLS
```python
# Source: https://realpython.com/python-send-email/ + Python smtplib docs
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_html_email(
    host: str, port: int, user: str, password: str,
    from_addr: str, to_addr: str,
    subject: str, text_body: str, html_body: str,
) -> None:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr
    # Attach plain text FIRST, then HTML (email clients render last compatible part)
    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    context = ssl.create_default_context()
    with smtplib.SMTP(host, port) as server:
        server.starttls(context=context)
        if user and password:
            server.login(user, password)
        server.sendmail(from_addr, to_addr, msg.as_string())
```

### FastAPI PDF Download Endpoint
```python
# Source: https://fastapi.tiangolo.com/advanced/custom-response/
import io
from fastapi.responses import StreamingResponse

@app.get("/api/export/pdf")
def api_export_pdf():
    # ... gather data and generate HTML ...
    pdf_bytes = html_to_pdf(html)
    headers = {
        "Content-Disposition": "attachment; filename=crypto-report.pdf"
    }
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers=headers,
    )
```

### React Download Button (follows existing project patterns)
```jsx
// Source: project patterns from PortfolioPage.jsx + useApi hook
function DownloadReport() {
  const [loading, setLoading] = useState(false);

  const handleDownload = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/export/pdf');
      if (!res.ok) throw new Error(`${res.status}`);
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
      className="px-3 py-1.5 bg-card border border-border rounded text-sm text-text hover:border-border-light disabled:opacity-50"
    >
      {loading ? 'Generating...' : 'Download Report'}
    </button>
  );
}
```

Note: The download button uses `fetch()` directly (not `useApi`) because it handles a binary blob response, not JSON.

### HTML Report Template Structure
```html
<!-- xhtml2pdf-compatible HTML with inline CSS -->
<html>
<head>
  <style>
    body { font-family: Helvetica, Arial, sans-serif; font-size: 11px; color: #333; }
    h1 { font-size: 18px; color: #0d1117; border-bottom: 2px solid #0d1117; padding-bottom: 5px; }
    h2 { font-size: 14px; color: #0d1117; margin-top: 20px; }
    table { width: 100%; border-collapse: collapse; margin-bottom: 15px; }
    th { background-color: #0d1117; color: #e6edf3; padding: 6px 8px; text-align: left; font-size: 10px; }
    td { padding: 5px 8px; border-bottom: 1px solid #ddd; font-size: 10px; }
    tr:nth-child(even) { background-color: #f6f8fa; }
    .green { color: #3fb950; }
    .red { color: #f85149; }
    .right { text-align: right; }
    .summary { margin-top: 10px; font-size: 12px; font-weight: bold; }
  </style>
</head>
<body>
  <h1>Crypto Portfolio Report</h1>
  <p>Generated: {timestamp}</p>

  <h2>Portfolio Summary</h2>
  <p class="summary">
    Total Value: EUR {total_value} |
    Total P&L: <span class="{pnl_class}">EUR {total_pnl}</span>
  </p>

  <h2>Holdings</h2>
  <table>
    <tr><th>Symbol</th><th class="right">Amount</th><th class="right">Avg Buy</th>
        <th class="right">Value</th><th class="right">P&L</th><th class="right">Alloc</th></tr>
    {portfolio_rows}
  </table>

  <h2>Top Prices</h2>
  <table>
    <tr><th>#</th><th>Symbol</th><th>Name</th><th class="right">Price (EUR)</th>
        <th class="right">24h %</th></tr>
    {price_rows}
  </table>

  <!-- Watchlist and Alerts sections follow same pattern -->
</body>
</html>
```

**Important xhtml2pdf CSS notes:**
- Use `border-collapse: collapse` for tables (supported)
- Use `nth-child(even)` for striped rows (supported in xhtml2pdf)
- Avoid `float`, `flexbox`, `grid` (not supported)
- Colors work: `color: #3fb950` for green, `color: #f85149` for red
- `width: 100%` on tables works correctly

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| weasyprint (system deps) | xhtml2pdf (pure Python) | Always available | Zero system-dep install for PDF generation |
| python-telegram-bot library | Direct httpx to Bot API | N/A | No extra dependency, single POST call is sufficient |
| email library complexity | MIMEMultipart("alternative") | Python 3.x | Simple, well-documented stdlib pattern |

**Deprecated/outdated:**
- pisa (old name): Now called xhtml2pdf, same library
- wkhtmltopdf: Requires headless WebKit, system binary -- overly complex for table reports

## Open Questions

1. **xhtml2pdf font rendering on Linux without desktop fonts**
   - What we know: xhtml2pdf uses ReportLab's built-in fonts (Helvetica, Times, Courier) which are always available
   - What's unclear: Whether custom fonts need configuration
   - Recommendation: Stick with Helvetica/Arial in CSS. These are ReportLab built-ins and always work. No custom font setup needed.

2. **Telegram message formatting for tabular data**
   - What we know: Telegram does not render HTML `<table>` tags. Message limit is 4096 chars.
   - What's unclear: Best visual formatting for portfolio summary in Telegram
   - Recommendation: Use `<pre>` blocks with fixed-width text alignment for table-like display. Keep to top-5 holdings and overall totals to stay within character limits.

## Plan Split Strategy

### Plan 1 (12-01): Backend + CLI + Tests
**Scope:** New modules (`report.py`, `notify.py`), CLI subcommands (`export`, `summary send`), unit tests.

**Tasks:**
1. Add xhtml2pdf dependency to pyproject.toml
2. Create `report.py`: HTML template generation, `html_to_pdf()`, `build_summary_text()`, `build_summary_html()`
3. Create `notify.py`: `send_telegram()`, `send_email()`, `send_summary()`
4. Add `crypto export --format pdf --output` subcommand to cli.py
5. Add `crypto summary send` subcommand to cli.py
6. Unit tests for report generation (HTML output, PDF bytes non-empty)
7. Unit tests for notify channels (mock httpx/smtplib, verify correct API calls)
8. Unit tests for CLI subcommand argument parsing

**Testing strategy:** Mock `get_top_coins_with_fallback`, `aggregate_portfolio`, httpx.post (for Telegram), smtplib.SMTP (for email). Verify PDF bytes are non-empty and start with `%PDF`. Verify HTML contains expected sections. Verify Telegram/email functions call correct endpoints with correct data.

### Plan 2 (12-02): Web API + React Frontend + Tests
**Scope:** FastAPI `/api/export/pdf` endpoint, React Download Report button, web tests.

**Tasks:**
1. Add `/api/export/pdf` endpoint to web.py returning StreamingResponse
2. Create `DownloadReport.jsx` component with download button
3. Add Download Report button to PortfolioPage.jsx
4. Web tests for `/api/export/pdf` endpoint (mock report generation, verify PDF response headers)

**Testing strategy:** Mock `generate_report_html` and `html_to_pdf` in web tests. Verify endpoint returns `application/pdf` content type. Verify Content-Disposition header includes filename.

## Sources

### Primary (HIGH confidence)
- [xhtml2pdf PyPI](https://pypi.org/project/xhtml2pdf/) - version 0.2.17, Python >=3.8, pure Python
- [xhtml2pdf Quickstart](https://xhtml2pdf.readthedocs.io/en/latest/quickstart.html) - CreatePDF API, BytesIO usage
- [xhtml2pdf Reference](https://xhtml2pdf.readthedocs.io/en/latest/reference.html) - Supported CSS properties
- [Telegram Bot API](https://core.telegram.org/bots/api) - sendMessage endpoint, parse_mode, 4096 char limit
- [FastAPI Custom Response](https://fastapi.tiangolo.com/advanced/custom-response/) - StreamingResponse for PDF
- [Python smtplib docs](https://docs.python.org/3/library/smtplib.html) - STARTTLS, login, sendmail
- [Python email.mime docs](https://docs.python.org/3/library/email.mime.html) - MIMEMultipart, MIMEText

### Secondary (MEDIUM confidence)
- [Real Python: Sending Emails](https://realpython.com/python-send-email/) - STARTTLS best practices, ssl.create_default_context()
- [PDFBolt Python HTML-to-PDF Comparison](https://pdfbolt.com/blog/python-html-to-pdf-library) - weasyprint vs xhtml2pdf tradeoffs

### Tertiary (LOW confidence)
- None -- all findings verified with primary or secondary sources.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - xhtml2pdf is well-documented, pure Python, version verified on PyPI
- Architecture: HIGH - follows established project patterns (argparse CLI, FastAPI endpoints, dataclass models)
- Pitfalls: HIGH - xhtml2pdf CSS limitations and Telegram message limits are well-documented
- Notification channels: HIGH - Telegram Bot API and smtplib are stable, mature APIs

**Research date:** 2026-03-08
**Valid until:** 2026-04-08 (30 days -- stable libraries, no fast-moving components)
