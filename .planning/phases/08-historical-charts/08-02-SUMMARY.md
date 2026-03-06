---
phase: 8
plan: 2
subsystem: web
tags: [plotly, charts, candles, web-dashboard, fastapi]
dependency_graph:
  requires: [08-01]
  provides: [candle-endpoint, plotly-charts, chart-modal]
  affects: [web.py, index.html, test_web.py]
tech_stack:
  added: [plotly-3.4.0-cdn]
  patterns: [candle-endpoint, chart-toggle, plotly-cleanup]
key_files:
  created: []
  modified:
    - src/crypto_price_tracker/web.py
    - src/crypto_price_tracker/static/index.html
    - tests/test_web.py
decisions:
  - Plotly CDN v3.4.0 pinned (not plotly-latest which is frozen at v1.58.5)
  - Chart placed inside existing coin detail modal, not a new tab
  - Line chart only (closing prices), matching dark theme colors
  - Modal widened from 400px to 600px for chart space
  - Plotly.purge() called on modal close to free memory
metrics:
  duration: 2m 31s
  completed: 2026-03-06
  tasks: 3
  tests_added: 10
  tests_total: 161
---

# Phase 8 Plan 2: Web Dashboard -- Candle API Endpoint, Plotly Charts in Coin Detail Modal Summary

Wired Bitvavo candle data into the web dashboard via a new `/api/candles/{symbol}` FastAPI endpoint, with Plotly.js (v3.4.0 CDN) rendering interactive dark-themed line charts inside the existing coin detail modal, 7D/30D toggle buttons, and 10 new web tests.

## What Was Done

### Task 1: Add /api/candles/{symbol} endpoint to web.py
- Added `get_candles` import from `api` module and `Candle` import from `models`
- Created `/api/candles/{symbol}` endpoint with `interval` (regex-validated against all Bitvavo intervals) and `limit` (1-1440) query parameters
- Translates Bitvavo HTTP 400 (invalid market) to HTTP 404 with descriptive message
- Returns chronological list of candle dicts via `dataclasses.asdict()`
- Commit: 80b4e7a

### Task 2: Add Plotly CDN, chart section, toggle buttons, JS, and CSS to index.html
- Added pinned Plotly CDN `plotly-3.4.0.min.js` script tag in `<head>`
- Added `.chart-period-btn` CSS with hover/active states matching dark theme
- Widened `#modal-card` max-width from 400px to 600px
- Added `#chart-section` with `#chart-container` div and 7D/30D toggle buttons inside modal
- Added `loadChart()` function: fetches candle data, renders Plotly line chart with dark theme colors (#161b22 bg, #58a6ff line, #c9d1d9 text)
- Added `switchPeriod()` function: toggles between 7D (4h interval, 42 candles) and 30D (1d interval, 30 candles)
- Modified `showDetail()` to reset chart section and load 7D chart after coin data loads
- Modified `closeModal()` to call `Plotly.purge()` for memory cleanup
- Commit: 80b4e7a

### Task 3: Add 10 web tests for candle endpoint and HTML content
- Added `make_test_candles()` helper returning 3 sample Candle objects
- `test_api_candles_returns_json_list` -- verifies 200, list structure, field names, values
- `test_api_candles_case_insensitive` -- verifies lowercase `btc` uppercased to `BTC-EUR`
- `test_api_candles_with_interval_param` -- verifies interval/limit params passed through
- `test_api_candles_invalid_market` -- verifies Bitvavo 400 translated to 404
- `test_api_candles_invalid_interval` -- verifies regex pattern rejects invalid intervals (422)
- `test_api_candles_empty_response` -- verifies empty candle list returns 200 with `[]`
- `test_index_has_plotly_script` -- verifies Plotly CDN script tag present
- `test_index_has_chart_elements` -- verifies chart-section, chart-container, chart-period-btn, loadChart, switchPeriod, /api/candles/ present
- `test_index_has_chart_period_buttons` -- verifies 7D and 30D button text
- `test_index_modal_width_increased` -- verifies modal max-width is 600px
- Commit: 80b4e7a

## Deviations from Plan

None -- plan executed exactly as written.

## Verification Results

- `uv run pytest tests/ -x -q` -- 161 passed (all existing + 10 new)
- `uv run pytest tests/test_web.py -x -q` -- 43 passed (33 existing + 10 new candle/chart tests)
- No regressions in test_api.py, test_display.py, test_cli.py, or other test modules

## Self-Check: PASSED

- All modified files exist on disk
- Commit 80b4e7a verified in git log
- 161 tests passing
