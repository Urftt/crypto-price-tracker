# Requirements: Crypto Price Tracker

**Defined:** 2026-02-28
**Core Value:** Instant, glanceable crypto prices in the terminal — one command, no browser needed.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### API (Data Fetching)

- [ ] **API-01**: User can fetch current crypto prices from the public Bitvavo REST API
- [ ] **API-02**: All prices are displayed in EUR via Bitvavo EUR trading pairs
- [ ] **API-03**: Top N coins are fetched dynamically and sorted by market cap (default 20)

### Display (Terminal Output)

- [ ] **DISP-01**: Prices are shown in a formatted terminal table with price, 24h change %, market cap, and volume
- [ ] **DISP-02**: 24h change is color-coded green (positive) or red (negative)
- [ ] **DISP-03**: Single-coin detail view shows expanded information for one cryptocurrency

### CLI (Commands & Interface)

- [ ] **CLI-01**: `crypto prices` displays the price table once and exits
- [ ] **CLI-02**: `crypto watch` auto-refreshes the price table (default 30s, configurable via `--interval`)
- [ ] **CLI-03**: `crypto info <SYMBOL>` shows detailed info for a single coin

### Setup (Project Infrastructure)

- [x] **SETUP-01**: Project uses uv with pyproject.toml (no setup.py or requirements.txt)
- [x] **SETUP-02**: CLI is installable with a `crypto` entry point command

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
| Mobile or web interface | CLI only |
| WebSocket streaming | REST API is sufficient for v1 refresh intervals |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| SETUP-01 | Phase 1 | Complete |
| SETUP-02 | Phase 1 | Complete |
| API-01 | Phase 2 | Pending |
| API-02 | Phase 2 | Pending |
| API-03 | Phase 2 | Pending |
| DISP-01 | Phase 3 | Pending |
| DISP-02 | Phase 3 | Pending |
| DISP-03 | Phase 3 | Pending |
| CLI-01 | Phase 3 | Pending |
| CLI-02 | Phase 3 | Pending |
| CLI-03 | Phase 3 | Pending |

**Coverage:**
- v1 requirements: 11 total
- Mapped to phases: 11
- Unmapped: 0

---
*Requirements defined: 2026-02-28*
*Last updated: 2026-02-28 after roadmap creation*
