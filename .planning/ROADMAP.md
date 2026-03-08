# Roadmap: Crypto Price Tracker

## Overview

Three phases to deliver a working CLI tool: scaffold the project so the `crypto` command exists, wire up the Bitvavo API so live EUR price data flows in, then build the three subcommands with formatted color-coded output. Each phase completes a coherent capability and unblocks the next.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Project Setup** - uv project scaffold with installable `crypto` entry point (completed 2026-03-01)
- [x] **Phase 2: API Integration** - Live EUR crypto prices fetched from the public Bitvavo REST API (completed 2026-03-01)
- [x] **Phase 3: CLI and Display** - All three subcommands working with formatted, color-coded terminal output (completed 2026-03-01)
- [x] **Phase 4: Web Dashboard** - Browser-based auto-refreshing price dashboard started with `crypto web` (completed 2026-03-05)
- [ ] **Phase 5: Web UX** - Auto-refresh countdown timer and manual refresh button
- [ ] **Phase 6: Portfolio Tracking** - Portfolio tracking for the crypto tracker
- [ ] **Phase 7: Price Alerts** - Target price notifications via CLI and web alerts panel
- [x] **Phase 8: Historical Charts** - 7d/30d price history with ASCII sparklines in CLI and Plotly charts in web dashboard (completed 2026-03-06)
- [x] **Phase 9: React Frontend** - Replace static HTML/JS dashboard with Vite + React + Tailwind app with real-time updates (completed 2026-03-07)
- [ ] **Phase 10: Multi-Exchange Support** - Abstract the exchange layer with Binance as second source, auto-fallback, and `--exchange` CLI flag
- [ ] **Phase 11: Watchlist & Tags** - Tag coins (DeFi, Layer1, Meme) and filter by tag; persistent watchlist separate from portfolio
- [ ] **Phase 12: Export & Reporting** - Export portfolio to CSV/PDF; weekly summary email or Telegram message; `crypto export --format pdf`
- [ ] **Phase 13: Mobile PWA** - Progressive Web App with manifest, service worker, offline support, and install-to-home-screen

## Phase Details

### Phase 1: Project Setup
**Goal**: A working Python project where `crypto` is an installable command that runs without error
**Depends on**: Nothing (first phase)
**Requirements**: SETUP-01, SETUP-02
**Success Criteria** (what must be TRUE):
  1. Running `uv sync` installs the project and all dependencies without error
  2. Running `crypto --help` after install shows the command exists and prints usage
  3. The project has a pyproject.toml with a `[project.scripts]` entry point — no setup.py or requirements.txt
**Plans**: 1 plan

Plans:
- [x] 01-01-PLAN.md — Scaffold uv project with pyproject.toml, entry point, and minimal CLI skeleton

### Phase 2: API Integration
**Goal**: Live EUR cryptocurrency price data flows from the public Bitvavo REST API into the application
**Depends on**: Phase 1
**Requirements**: API-01, API-02, API-03
**Success Criteria** (what must be TRUE):
  1. Calling the Bitvavo API client returns current prices denominated in EUR
  2. The top N coins (default 20) are fetched and sorted by market cap
  3. API calls require no authentication or API key
  4. Price, 24h change %, market cap, and volume are all retrievable for each coin
**Plans**: 1 plan

Plans:
- [x] 02-01-PLAN.md — Build Bitvavo API client with data models, EUR filtering, volume-based sorting, and unit tests

### Phase 3: CLI and Display
**Goal**: Users can run all three subcommands and see formatted, color-coded crypto prices in the terminal
**Depends on**: Phase 2
**Requirements**: CLI-01, CLI-02, CLI-03, DISP-01, DISP-02, DISP-03
**Success Criteria** (what must be TRUE):
  1. `crypto prices` prints a formatted table of the top 20 coins with price, 24h change %, market cap, and volume, then exits
  2. `crypto watch` refreshes the price table every 30 seconds by default; `--interval N` overrides the refresh period
  3. `crypto info BTC` shows a detailed single-coin view with expanded information
  4. Positive 24h change is displayed in green and negative in red in the terminal
**Plans**: 2 plans

