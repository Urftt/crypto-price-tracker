---
phase: "08"
plan: "01"
subsystem: "historical-charts"
tags: [candle-api, sparkline, cli-chart, display]
dependency_graph:
  requires: []
  provides: [Candle model, get_candles API, sparkline rendering, chart CLI subcommand]
  affects: [models.py, api.py, display.py, cli.py]
tech_stack:
  added: []
  patterns: [OHLCV candle dataclass, Unicode sparkline rendering, sequential candle fetching with Rich status]
key_files:
  created: []
  modified:
    - src/crypto_price_tracker/models.py
    - src/crypto_price_tracker/api.py
    - src/crypto_price_tracker/display.py
    - src/crypto_price_tracker/cli.py
    - tests/test_api.py
    - tests/test_display.py
    - tests/test_cli.py
decisions:
  - "URL matching in pytest-httpx requires full URL with query params (strict matching in v0.36.0)"
  - "Rich bold markup splits numeric-prefixed labels with ANSI codes; test assertions check parts separately"
metrics:
  duration: "5 min"
  completed: "2026-03-06"
  tasks_completed: 4
  tasks_total: 4
  tests_added: 20
  tests_total: 151
---

# Phase 8 Plan 1: Backend + CLI -- Candle Model, API Fetching, Sparkline Rendering, Chart Subcommand Summary

Candle OHLCV dataclass, Bitvavo candle API integration with chronological reversal, Unicode sparkline rendering (8-block linear mapping), and `crypto chart` CLI with overview table and single-coin detail modes.

## What Was Built

### Task 1: Candle model + API

- Added `Candle` dataclass to `models.py` with `timestamp`, `open`, `high`, `low`, `close`, `volume` fields (slots=True)
- Added `get_candles()` method to `BitvavoClient` that fetches from `/{market}/candles`, converts string values to float, reverses newest-first response to chronological order
- Added module-level `get_candles()` convenience function matching existing `get_top_coins()` pattern

### Task 2: Sparkline rendering + chart display

- Added `SPARK_CHARS` constant (U+2581..U+2588) and `sparkline()` function with linear mapping, empty/constant value handling
- Added `render_chart_table()` for compact multi-coin sparkline overview (rank, symbol, 7d, 30d columns)
- Added `render_chart_detail()` for single-coin view with sparklines, open/close/high/low stats, and color-coded change %

### Task 3: Chart CLI subcommand

- Added `cmd_chart()` with two modes: overview (all top coins with Rich status spinner) and single-coin detail
- Added `chart` subparser with optional `symbol` positional arg and `-n/--top` flag
- Error handling: coin-not-found exits with code 1, HTTP errors caught gracefully with empty candle fallback

### Task 4: Comprehensive tests

- 4 API tests: chronological order, string-to-float conversion, empty response, invalid market 400 error
- 11 display tests: 6 sparkline tests (basic, empty, single, constant, ascending, two-value), 2 chart table tests, 3 chart detail tests
- 5 CLI tests: all-coins, single-coin, case-insensitive, not-found, top-n flag

## Test Results

- 151 total tests passing (131 existing + 20 new)
- test_api.py: 9 tests (5 existing + 4 new)
- test_display.py: 24 tests (13 existing + 11 new)
- test_cli.py: 26 tests (21 existing + 5 new)

## Commits

| Hash | Message |
|------|---------|
| 30863c9 | feat(08-01): add Candle model, candle API, sparkline rendering, and chart CLI subcommand |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] pytest-httpx strict URL matching with query params**
- **Found during:** Task 4 (test writing)
- **Issue:** pytest-httpx v0.36.0 does strict URL matching; mock URL `https://api.bitvavo.com/v2/BTC-EUR/candles` does not match request URL with query params `?interval=4h&limit=3`
- **Fix:** Updated all candle test mock URLs to include the full query string (e.g. `?interval=4h&limit=42`)
- **Files modified:** tests/test_api.py

**2. [Rule 1 - Bug] Rich ANSI codes splitting "7-Day" in bold markup**
- **Found during:** Task 4 (test assertions)
- **Issue:** Rich's `[bold]7-Day[/bold]` renders with ANSI codes that split "7" from "-Day" (`\x1b[1;36m7\x1b[0m\x1b[1m-Day\x1b[0m`), so `assert "7-Day" in output` fails
- **Fix:** Changed assertions to check for component parts ("7" and "Day") separately instead of the full "7-Day" string
- **Files modified:** tests/test_display.py

## Self-Check: PASSED

All 7 modified files verified present on disk. Commit 30863c9 verified in git log. 151/151 tests passing.
