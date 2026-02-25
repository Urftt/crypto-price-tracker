# Requirements — Crypto Price Tracker

## v1 Requirements

### Display
- [ ] **DISP-01**: User can view top 20 crypto prices in a formatted terminal table
- [ ] **DISP-02**: User can see price, 24h change %, market cap, and volume per coin
- [ ] **DISP-03**: User can see green/red coloring for positive/negative 24h change

### CLI
- [ ] **CLI-01**: User can run `crypto prices` for a one-shot price table
- [ ] **CLI-02**: User can run `crypto watch` with auto-refresh (default 30s, configurable via `--interval`)
- [ ] **CLI-03**: User can run `crypto info <SYMBOL>` for single-coin detail view

### Data
- [ ] **DATA-01**: Prices fetched from public Bitvavo REST API (no auth)
- [ ] **DATA-02**: All prices displayed in EUR
- [ ] **DATA-03**: Top N coins fetched dynamically and sorted by market cap

### Project
- [ ] **PROJ-01**: uv-managed project with pyproject.toml

## Out of Scope
- Authentication / private Bitvavo endpoints — public data only
- Extended stats (ATH, supply, 24h high/low) — keep info view simple
- Custom coin lists / watchlists — dynamic ranking is sufficient
- Portfolio tracking / balance management — viewer only
- USD or multi-currency support — EUR only
- Mobile or web interface — CLI only

## Traceability

| REQ | Phase |
|-----|-------|
| (To be filled by roadmapper) | |