Plans:
- [x] 03-01-PLAN.md — Build terminal table renderer and single-coin detail view using rich library
- [x] 03-02-PLAN.md — Implement `prices`, `watch`, and `info` subcommands wired to the API client and display module

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12 → 13

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Project Setup | 1/1 | Complete   | 2026-03-01 |
| 2. API Integration | 1/1 | Complete   | 2026-03-01 |
| 3. CLI and Display | 2/2 | Complete   | 2026-03-01 |
| 4. Web Dashboard | 2/2 | Complete | 2026-03-05 |
| 5. Web UX | 0/1 | Planned | — |
| 6. Portfolio Tracking | 1/2 | In Progress | — |
| 7. Price Alerts | 1/2 | In Progress | — |
| 8. Historical Charts | 2/2 | Complete | 2026-03-06 |
| 9. React Frontend | 2/2 | Complete | 2026-03-07 |
| 10. Multi-Exchange Support | 1/2 | In Progress | — |
| 11. Watchlist & Tags | 1/2 | In Progress | — |
| 12. Export & Reporting | 0/0 | Planned | — |
| 13. Mobile PWA | 0/2 | Planned | — |

### Phase 4: Web Dashboard
**Goal**: A browser-based dashboard that displays live, auto-refreshing cryptocurrency prices from the Bitvavo API, started with a single `crypto web` command
**Depends on**: Phase 3
**Requirements**: WEB-01, WEB-02, WEB-03, WEB-04
**Success Criteria** (what must be TRUE):
  1. `crypto web` starts a web server that serves the dashboard at http://localhost:8000
  2. Opening the dashboard in a browser shows a price table matching the CLI output (rank, symbol, name, EUR price, 24h change %, volume)
  3. The dashboard auto-refreshes prices every 30 seconds without manual page reload
  4. Clicking a coin row shows a detail view with expanded information for that coin
  5. Positive 24h changes are green and negative changes are red in the browser
**Plans**: 2 plans

Plans:
- [x] 04-01-PLAN.md — Add FastAPI web server with JSON API endpoints and `crypto web` CLI subcommand
- [x] 04-02-PLAN.md — Build HTML/CSS/JS frontend with auto-refreshing price table and coin detail modal

### Phase 5: Web UX - Add auto-refresh countdown timer and manual refresh button to the web dashboard HTML. Pure frontend change to static/index.html.

**Goal**: User sees a live countdown timer and a manual refresh button on the web dashboard, giving visibility into when the next auto-refresh happens and control to refresh on demand
**Depends on**: Phase 4
**Requirements**: UX-01, UX-02
**Success Criteria** (what must be TRUE):
  1. The dashboard subtitle area shows a countdown timer that decrements every second from 30 to 0
  2. When the countdown reaches 0, prices auto-refresh and the countdown resets to 30
  3. A "Refresh" button is visible next to the countdown timer
  4. Clicking the "Refresh" button immediately fetches fresh prices and resets the countdown
  5. Existing table, modal, and color coding remain unchanged
**Plans**: 1 plan

Plans:
- [ ] 05-01-PLAN.md — Add countdown timer, refresh button, and 1-second tick interval to index.html

### Phase 6: Portfolio Tracking

**Goal:** Add portfolio tracking with holdings CRUD, P&L aggregation, and CSV/JSON export to both CLI and web surfaces, using SQLite for persistence
**Depends on:** Phase 5
**Requirements**: PORT-01, PORT-02, PORT-03, PORT-04, PORT-05, PORT-06, PORT-07, PORT-08
**Success Criteria** (what must be TRUE):
  1. `crypto portfolio add BTC 0.5 45000` adds a holding to SQLite DB at `~/.local/share/crypto-tracker/portfolio.db`
  2. `crypto portfolio list` shows aggregated per-coin view with total amount, avg buy price, current value, P&L (EUR + %), allocation %
  3. `crypto portfolio lots BTC` shows individual lots with IDs, buy prices, dates
  4. `crypto portfolio remove <ID>` removes a holding by lot ID
  5. `crypto portfolio edit <ID> --amount 0.3` edits a holding by lot ID
  6. `crypto portfolio export --format csv|json` exports holdings
  7. Web dashboard has a "Portfolio" tab with same data + add holding form
  8. Summary footer shows total portfolio value and total P&L
  9. Coins not in top 100 show "N/A" for current price and P&L
**Plans**: 2 plans

Plans:
- [x] 06-01-PLAN.md — Backend storage layer (SQLite CRUD), aggregation service (P&L calculations), export (CSV/JSON), and unit tests
- [ ] 06-02-PLAN.md — CLI portfolio subcommands, Rich display, FastAPI CRUD endpoints, HTML portfolio tab, and integration tests

### Phase 7: Price Alerts

