---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
status: in_progress
last_updated: "2026-03-07T13:27:00Z"
progress:
  total_phases: 13
  completed_phases: 6
  total_plans: 13
  completed_plans: 13
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-28)

**Core value:** Instant, glanceable crypto prices in the terminal — one command, no browser needed.
**Current focus:** Phase 10 in progress -- Exchange abstraction layer built, Plan 10-01 complete. Plan 10-02 (web integration) next.

## Current Position

Phase: 10 of 13 (Multi-Exchange Support) -- IN PROGRESS
Plan: 1 of 2 complete
Status: Plan 10-01 complete -- ExchangeClient protocol, BinanceClient, auto-fallback, CLI --exchange flag, 168 tests passing
Last activity: 2026-03-07 -- Plan 10-01 verified, all 168 tests passing

Progress: [█████-----] 50% (Phase 10)

## Performance Metrics

**Velocity:**
- Total plans completed: 13
- Average duration: 3 min
- Total execution time: ~42 min

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1. Project Setup | 1 | 5 min | 5 min |
| 2. API Integration | 1 | 2 min | 2 min |
| 3. CLI and Display | 2 | 4 min | 2 min |
| 4. Web Dashboard | 2 | 2 min | 1 min |
| 6. Portfolio Tracking | 1 | 3 min | 3 min |
| 7. Price Alerts | 1 | 2 min | 2 min |
| 8. Historical Charts | 2 | 8 min | 4 min |
| 9. React Frontend | 2 | 8 min | 4 min |
| 10. Multi-Exchange | 1 | 7 min | 7 min |

