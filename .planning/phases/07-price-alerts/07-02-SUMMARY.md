---
phase: "07"
plan: "02"
subsystem: alerts-integration
tags: [alerts, cli, web-api, html, toast, rich-display, integration-tests]
dependency_graph:
  requires: [PriceAlert, alerts_db, alerts, display.py, cli.py, web.py, index.html]
  provides: [alert CLI subcommands, alert web endpoints, alerts tab, toast system, set-alert modal button]
  affects: [tests/test_cli.py, tests/test_display.py, tests/test_web.py]
tech_stack:
  added: []
  patterns: [passive alert checking on price fetch, flash-once in watch mode, breaking API response format change, route ordering for path params, Pydantic validation for API input]
key_files:
  created: []
  modified:
    - src/crypto_price_tracker/display.py
    - src/crypto_price_tracker/cli.py
    - src/crypto_price_tracker/web.py
    - src/crypto_price_tracker/static/index.html
    - tests/test_cli.py
    - tests/test_display.py
    - tests/test_web.py
decisions:
  - "/api/prices response changed from bare array to {coins: [...], triggered_alerts: [...]}"
  - "Passive alert checking runs on every price fetch (cmd_prices, cmd_watch, /api/prices)"
  - "Flash-once in watch mode via mark_triggered() -- get_active_alerts() skips already-triggered"
  - "Route ordering: /api/alerts/triggered defined BEFORE /api/alerts/{alert_id} to avoid path param collision"
  - "AlertCreate Pydantic model validates direction with regex pattern and target_price > 0"
  - "Toast auto-dismiss at 10 seconds with CSS slide-in/fade-out transition"
  - "Coin dropdown populated from /api/prices data on every refresh, not a separate API call"
metrics:
  duration: "~3 min"
  completed: "2026-03-06"
  tasks_completed: 4
  tasks_total: 4
  tests_added: 30
  tests_total: 161
---

# Phase 7 Plan 2: Integration -- CLI Alert Subcommands, Display Functions, Web API Endpoints, HTML Alerts Tab, and Integration Tests Summary

Full alert integration across CLI and web surfaces: Rich banner + inline markers on price table, 4 alert subcommands (add/list/remove/check), FastAPI CRUD endpoints with alert-aware /api/prices, HTML Alerts tab with toast notifications and Set Alert modal button, plus 30 new integration tests covering all surfaces.

## What Was Built

### Display Functions (display.py)

**Modified `render_price_table`** -- Added optional `triggered_symbols: set[str]` parameter. When a coin's symbol is in the set, the symbol cell renders as `[bold yellow]<warning> SYMBOL[/bold yellow]` with a warning marker. Backward-compatible: defaults to empty set.

**Added `render_alert_banner`** -- Renders a Rich Panel with yellow border titled "ALERTS TRIGGERED". Each triggered alert gets a line showing the warning symbol, coin symbol, target price formatted with thousands separators, and direction.

**Added `render_alert_list`** -- Renders a Rich Table titled "Price Alerts" with columns: ID, Symbol, Target (EUR), Direction, Status, Created, Triggered. Active alerts show green status, triggered alerts show yellow status with a section separator. Empty list prints "No alerts set."

### CLI Commands (cli.py)

**4 new `cmd_alert_*` functions:**
- `cmd_alert_add` -- Calls `add_alert()`, prints confirmation with alert ID. Handles ValueError and IntegrityError.
- `cmd_alert_list` -- Calls `get_all_alerts()` and `render_alert_list()`.
- `cmd_alert_remove` -- Calls `remove_alert_db()`, prints confirmation or exits 1 if not found.
- `cmd_alert_check` -- Fetches top 100 coins, checks active alerts, marks triggered, renders banner if any triggered, exits 1 on triggers, 0 on none. Scriptable exit codes.

**Passive alert checking in `cmd_prices` and `cmd_watch`:**
After fetching prices, both commands now call `get_active_alerts()` + `check_alerts()` + `mark_triggered()`. Triggered symbols are passed to `render_price_table()` for inline markers. Banner renders if any triggered.

**Argparse setup:**
- `alert` subparser with `add`, `list`, `remove`, `check` sub-subcommands
- `--above`/`--below` mutually exclusive group on `add` with `--above` as default
- Dispatch chain in `main()` with help fallback when no subcommand given

