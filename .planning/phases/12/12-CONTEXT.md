# Phase 12 Context: Export & Reporting

**Phase Goal:** Export portfolio to CSV/PDF. Generate a weekly summary via email or Telegram. `crypto export --format pdf`.

## Decisions

### 1. Export Scope & Command Structure

| Decision | Choice |
|----------|--------|
| Command structure | **Both** — keep `crypto portfolio export` for raw data (csv/json), add new top-level `crypto export` for rich reports (pdf) |
| Data scope | **Full report** — portfolio P&L + current top-N price table + watchlist + active alerts |
| Price data | **Live fetch at export time** — calls exchange API when the command runs, includes real-time prices and P&L |
| Output | **Optional `--output` flag** — `crypto export --format pdf --output report.pdf`. Defaults to auto-named file for PDF |

**Rationale:** Separating the commands keeps `crypto portfolio export` simple for data interchange (csv/json piping) while `crypto export` serves as a comprehensive reporting tool. Live price fetch ensures the report reflects current market state at the moment of generation.

### 2. PDF Report Content & Styling

| Decision | Choice |
|----------|--------|
| Sections | **Summary + Portfolio + Prices** — header with date/time, portfolio summary (total value, P&L), holdings table, top-N price table |
| PDF library | **HTML-to-PDF** — generate HTML tables, convert with a lightweight library (weasyprint or xhtml2pdf). Easy to style. |
| Styling | **Minimal with color** — clean tables with green/red P&L coloring matching CLI/web theme. Dark header row. No logo or heavy design. |
| Web download | **Yes** — add `/api/export/pdf` endpoint. Web dashboard gets a Download Report button. |

**Rationale:** HTML-to-PDF is the simplest approach — reuse HTML/CSS skills, easy to iterate on layout. Minimal color styling keeps the report professional while matching the existing green/red P&L convention. Web endpoint makes reports accessible without CLI.

### 3. Weekly Summary Delivery

| Decision | Choice |
|----------|--------|
| Channels | **Both** — Telegram bot and email via SMTP. User picks one or both via config. |
| Summary data | **Portfolio P&L changes** — total portfolio value, week-over-week change, top gainers/losers from holdings |
| Scheduling | **Manual `crypto summary send` command** — user runs when they want. Can be cron-scheduled externally. Simplest. |
| Config storage | **Environment variables** — `CRYPTO_TELEGRAM_TOKEN`, `CRYPTO_TELEGRAM_CHAT_ID`, `CRYPTO_SMTP_HOST`, etc. 12-factor style. |
| Send behavior | **Auto-send to all configured** — if Telegram env vars are set, send there. If SMTP is set, send email. Both if both configured. |

**Rationale:** Manual command + external cron keeps the tool simple without a background daemon. Environment variables follow 12-factor conventions and avoid another config file format. Auto-send to all configured channels removes friction — configure once, run one command.

## Code Context

### What gets modified
- **New: `src/crypto_price_tracker/report.py`** — HTML report generation, PDF conversion, summary data aggregation
- **New: `src/crypto_price_tracker/notify.py`** — Telegram and email notification channel implementations
- **`src/crypto_price_tracker/cli.py`** — add `export` top-level subcommand + `summary send` subcommand
- **`src/crypto_price_tracker/web.py`** — add `/api/export/pdf` endpoint
- **`frontend/src/`** — Download Report button (small addition to an existing page)

### What stays unchanged
- `src/crypto_price_tracker/portfolio.py` — existing `export_csv`/`export_json` stay as-is
- `src/crypto_price_tracker/portfolio_db.py`, `alerts_db.py`, `watchlist_db.py` — read-only consumers
- `src/crypto_price_tracker/exchange.py`, `api.py` — used for live price fetch, not modified
- `src/crypto_price_tracker/display.py` — CLI display, not related to export

### Key integration points
- `aggregate_portfolio()` from `portfolio.py` provides P&L data for the report
- `get_top_coins_with_fallback()` from `exchange.py` provides live prices at export time
- `get_all_watchlist_entries()` and `get_all_alerts()` provide watchlist/alert data for full report
- PDF endpoint follows same pattern as other API endpoints in `web.py` (FastAPI)
- `crypto portfolio export` (csv/json) remains unchanged — `crypto export` is a new top-level command
- Telegram uses `httpx` (already a dependency) to call the Bot API
- Email uses stdlib `smtplib` + `email.mime` — no new dependency
- HTML-to-PDF library (weasyprint or xhtml2pdf) is the only new dependency

### Environment variables for notifications
- `CRYPTO_TELEGRAM_TOKEN` — Telegram bot token from @BotFather
- `CRYPTO_TELEGRAM_CHAT_ID` — target chat/group ID
- `CRYPTO_SMTP_HOST` — SMTP server hostname
- `CRYPTO_SMTP_PORT` — SMTP port (default 587)
- `CRYPTO_SMTP_USER` — SMTP username
- `CRYPTO_SMTP_PASS` — SMTP password
- `CRYPTO_SMTP_FROM` — sender email address
- `CRYPTO_SMTP_TO` — recipient email address

## Deferred Ideas

None raised during discussion.

---
*Created: 2026-03-08 via /gsd:discuss-phase 12*
