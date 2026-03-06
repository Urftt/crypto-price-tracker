---
phase: "06"
plan: "02"
subsystem: portfolio-integration
tags: [cli, web-api, dashboard, portfolio, rich, fastapi]
dependency_graph:
  requires: [06-01]
  provides: [portfolio-cli, portfolio-api, portfolio-ui]
  affects: [cli, display, web, index.html]
tech_stack:
  added: [pydantic-models]
  patterns: [subcommand-group, crud-endpoints, tab-navigation, form-submission]
key_files:
  modified:
    - src/crypto_price_tracker/cli.py
    - src/crypto_price_tracker/display.py
    - src/crypto_price_tracker/web.py
    - src/crypto_price_tracker/static/index.html
    - tests/test_cli.py
    - tests/test_web.py
decisions:
  - Pydantic BaseModel for request validation (HoldingCreate, HoldingUpdate)
  - Portfolio routes defined before index catch-all in FastAPI app
  - Tab navigation with inline JS switchTab() keeps single-file dashboard pattern
  - Lots toggle expands/collapses inline below portfolio row
metrics:
  duration: "4 min"
  completed: "2026-03-06"
  tasks: 5
  tests_added: 15
  tests_total: 76
---

# Phase 6 Plan 2: Portfolio CLI + Web Integration Summary

Portfolio CLI subcommands with Rich tables, FastAPI CRUD endpoints with Pydantic validation, and Portfolio tab in HTML dashboard with add-holding form and lots toggle.

## Tasks Completed

| Task | Description | Commit |
|------|-------------|--------|
| 1 | Portfolio subcommand group in cli.py (add/remove/edit/list/lots/export) | d6b2c54 |
| 2 | render_portfolio_table and render_portfolio_lots in display.py | d6b2c54 |
| 3 | Portfolio API endpoints in web.py (GET/POST/PUT/DELETE with Pydantic) | d6b2c54 |
| 4 | Portfolio tab in index.html (form, table, lots toggle, summary footer) | d6b2c54 |
| 5 | 6 CLI tests + 9 web API tests for portfolio functionality | d6b2c54 |

## Decisions Made

1. **Pydantic BaseModel for request validation** -- HoldingCreate and HoldingUpdate models provide automatic validation (amount > 0, buy_price > 0) with 422 responses for invalid input.

2. **Portfolio routes before index catch-all** -- FastAPI route ordering matters; portfolio endpoints defined before the "/" route and static mount to prevent routing conflicts.

3. **Tab navigation with inline JS** -- Continues the single self-contained HTML file pattern from 04-02. switchTab() hides/shows tab-content divs and loads portfolio data on demand.

4. **Lots toggle inline expansion** -- Clicking "lots" on a portfolio row fetches and inserts individual lot rows directly below, with per-lot delete buttons.

5. **Best-effort pricing in both CLI and web** -- Portfolio aggregation uses try/except for price fetching; unpriced coins display as N/A in UI and use cost basis in totals.

## Deviations from Plan

None -- plan executed exactly as written.

## Test Results

76 tests passing (61 existing + 15 new):
- 6 new CLI portfolio tests (add, remove, list, lots, export, no-subcommand)
- 9 new web portfolio tests (empty GET, add, add-then-get, delete, delete-not-found, update, lots, validation, portfolio-tab-in-html)

## Files Modified

- **src/crypto_price_tracker/cli.py** -- Added 6 cmd_portfolio_* functions, portfolio argparse subparser group, dispatch logic
- **src/crypto_price_tracker/display.py** -- Added render_portfolio_table() and render_portfolio_lots() with Rich formatting
- **src/crypto_price_tracker/web.py** -- Added HoldingCreate/HoldingUpdate Pydantic models, 5 portfolio CRUD endpoints
- **src/crypto_price_tracker/static/index.html** -- Added tabs CSS, portfolio tab with form/table/summary, JS functions (switchTab, loadPortfolio, toggleLots, deleteLot, addHolding)
- **tests/test_cli.py** -- Added 6 portfolio CLI tests
- **tests/test_web.py** -- Added portfolio_db fixture and 9 portfolio API tests
