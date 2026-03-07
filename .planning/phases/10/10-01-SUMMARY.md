---
phase: 10-multi-exchange
plan: 01
subsystem: exchange
tags: [exchange, binance, bitvavo, abstraction, fallback, cli]
dependency_graph:
  requires: []
  provides: [exchange-abstraction, binance-client, auto-fallback, exchange-cli-flag]
  affects: [api, cli, display, web]
tech_stack:
  added: []
  patterns: [protocol-class, factory-function, auto-fallback, fx-caching]
key_files:
  created:
    - src/crypto_price_tracker/exchange.py
    - tests/test_exchange.py
  modified:
    - src/crypto_price_tracker/api.py
    - src/crypto_price_tracker/cli.py
    - src/crypto_price_tracker/display.py
    - tests/test_cli.py
decisions:
  - "ExchangeClient protocol defines name property, get_top_coins, and context manager methods"
  - "BinanceClient fetches USDT pairs and converts to EUR via Binance EURUSDT inverse rate"
  - "FX rate cached using time.monotonic with 5-minute TTL"
  - "Stablecoins (USDC, BUSD, DAI, TUSD, FDUSD, USDD, USDP) filtered from Binance results"
  - "get_top_coins_with_fallback returns (coins, source_name) tuple for source labeling"
  - "CLI uses get_top_coins_with_fallback replacing all get_top_coins calls"
  - "render_price_table shows 'via {source}' as table caption with dim style"
metrics:
  duration: "7 min"
  completed: "2026-03-07"
  tasks_completed: 4
  tasks_total: 4
  tests_before: 152
  tests_after: 168
---

# Phase 10 Plan 01: Exchange Abstraction Layer Summary

Exchange abstraction with ExchangeClient protocol, BinanceClient USDT-to-EUR conversion with 5-min FX caching, auto-fallback between exchanges, and --exchange CLI flag on all price subcommands.

## What Was Built

### Task 1: Exchange Abstraction Module
Created `src/crypto_price_tracker/exchange.py` with:
- `ExchangeClient` protocol defining the interface for exchange clients
- `BinanceClient` implementing the protocol with USDT pair fetching, EUR conversion via Binance's EURUSDT rate, and 5-minute FX caching using `time.monotonic`
- Stablecoin filtering (USDC, BUSD, DAI, TUSD, FDUSD, USDD, USDP)
- `get_exchange_client()` factory function returning the correct client
- `get_top_coins_with_fallback()` trying primary exchange then falling back to other on HTTP errors
- Commit: `4a8f121`

### Task 2: API Module Updates
Updated `src/crypto_price_tracker/api.py`:
- Added `name` property to `BitvavoClient` returning "Bitvavo" (protocol conformance)
- Extended `get_top_coins()` to accept `exchange` parameter (backward compatible, defaults to "bitvavo")
- `get_candles()` unchanged (always Bitvavo per CONTEXT.md decision)
- Commit: `e3412d4`

### Task 3: CLI --exchange Flag and Display Source
Updated `src/crypto_price_tracker/cli.py` and `src/crypto_price_tracker/display.py`:
- Added `--exchange bitvavo|binance` argument to prices, watch, info, web, chart subcommands
- All `get_top_coins()` calls replaced with `get_top_coins_with_fallback()` returning `(coins, source)` tuples
- `cmd_web()` stores `default_exchange` on `app.state` for web module access
- `render_price_table()` shows "via {source}" as Rich table caption when source is provided
- `cmd_info()` prints source label before coin detail
- Commit: `ea59bc5`

### Task 4: Unit Tests and Mock Updates
Created `tests/test_exchange.py` with 15 tests and updated `tests/test_cli.py`:
- BinanceClient tests: FX conversion, USDT-only filtering, stablecoin exclusion, zero-open skip, volume sorting, top_n limiting, 24h change calculation, FX caching, cache expiry, name property
- Factory tests: correct client type for bitvavo/binance
- Fallback tests: primary success, fallback on primary failure, both-fail exception propagation
- Updated all CLI test mocks from `get_top_coins` to `get_top_coins_with_fallback` with tuple returns
- Added `test_prices_command_with_exchange_flag` for --exchange binance
- All 168 tests passing (152 original + 16 new)
- Commit: `1f36d33`

## Deviations from Plan

None - plan executed exactly as written.

## Decisions Made

1. **FX rate URL matching in tests**: Used full URL with query params (`?symbol=EURUSDT`) for pytest-httpx strict matching (v0.36.0 requires exact URL match including params)
2. **Stablecoin set as frozenset**: Used `frozenset` class attribute for immutable, hashable stablecoin filter set
3. **getattr for chart exchange**: Used `getattr(args, "exchange", "bitvavo")` in cmd_chart for safe attribute access

## Verification Results

1. Full test suite: 168 passed (0 failed)
2. Import check: `from crypto_price_tracker.exchange import BinanceClient, get_top_coins_with_fallback` -- OK
3. CLI help: `crypto prices --help` shows `--exchange {bitvavo,binance}` -- OK
4. Backward compat: `get_top_coins()` with no exchange param defaults to bitvavo -- OK
