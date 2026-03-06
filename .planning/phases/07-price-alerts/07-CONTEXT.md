# Phase 7: Price Alerts — Context

**Discussed:** 2026-03-06
**Phase goal:** Let users set target prices for coins and get notified when hit. Store alerts in SQLite alongside portfolio. CLI: `crypto alert add BTC 100000 --above`, web: alerts panel.

## Locked Decisions

### 1. Alert Checking Model
- **Passive only** — alerts are checked every time prices are fetched (during `crypto prices`, `crypto watch`, web dashboard auto-refresh)
- No background daemon or separate polling process
- **CLI banner** — when `crypto prices` or `crypto watch` detects a triggered alert, show a colored banner above the price table plus an inline marker on the affected row
- **Flash once in watch mode** — alert banner appears on the refresh cycle when it triggers; subsequent refreshes don't repeat it (marked as triggered in DB)
- **`crypto alert check` command** — standalone command that fetches prices, checks all active alerts, prints triggered ones. Exit code 1 if any alerts fired, exit 0 if none. Useful for scripting/cron.

### 2. Alert Conditions & Types
- **Above/below only** — simple absolute price targets. No percentage-change alerts.
- **One-shot** — alert triggers once, gets marked as "triggered" with a timestamp, stops checking. User can re-create if needed.
- **CLI syntax:** `crypto alert add BTC 100000 --above` (explicit direction flag, default `--above` if omitted)
- **`crypto alert list`** — shows active alerts first, then triggered alerts below with a separator. Both sections always visible.
- **`crypto alert remove <ID>`** — removes an alert by ID

### 3. Notification Experience
- **CLI:** Both colored banner above table AND inline marker (e.g., warning symbol) on the triggered coin's row. Uses rich formatting.
- **Web:** Toast notification that auto-dismisses after ~10 seconds. Visual only, no sound, no browser Notification API.
- **Exit codes:** `crypto alert check` uses exit 1 on trigger, exit 0 on no triggers.

### 4. Alerts Panel Layout (Web)
- **New tab** — "Alerts" tab alongside "Prices" (and future "Portfolio"). Consistent with phase 6 tab pattern.
- **Two entry points for creating alerts:**
  - Form on the alerts tab: coin dropdown, price input, above/below toggle, "Add Alert" button
  - "Set Alert" button in the existing coin detail modal (pre-fills symbol)
- **Tab layout:** Two sections with headers — "Active Alerts" on top (with remove buttons), "Triggered Alerts" below (with trigger timestamps)
- **Cleanup:** Individual delete button per alert + "Clear All Triggered" bulk button

## Claude's Discretion

- SQLite schema design for alerts table (columns, constraints, indexes)
- Alert checking logic integration point (where in the price-fetch flow to inject the check)
- Toast notification CSS/JS implementation details
- Rich formatting specifics for CLI banner and inline markers
- API endpoint design (routes, request/response shapes)
- How the coin dropdown in the web form is populated

## Code Context

### Existing Patterns to Follow
- **SQLite storage:** Phase 6 establishes `~/.local/share/crypto-tracker/portfolio.db` with WAL mode, `CREATE TABLE IF NOT EXISTS`, connection-per-call pattern. Alerts table goes in the same DB file.
- **CLI subcommands:** argparse nested subparsers in `cli.py`. `crypto alert` gets sub-subcommands: `add`, `list`, `remove`, `check`.
- **Web endpoints:** FastAPI with Pydantic request models. Follow existing `/api/prices` and `/api/coin/{symbol}` patterns.
- **Frontend:** Single-file `index.html` with inline CSS/JS. Tab switching pattern from phase 6.
- **Display:** Rich library for terminal output. Console injection pattern for testable output.
- **Data models:** `@dataclass(slots=True)` in `models.py`.

### Key Files to Modify
- `src/crypto_price_tracker/models.py` — add `PriceAlert` dataclass
- `src/crypto_price_tracker/cli.py` — add `alert` subcommand group
- `src/crypto_price_tracker/web.py` — add alert API endpoints
- `src/crypto_price_tracker/static/index.html` — add alerts tab, toast, modal button
- New: `src/crypto_price_tracker/alerts_db.py` — SQLite CRUD for alerts
- New: `src/crypto_price_tracker/alerts.py` — alert checking logic

### Integration Points
- Alert checking hooks into `get_top_coins()` calls in `cmd_prices()`, `cmd_watch()`, and web `/api/prices` endpoint
- Shares the same SQLite DB as portfolio (phase 6)
- Coin detail modal in `index.html` gets a new "Set Alert" button

## Deferred Ideas

None captured during discussion.
