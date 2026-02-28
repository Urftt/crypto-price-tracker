# Roadmap: Crypto Price Tracker

## Overview

Three phases to deliver a working CLI tool: scaffold the project so the `crypto` command exists, wire up the Bitvavo API so live EUR price data flows in, then build the three subcommands with formatted color-coded output. Each phase completes a coherent capability and unblocks the next.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Project Setup** - uv project scaffold with installable `crypto` entry point
- [ ] **Phase 2: API Integration** - Live EUR crypto prices fetched from the public Bitvavo REST API
- [ ] **Phase 3: CLI and Display** - All three subcommands working with formatted, color-coded terminal output

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
- [ ] 01-01-PLAN.md — Scaffold uv project with pyproject.toml, entry point, and minimal CLI skeleton

### Phase 2: API Integration
**Goal**: Live EUR cryptocurrency price data flows from the public Bitvavo REST API into the application
**Depends on**: Phase 1
**Requirements**: API-01, API-02, API-03
**Success Criteria** (what must be TRUE):
  1. Calling the Bitvavo API client returns current prices denominated in EUR
  2. The top N coins (default 20) are fetched and sorted by market cap
  3. API calls require no authentication or API key
  4. Price, 24h change %, market cap, and volume are all retrievable for each coin
**Plans**: TBD

Plans:
- [ ] 02-01: Implement Bitvavo API client — fetch ticker, 24h stats, and market cap data

### Phase 3: CLI and Display
**Goal**: Users can run all three subcommands and see formatted, color-coded crypto prices in the terminal
**Depends on**: Phase 2
**Requirements**: CLI-01, CLI-02, CLI-03, DISP-01, DISP-02, DISP-03
**Success Criteria** (what must be TRUE):
  1. `crypto prices` prints a formatted table of the top 20 coins with price, 24h change %, market cap, and volume, then exits
  2. `crypto watch` refreshes the price table every 30 seconds by default; `--interval N` overrides the refresh period
  3. `crypto info BTC` shows a detailed single-coin view with expanded information
  4. Positive 24h change is displayed in green and negative in red in the terminal
**Plans**: TBD

Plans:
- [ ] 03-01: Build terminal table renderer with color-coded 24h change
- [ ] 03-02: Implement `prices`, `watch`, and `info` subcommands wired to the API client

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Project Setup | 0/1 | Not started | - |
| 2. API Integration | 0/1 | Not started | - |
| 3. CLI and Display | 0/2 | Not started | - |
