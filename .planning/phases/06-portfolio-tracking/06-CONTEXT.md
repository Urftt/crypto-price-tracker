# Phase 6: Portfolio Tracking — Context

**Discussed:** 2026-03-06
**Phase goal:** Add portfolio tracking (holdings CRUD, P&L aggregation, export) to both CLI and web surfaces.

## Locked Decisions

### 1. Holdings Input
- **Both CLI and web** — `crypto portfolio add BTC 0.5 45000` in CLI, form on portfolio tab in web
- **Fields per holding:** symbol, amount, buy price (EUR), buy date (defaults to today)
- **Multiple lots per coin** — each purchase is a separate DB row
- **Operations:** add, remove (by lot ID), edit (by lot ID)

### 2. Data Persistence
- **SQLite database** at `~/.local/share/crypto-tracker/portfolio.db`
- **Single file** shared by CLI and web server (WAL mode for concurrency)
- **Export:** CSV and JSON formats via `crypto portfolio export --format csv|json`
- No import — export only

### 3. Portfolio Display — CLI
- **Default view: aggregated per coin** — one row per symbol showing total amount, avg buy price, current value, P&L (EUR + %), allocation %
- **Summary footer** — total portfolio value, total P&L in EUR and %
- **Lot detail via dedicated command:** `crypto portfolio lots BTC` — shows individual lots with IDs, buy prices, dates
- **Color coding:** green for positive P&L, red for negative — matches existing 24h change colors
- **Columns:** Symbol, Amount, Avg Buy, Value, P&L, %, Alloc

### 4. Portfolio Display — Web
- **New "Portfolio" tab** alongside "Prices" in existing `index.html`
- **Same aggregated view** as CLI: per-coin rows with expandable lots
- **Add holding form** on the portfolio tab
- **Summary totals** at the bottom

### 5. Coins Not in Top 100
- Show "N/A" for current price and P&L when a held coin is not in the Bitvavo top 100
- Include at cost basis in totals (not excluded, not fetched separately)

## Claude's Discretion

- SQLite library choice (stdlib `sqlite3` recommended by research)
- XDG path resolution approach (manual vs `platformdirs`)
- Export format details (CSV columns, JSON structure)
- CLI `portfolio` subcommand exact syntax and flags beyond what's locked above
- Web form layout and styling details
- API endpoint routes and request/response shapes
- Command feedback text after add/remove/edit operations

## Code Context

### Existing Patterns to Follow
- **Data models:** `@dataclass(slots=True)` in `models.py` (see `CoinData`)
- **API client:** `BitvavoClient` with context manager in `api.py`
- **CLI:** argparse with subparsers in `cli.py`, dispatch via if/elif
- **Web:** FastAPI `create_app()` factory in `web.py`, `dataclasses.asdict()` for JSON serialization
- **Frontend:** Single self-contained `index.html` with inline CSS/JS, nl-NL locale for EUR formatting
- **Display:** Rich library for terminal tables, console injection for testability
- **Tests:** pytest, `uv run pytest tests/ -x -q` for quick runs

### Key Files to Modify
- `src/crypto_price_tracker/models.py` — add `Holding` dataclass
- `src/crypto_price_tracker/cli.py` — add `portfolio` subcommand group with sub-subcommands
- `src/crypto_price_tracker/web.py` — add portfolio CRUD API endpoints
- `src/crypto_price_tracker/static/index.html` — add portfolio tab with form and table
- New: `src/crypto_price_tracker/portfolio_db.py` — SQLite storage layer
- New: `src/crypto_price_tracker/portfolio.py` — aggregation service, P&L calculations, export

### Integration Points
- Portfolio aggregation calls `get_top_coins()` to get current prices for P&L calculation
- CLI and web share the same SQLite DB file via WAL mode
- Web frontend reuses existing tab pattern (to be established in this phase)

## Deferred Ideas

None captured during discussion.
