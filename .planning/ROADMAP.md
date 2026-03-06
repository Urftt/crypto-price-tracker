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
- [ ] **Phase 8: Historical Charts** - 7d/30d price history with ASCII sparklines in CLI and Plotly charts in web dashboard
- [ ] **Phase 9: React Frontend** - Replace static HTML/JS dashboard with Vite + React + Tailwind app with real-time updates
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
| 7. Price Alerts | 0/2 | Planned | — |
| 8. Historical Charts | 0/0 | Planned | — |
| 9. React Frontend | 0/0 | Planned | — |
| 10. Multi-Exchange Support | 0/0 | Planned | — |
| 11. Watchlist & Tags | 0/0 | Planned | — |
| 12. Export & Reporting | 0/0 | Planned | — |
| 13. Mobile PWA | 0/0 | Planned | — |

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
- [ ] 07-01-PLAN.md — Backend: PriceAlert model, alerts_db.py (SQLite CRUD), alerts.py (checking logic), and unit tests
- [ ] 07-02-PLAN.md — Integration: CLI alert subcommands, display functions (banner + alert list + modified price table), web API endpoints, HTML alerts tab + toast + modal button, and integration tests

### Phase 8: Historical Charts

**Goal:** Show 7d/30d price history. ASCII sparklines in CLI (`crypto chart BTC`), interactive Plotly chart in web dashboard. Use Bitvavo candles endpoint.
**Depends on:** Phase 7
**Requirements**: TBD
**Plans:** 0 plans

Plans:
- [ ] TBD (run /gsd:plan-phase 8 to break down)

### Phase 9: React Frontend

**Goal:** Replace the static HTML/JS dashboard with a proper React app. Vite + React + Tailwind. Real-time updates via WebSocket or SSE. Keep FastAPI backend.
**Depends on:** Phase 8
**Requirements**: TBD
**Plans:** 0 plans

Plans:
- [ ] TBD (run /gsd:plan-phase 9 to break down)

### Phase 10: Multi-Exchange Support

**Goal:** Abstract the exchange layer. Add Binance as second source alongside Bitvavo. Auto-fallback if one is down. CLI flag `--exchange binance`.
**Depends on:** Phase 9
**Requirements**: TBD
**Plans:** 0 plans

Plans:
- [ ] TBD (run /gsd:plan-phase 10 to break down)

### Phase 11: Watchlist & Tags

**Goal:** Let users tag coins (DeFi, Layer1, Meme) and filter by tag. Persistent watchlist separate from portfolio. CLI: `crypto watch add ETH`, web: tag filters.
**Depends on:** Phase 10
**Requirements**: TBD
**Plans:** 0 plans

Plans:
- [ ] TBD (run /gsd:plan-phase 11 to break down)

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
**Requirements**: TBD
**Plans:** 0 plans

Plans:
- [ ] TBD (run /gsd:plan-phase 13 to break down)