### Web API Endpoints (web.py)

**Modified `/api/prices`** -- Breaking change: response changed from bare JSON array `[...]` to `{"coins": [...], "triggered_alerts": [...]}`. Passive alert checking runs on every price fetch: gets active alerts, checks against fetched coins, marks triggered.

**4 new alert endpoints:**
- `GET /api/alerts` -- Returns all alerts as JSON array
- `POST /api/alerts` (201) -- Creates alert with `AlertCreate` Pydantic validation (symbol, target_price > 0, direction matching `^(above|below)$`)
- `DELETE /api/alerts/triggered` -- Clears all triggered alerts, returns count (defined BEFORE parameterized route)
- `DELETE /api/alerts/{alert_id}` -- Removes single alert by ID, 404 if not found

### HTML Dashboard (index.html)

**Alerts tab** -- Third tab alongside Prices and Portfolio. Contains:
- Add alert form with coin dropdown (populated from /api/prices data), target price input, above/below direction select
- Active alerts table with remove buttons
- Triggered alerts table with remove buttons and "Clear All Triggered" bulk button (hidden when empty)

**Toast notification system** -- Fixed-position container at top-right. Each triggered alert shows a toast with orange border, slide-in animation, auto-dismiss at 10 seconds with fade-out transition.

**Modified `load()` function** -- Reads `raw.coins` instead of `raw` directly to handle the new /api/prices dict format. Calls `populateAlertDropdown(data)` on every refresh. Shows toast for each triggered alert.

**"Set Alert" button in coin detail modal** -- Closes modal, switches to Alerts tab, pre-selects the coin in the dropdown, focuses the price input.

**JavaScript functions added:** `showToast()`, `populateAlertDropdown()`, `loadAlerts()`, `addAlert()`, `removeAlert()`, `clearTriggered()`, `setAlertFromModal()`.

### Test Updates

**Fixed 5 existing broken tests:**
- `test_prices_command_calls_api_and_renders` -- Added `get_active_alerts`/`check_alerts` patches + `triggered_symbols=set()` assertion
- `test_prices_command_respects_top_n_flag` -- Added alert patches
- `test_watch_command_parses_interval` -- Added alert patches
- `test_api_prices_returns_json_list` -- Changed from list to dict assertion, added `portfolio_db` fixture
- `test_api_prices_respects_top_param` -- Added `portfolio_db` fixture

**Added 30 new integration tests:**
- CLI (8 new): alert add/add-below/remove/list/check-no-triggers/check-with-triggers/no-subcommand/prices-with-alert-checking
- Display (5 new): price table with/without triggered symbols, alert banner, alert list active+triggered, alert list empty
- Web (11 new): prices new format, prices triggers alerts, alerts get/add/add-then-get/delete/delete-not-found/clear-triggered/validation, index has alerts tab, index has set alert modal button
- Additional web test for prices format: `test_api_prices_returns_new_format`

## Deviations from Plan

None -- plan executed exactly as written. All 4 tasks completed with all specified functionality.

## Decisions Made

1. **/api/prices breaking change** -- Response format changed from `[...]` to `{"coins": [...], "triggered_alerts": [...]}` to enable passive alert notification through the existing price polling mechanism
2. **Passive checking on every fetch** -- Alerts checked in `cmd_prices`, `cmd_watch`, and `/api/prices` so users get notified without explicit `alert check`
3. **Flash-once behavior** -- `mark_triggered()` changes status immediately, so subsequent `get_active_alerts()` calls skip the alert
4. **Route ordering** -- `/api/alerts/triggered` must precede `/api/alerts/{alert_id}` because FastAPI matches top-down and would interpret "triggered" as an integer path parameter
5. **Pydantic validation** -- `AlertCreate` model validates direction with regex `^(above|below)$` and target_price with `gt=0`, returning 422 on bad input
6. **Toast timing** -- 10-second auto-dismiss with CSS transition for smooth UX, matching the locked decision from CONTEXT.md

## Test Results

```
161 passed in 13.58s
- 26 CLI tests (8 new alert integration tests)
- 24 display tests (5 new alert display tests)
- 43 web tests (12 new alert web tests)
- 68 other tests (API, portfolio DB, portfolio, alerts DB, alerts checking, charts)
```

## Self-Check: PASSED

All 7 modified files verified on disk. Commit d3c969b confirmed in git log.
