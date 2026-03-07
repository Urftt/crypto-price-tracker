# Requirements: Crypto Price Tracker

**Defined:** 2026-02-28
**Core Value:** Instant, glanceable crypto prices in the terminal — one command, no browser needed.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### API (Data Fetching)

- [x] **API-01**: User can fetch current crypto prices from the public Bitvavo REST API
- [x] **API-02**: All prices are displayed in EUR via Bitvavo EUR trading pairs
- [x] **API-03**: Top N coins are fetched dynamically and sorted by market cap (default 20)

### Display (Terminal Output)

- [x] **DISP-01**: Prices are shown in a formatted terminal table with price, 24h change %, market cap, and volume
- [x] **DISP-02**: 24h change is color-coded green (positive) or red (negative)
- [x] **DISP-03**: Single-coin detail view shows expanded information for one cryptocurrency

### CLI (Commands & Interface)

- [x] **CLI-01**: `crypto prices` displays the price table once and exits
- [x] **CLI-02**: `crypto watch` auto-refreshes the price table (default 30s, configurable via `--interval`)
- [x] **CLI-03**: `crypto info <SYMBOL>` shows detailed info for a single coin

### Setup (Project Infrastructure)

- [x] **SETUP-01**: Project uses uv with pyproject.toml (no setup.py or requirements.txt)
- [x] **SETUP-02**: CLI is installable with a `crypto` entry point command

### Web Dashboard

- [ ] **WEB-01**: Web dashboard displays a price table matching the CLI output (rank, symbol, name, EUR price, 24h change %, volume)
- [ ] **WEB-02**: Dashboard auto-refreshes prices at a configurable interval (default 30s)
- [ ] **WEB-03**: Clicking a coin shows a detail view with expanded information
- [ ] **WEB-04**: Web server starts with a single `crypto web` command on a configurable port

### Web UX (Dashboard Enhancements)

- [ ] **UX-01**: Dashboard shows a countdown timer displaying seconds until the next auto-refresh
- [ ] **UX-02**: Dashboard has a manual refresh button that immediately reloads prices and resets the countdown

### Price Alerts

- [x] **ALERT-01**: SQLite CRUD for alerts: add, get active, get all, remove, mark triggered, clear triggered
- [x] **ALERT-02**: Pure alert checking logic: above/below price targets fire one-shot alerts
- [ ] **ALERT-03**: CLI subcommands: `crypto alert add/list/remove/check` with argparse
- [ ] **ALERT-04**: Web API endpoints: GET/POST/DELETE /api/alerts, modified /api/prices with triggered alerts
- [ ] **ALERT-05**: Rich CLI banner and inline markers render correctly when alerts trigger
- [ ] **ALERT-06**: Web HTML has alerts tab, toast notifications, coin dropdown, Set Alert modal button
- [ ] **ALERT-07**: `crypto alert check` exit code 1 on trigger, exit 0 on none (scriptable)

### React Frontend

- [x] **REACT-01**: Vite + React + Tailwind project in `frontend/` builds successfully with `npm run build`
- [x] **REACT-02**: SSE endpoint at `/api/prices/stream` pushes price + triggered alert data every 10 seconds
- [x] **REACT-03**: React Router provides URL-based navigation at `/`, `/portfolio`, `/alerts` with top tab bar
- [x] **REACT-04**: Prices tab auto-updates via SSE with countdown timer and manual refresh button
- [x] **REACT-05**: Clicking a coin row opens a modal with coin details and Recharts line chart (7D/30D toggle)
- [ ] **REACT-06**: Portfolio tab has add holding form, aggregated table, lots toggle, delete, and summary footer
- [ ] **REACT-07**: Alerts tab has add alert form, active/triggered sections, remove individual and clear all
- [ ] **REACT-08**: Set Alert button in coin modal navigates to alerts tab with symbol pre-filled
- [ ] **REACT-09**: Toast notifications appear when SSE reports triggered alerts (auto-dismiss ~10s)
- [x] **REACT-10**: GitHub-dark theme applied: #0d1117 bg, #161b22 cards, monospace font, nl-NL EUR formatting
- [ ] **REACT-11**: Vite build output replaces `src/crypto_price_tracker/static/index.html`
- [x] **REACT-12**: FastAPI SPA catch-all route serves React app at all non-API paths

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

(None yet)

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Authentication / private API endpoints | Public data only, no auth complexity |
| Extended stats (ATH, supply, 24h high/low) | Keep info view simple for v1 |
| Custom coin lists / watchlists | Dynamic ranking is sufficient |
| Portfolio tracking / balance management | This is a viewer only |
| USD or multi-currency support | EUR only |
| Mobile app | CLI and web only — no native mobile app |
| WebSocket streaming | REST API is sufficient for v1 refresh intervals |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| SETUP-01 | Phase 1 | Complete |
| SETUP-02 | Phase 1 | Complete |
| API-01 | Phase 2 | Complete |
| API-02 | Phase 2 | Complete |
| API-03 | Phase 2 | Complete |
| DISP-01 | Phase 3 | Complete |
| DISP-02 | Phase 3 | Complete |
| DISP-03 | Phase 3 | Complete |
| CLI-01 | Phase 3 | Complete |
| CLI-02 | Phase 3 | Complete |
| CLI-03 | Phase 3 | Complete |
| WEB-01 | Phase 4 | Planned |
| WEB-02 | Phase 4 | Planned |
| WEB-03 | Phase 4 | Planned |
| WEB-04 | Phase 4 | Planned |
| UX-01 | Phase 5 | Planned |
| UX-02 | Phase 5 | Planned |
| ALERT-01 | Phase 7 | Complete |
| ALERT-02 | Phase 7 | Complete |
| ALERT-03 | Phase 7 | Planned |
| ALERT-04 | Phase 7 | Planned |
| ALERT-05 | Phase 7 | Planned |
| ALERT-06 | Phase 7 | Planned |
| ALERT-07 | Phase 7 | Planned |

| REACT-01 | Phase 9 | Complete |
| REACT-02 | Phase 9 | Complete |
| REACT-03 | Phase 9 | Complete |
| REACT-04 | Phase 9 | Complete |
| REACT-05 | Phase 9 | Complete |
| REACT-06 | Phase 9 | Planned |
| REACT-07 | Phase 9 | Planned |
| REACT-08 | Phase 9 | Planned |
| REACT-09 | Phase 9 | Planned |
| REACT-10 | Phase 9 | Complete |
| REACT-11 | Phase 9 | Planned |
| REACT-12 | Phase 9 | Complete |

**Coverage:**
- v1 requirements: 36 total
- Mapped to phases: 36
- Unmapped: 0

---
*Requirements defined: 2026-02-28*
*Last updated: 2026-03-06 after Phase 7 planning*