**Goal:** Let users set target prices for coins and get notified when hit. Store alerts in SQLite alongside portfolio. CLI: `crypto alert add BTC 100000 --above`, web: alerts panel with toast notifications.
**Depends on:** Phase 6
**Requirements**: ALERT-01, ALERT-02, ALERT-03, ALERT-04, ALERT-05, ALERT-06, ALERT-07
**Success Criteria** (what must be TRUE):
  1. `crypto alert add BTC 100000 --above` creates an alert stored in SQLite
  2. `crypto alert list` shows active alerts first, then triggered alerts
  3. `crypto alert remove <ID>` removes an alert by ID
  4. `crypto alert check` fetches prices, checks all active alerts, prints triggered ones, exits 1 if any triggered, 0 if none
  5. When `crypto prices` or `crypto watch` detects a triggered alert, a colored banner appears above the price table plus inline marker on affected row
  6. In watch mode, alert banner appears once (flash once), then marked as triggered
  7. Web dashboard has "Alerts" tab with add alert form, active/triggered sections, remove/clear buttons
  8. Web coin detail modal has "Set Alert" button
  9. Toast notification on web when alert triggers (auto-dismiss ~10s, no sound)
**Plans**: 2 plans

Plans:
- [x] 07-01-PLAN.md — Backend: PriceAlert model, alerts_db.py (SQLite CRUD), alerts.py (checking logic), and unit tests
- [ ] 07-02-PLAN.md — Integration: CLI alert subcommands, display functions (banner + alert list + modified price table), web API endpoints, HTML alerts tab + toast + modal button, and integration tests

### Phase 8: Historical Charts

**Goal:** Show 7d/30d price history with ASCII sparklines in CLI (`crypto chart`) and interactive Plotly charts in web dashboard coin modal. Use Bitvavo candles endpoint.
**Depends on:** Phase 7
**Requirements**: CHART-01, CHART-02, CHART-03, CHART-04, CHART-05, CHART-06
**Success Criteria** (what must be TRUE):
  1. `crypto chart` shows a compact sparkline overview table for all top 20 coins with 7d and 30d Unicode sparklines
  2. `crypto chart BTC` shows a detailed single-coin view with sparklines + stats (open, close, high, low, change %) for both timeframes
  3. Sparklines use Unicode block characters and stats are color-coded green/red
  4. Web coin detail modal includes an interactive Plotly line chart below the coin info
  5. 7D/30D toggle buttons switch between timeframes in the web chart, defaulting to 7D
  6. `/api/candles/{symbol}` endpoint returns OHLCV candle data from Bitvavo in chronological order
**Plans**: 2 plans

Plans:
- [x] 08-01-PLAN.md — Backend + CLI: Candle model, API candle fetching, sparkline rendering, chart CLI subcommand, and tests
- [x] 08-02-PLAN.md — Web dashboard: candle API endpoint, Plotly CDN integration, chart in coin modal with 7D/30D toggle, and tests

### Phase 9: React Frontend

**Goal:** Replace the monolithic 814-line static HTML/JS dashboard with a Vite + React + Tailwind app. SSE for real-time price updates (10s interval). Recharts for charts. React Router for SPA navigation. Same GitHub-dark theme. Keep FastAPI backend unchanged except SSE endpoint and SPA catch-all.
**Depends on:** Phase 8
**Requirements**: REACT-01, REACT-02, REACT-03, REACT-04, REACT-05, REACT-06, REACT-07, REACT-08, REACT-09, REACT-10, REACT-11, REACT-12
**Success Criteria** (what must be TRUE):
  1. Vite + React + Tailwind project in `frontend/` builds successfully with `npm run build`
  2. SSE endpoint at `/api/prices/stream` pushes price + triggered alert data every 10 seconds
  3. React Router provides URL-based navigation at `/`, `/portfolio`, `/alerts` with top tab bar
  4. Prices tab auto-updates via SSE with countdown timer and manual refresh button
  5. Clicking a coin row opens a modal with coin details and Recharts line chart (7D/30D toggle)
  6. Portfolio tab has add holding form, aggregated table, lots toggle, delete, and summary footer
  7. Alerts tab has add alert form, active/triggered sections, remove individual and clear all
  8. Set Alert button in coin modal navigates to alerts tab with symbol pre-filled
  9. Toast notifications appear when SSE reports triggered alerts (auto-dismiss ~10s)
  10. GitHub-dark theme applied: #0d1117 bg, #161b22 cards, monospace font, nl-NL EUR formatting
  11. Vite build output replaces `src/crypto_price_tracker/static/index.html`
  12. FastAPI SPA catch-all route serves React app at all non-API paths
**Plans**: 2 plans

Plans:
- [x] 09-01-PLAN.md — Backend SSE endpoint + SPA catch-all, Vite scaffold, core React shell (Router, layout, PricesPage with SSE, CoinModal with Recharts chart)
- [x] 09-02-PLAN.md — PortfolioPage + AlertsPage with full CRUD, toast notifications, build integration, test updates

### Phase 10: Multi-Exchange Support

