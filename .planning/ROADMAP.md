# Roadmap: Crypto Price Tracker

## Overview

Three phases deliver the complete v1.0 Core CLI: first the project skeleton and installable entry point, then the Bitvavo API integration that fetches and sorts live EUR market data, and finally the three CLI subcommands with formatted table output and color-coded price changes.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Project Setup** - uv-managed Python project with installable `crypto` entry point
- [ ] **Phase 2: API Integration** - Fetch, sort, and normalize live EUR crypto data from Bitvavo
- [ ] **Phase 3: CLI and Display** - Three subcommands with formatted tables and color-coded output

## Phase Details

### Phase 1: Project Setup
**Goal**: A working Python project that can be installed locally and invoked as `crypto` from the terminal
**Depends on**: Nothing (first phase)
**Requirements**: SETUP-01, SETUP-02
**Success Criteria** (what must be TRUE):
  1. Running `uv sync` in the repo installs all dependencies without errors
  2. Running `crypto --help` after install prints usage information without errors
  3. The project has no setup.py or requirements.txt — only pyproject.toml
**Plans**: TBD

### Phase 2: API Integration
**Goal**: The tool can fetch live EUR cryptocurrency data from the Bitvavo public API and return structured results sorted by market cap
**Depends on**: Phase 1
**Requirements**: API-01, API-02, API-03
**Success Criteria** (what must be TRUE):
  1. Calling the data layer returns prices denominated in EUR for each coin
  2. The returned coin list is sorted by market cap descending
  3. Fetching top 20 coins requires no API key or authentication
  4. The number of coins fetched can be configured (default 20)
**Plans**: TBD

### Phase 3: CLI and Display
**Goal**: Users can view live crypto prices in the terminal via three subcommands with color-coded formatted output
**Depends on**: Phase 2
**Requirements**: CLI-01, CLI-02, CLI-03, DISP-01, DISP-02, DISP-03
**Success Criteria** (what must be TRUE):
  1. `crypto prices` prints a formatted table of top 20 coins (price, 24h change %, market cap, volume) and exits
  2. `crypto watch` refreshes the price table every 30 seconds by default; `--interval N` changes the refresh rate
  3. `crypto info BTC` prints an expanded detail view for a single coin and exits
  4. Coins with positive 24h change display in green; coins with negative change display in red
  5. All prices in the table and detail view are shown in EUR
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Project Setup | 0/? | Not started | - |
| 2. API Integration | 0/? | Not started | - |
| 3. CLI and Display | 0/? | Not started | - |
