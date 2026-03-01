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
- [ ] **Phase 4: Web Dashboard** - Browser-based auto-refreshing price dashboard started with `crypto web`

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
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Project Setup | 1/1 | Complete   | 2026-03-01 |
| 2. API Integration | 1/1 | Complete   | 2026-03-01 |
| 3. CLI and Display | 2/2 | Complete   | 2026-03-01 |
| 4. Web Dashboard | 0/2 | Planned | — |
| 5. Web UX | 0/1 | Planned | — |

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
- [ ] 04-01-PLAN.md — Add FastAPI web server with JSON API endpoints and `crypto web` CLI subcommand
- [ ] 04-02-PLAN.md — Build HTML/CSS/JS frontend with auto-refreshing price table and coin detail modal

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