**Goal:** Abstract the exchange layer. Add Binance as second source alongside Bitvavo. Auto-fallback if one is down. CLI flag `--exchange binance`.
**Depends on:** Phase 9
**Requirements**: EXCH-01, EXCH-02, EXCH-03, EXCH-04, EXCH-05, EXCH-06, EXCH-07, EXCH-08, EXCH-09
**Success Criteria** (what must be TRUE):
  1. ExchangeClient protocol with BitvavoClient and BinanceClient implementations
  2. BinanceClient fetches USDT pairs and converts to EUR via Binance USDT-EUR rate (cached 5 min)
  3. `get_top_coins_with_fallback()` tries primary exchange, falls back to other on failure
  4. CLI `--exchange bitvavo|binance` flag on prices, watch, info, web, chart subcommands
  5. Web API endpoints accept `?exchange=bitvavo|binance` query param
  6. React nav has exchange dropdown; changing it reconnects SSE with new exchange
  7. Source label ("via Bitvavo" / "via Binance") shown on CLI and web
  8. Candle/chart data always from Bitvavo regardless of exchange selection
**Plans**: 2 plans

Plans:
- [x] 10-01-PLAN.md — Exchange abstraction layer, BinanceClient, auto-fallback, CLI --exchange flag, unit tests
- [ ] 10-02-PLAN.md — Web API ?exchange= param, React exchange dropdown, SSE reconnect, web tests

### Phase 11: Watchlist & Tags

**Goal:** Let users tag coins (DeFi, Layer1, Meme) and filter by tag. Persistent watchlist separate from portfolio. CLI: `crypto watchlist add ETH --tag defi`, web: Watchlist tab with tag filter pills.
**Depends on:** Phase 10
**Requirements**: WATCH-01, WATCH-02, WATCH-03, WATCH-04, WATCH-05, WATCH-06, WATCH-07, WATCH-08, WATCH-09, WATCH-10
**Success Criteria** (what must be TRUE):
  1. `crypto watchlist add ETH --tag defi` adds ETH to the watchlist with the DeFi tag
  2. `crypto watchlist list` shows all watchlist entries with live prices, tags, and 24h change
  3. `crypto watchlist list --tag defi` filters to only show entries tagged DeFi
  4. `crypto watchlist remove ETH` removes ETH from the watchlist
  5. `crypto watchlist tag ETH --tag layer1` updates tags on an existing entry
  6. `crypto prices --watchlist` filters the price table to only show watched symbols
  7. Watchlist data persists in the same SQLite DB as portfolio and alerts
  8. Web dashboard has a "Watchlist" tab with tag filter pills and watchlist table
  9. Star icon on Prices tab rows toggles watchlist membership
  10. GET/POST/DELETE /api/watchlist endpoints work correctly
**Plans**: 2 plans

Plans:
- [x] 11-01-PLAN.md — Backend: WatchlistEntry model, watchlist_db.py (SQLite CRUD), render_watchlist_table, CLI watchlist subcommands, --watchlist flag, unit tests
- [ ] 11-02-PLAN.md — Web: FastAPI watchlist endpoints, WatchlistPage with tag pills, PriceTable star icon, App routing, web tests

### Phase 12: Export & Reporting

**Goal:** Export portfolio to CSV/PDF. Generate a weekly summary email (or Telegram message). `crypto export --format pdf`.
**Depends on:** Phase 11
**Requirements**: TBD
**Plans:** 0 plans

Plans:
- [ ] TBD (run /gsd:plan-phase 12 to break down)

### Phase 13: Mobile PWA

**Goal:** Make the web dashboard a Progressive Web App. Add manifest, service worker, offline support. Install to home screen on phone.
**Depends on:** Phase 12
**Requirements**: PWA-01, PWA-02, PWA-03, PWA-04, PWA-05, PWA-06, PWA-07, PWA-08, PWA-09, PWA-10
**Success Criteria** (what must be TRUE):
  1. `npm run build` generates manifest.json and sw.js in the static output directory
  2. Chrome DevTools > Application > Manifest shows "Installable" with no errors
  3. Clicking "Install" button in header triggers the browser install prompt (Chrome/Edge)
  4. With network offline, app shell loads and shows last-known prices/portfolio from cache
  5. An offline banner appears when disconnected; disappears when reconnected
  6. SSE price streaming continues to work normally (not intercepted by service worker)
  7. All existing 265+ tests continue to pass
**Plans**: 2 plans

Plans:
- [ ] 13-01-PLAN.md — PWA infrastructure: vite-plugin-pwa, manifest, service worker, icons, meta tags
- [ ] 13-02-PLAN.md — Offline UX + install button: React hooks, offline banner, install button, tests