**Recent Trend:**
- Last 5 plans: 5 min, 3 min, 5 min, 3 min, 7 min
- Trend: Fast execution

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- All: Bitvavo public API (no auth), EUR-only, uv tooling, dynamic top-N ranking, configurable refresh interval
- 01-01: Used hatchling build backend with explicit src/ layout in [tool.hatch.build.targets.wheel]
- 01-01: CLI registers all three subcommand stubs (prices, watch, info) upfront at import time
- 01-01: uv installed via official installer (was not pre-installed); use absolute path /home/james-turing/.local/bin/uv
- 02-01: volumeQuote (24h EUR trading volume) used as market cap proxy — Bitvavo public API does not expose market cap data
- 02-01: httpx chosen as HTTP client with 10-second timeout and custom User-Agent header
- 02-01: Entries with open=0 skipped to avoid ZeroDivisionError in 24h change computation
- 02-01: CoinData uses slots=True for memory efficiency
- 03-01: Console injection pattern — optional Console param lets tests capture rich output via StringIO
- 03-01: Per-cell rich color markup for 24h change column (green for positive, red for negative)
- 03-01: rich.box.SIMPLE used for coin detail view (clean borderless label/value layout)
- 03-01: uv sync removes dev extras — must use uv sync --extra dev to retain pytest
- 03-02: argparse retained (no click/typer) — stdlib only for CLI parsing
- 03-02: cmd_watch catches HTTP errors inside the loop — one failed refresh does not kill the session
- 03-02: cmd_info fetches top 100 coins to maximise symbol lookup coverage
- 03-02: ANSI escape (\033[2J\033[H) used for screen clearing in watch mode — no external dep needed
- 04-01: create_app() factory for testable FastAPI app; dataclasses.asdict() for serialization
- 04-01: Lazy import of run_server inside cmd_web to keep CLI startup fast
- 04-01: Static mount guarded by directory existence check
- 04-02: Single self-contained HTML file with inline CSS + JS — no build tools
- 04-02: nl-NL locale for EUR number formatting
- 04-02: 1-second countdown tick for visible refresh timer
- 06-01: stdlib sqlite3 only -- no ORM, no new dependencies
- 06-01: Connection-per-call with try/finally close for CLI/web concurrency safety
- 06-01: WAL journal mode set on every connection open
- 06-01: XDG_DATA_HOME with fallback to ~/.local/share for DB path
- 06-01: Row factory returns Holding instances directly from queries
- 06-01: Unpriced coins included at cost basis in total_value
- 08-01: pytest-httpx v0.36.0 requires full URL with query params for strict matching
- 08-01: Rich bold markup splits numeric-prefixed labels ("7-Day") with ANSI codes; tests check parts separately
- 08-02: Plotly CDN v3.4.0 pinned (not plotly-latest which is frozen at v1.58.5)
- 08-02: Chart placed inside existing coin detail modal, not a new tab; line chart only (closing prices)
- 08-02: Modal widened from 400px to 600px for chart space; Plotly.purge() on close for memory cleanup
- 07-01: alerts_db.py imports portfolio_db as module (not from-import) so test patches propagate
- 07-01: Both alerts and holdings tables share the same SQLite DB file
- 07-01: check_alerts() is pure -- no DB side effects, caller handles mark_triggered
- 07-01: Race condition guard: UPDATE WHERE status='active' prevents double-triggering
- 07-01: Direction validated in Python (ValueError) AND via SQLite CHECK constraint
- 07-01: get_all_alerts orders active-first then triggered for display readiness
- 09-01: FastAPI EventSourceResponse for SSE (built-in since 0.135.0, no extra dependency)
- 09-01: SPA catch-all replaces both old @app.get("/") and app.mount("/static")
- 09-01: Import from 'react-router' not 'react-router-dom' (React Router v7)
- 09-01: Tailwind v4 CSS-first @theme config (no tailwind.config.js)
- 09-01: Updated 13 old HTML-content tests to 4 new SPA-appropriate tests
- 09-02: useApi hook shared across all CRUD forms for consistent fetch wrapper usage
- 09-02: PortfolioTable uses inline lots expansion (click row to toggle) rather than separate modal
- 09-02: Toast notifications use module-level counter for unique IDs, seenAlertIds ref prevents duplicates
- 09-02: AlertsPage reads and immediately clears URL symbol param for clean browser history
- 10-01: ExchangeClient protocol with name property, get_top_coins, context manager
- 10-01: BinanceClient USDT-to-EUR via Binance EURUSDT inverse rate, FX cached 5 min with time.monotonic
- 10-01: get_top_coins_with_fallback returns (coins, source_name) tuple for source labeling
- 10-01: Stablecoins filtered from Binance: USDC, BUSD, DAI, TUSD, FDUSD, USDD, USDP
- 10-01: render_price_table shows "via {source}" as Rich table caption with dim style
- 10-01: CLI --exchange flag on prices, watch, info, web, chart subcommands (default: bitvavo)

### Pending Todos

None.

### Roadmap Evolution

- 2026-03-06: Added Phase 7 (Price Alerts) — target price notifications via CLI and web alerts panel, SQLite storage
- 2026-03-06: Added Phase 8 (Historical Charts) — 7d/30d price history with ASCII sparklines in CLI and Plotly charts in web dashboard
- 2026-03-06: Added Phase 9 (React Frontend) — Replace static HTML/JS dashboard with Vite + React + Tailwind app, real-time updates via WebSocket/SSE
- 2026-03-06: Added Phase 10 (Multi-Exchange Support) — Abstract exchange layer, add Binance as second source, auto-fallback, --exchange CLI flag
- 2026-03-06: Added Phase 11 (Watchlist & Tags) — Tag coins by category (DeFi, Layer1, Meme), filter by tag, persistent watchlist separate from portfolio
- 2026-03-06: Added Phase 12 (Export & Reporting) — Export portfolio to CSV/PDF, weekly summary email or Telegram message, `crypto export --format pdf`
- 2026-03-06: Added Phase 13 (Mobile PWA) — Progressive Web App with manifest, service worker, offline support, install-to-home-screen


### Blockers/Concerns

None.

## Session Continuity

Last session: 2026-03-07
Stopped at: Completed 10-01-PLAN.md -- Exchange abstraction layer, BinanceClient, auto-fallback, CLI --exchange flag, 168 tests passing
Resume file: None
