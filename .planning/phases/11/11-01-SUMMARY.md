---
phase: 11-watchlist-tags
plan: 01
subsystem: watchlist
tags: [watchlist, tags, sqlite, cli, display]
dependency_graph:
  requires: [portfolio_db, alerts_db, models, display, cli]
  provides: [watchlist_db, WatchlistEntry, render_watchlist_table, watchlist-cli-subcommands]
  affects: [models.py, display.py, cli.py]
tech_stack:
  added: []
  patterns: [connection-per-call, row-factory, tag-normalization, VALID_TAGS-frozenset]
key_files:
  created:
    - src/crypto_price_tracker/watchlist_db.py
    - tests/test_watchlist_db.py
  modified:
    - src/crypto_price_tracker/models.py
    - src/crypto_price_tracker/display.py
    - src/crypto_price_tracker/cli.py
    - tests/test_cli.py
decisions:
  - "watchlist_db mirrors alerts_db pattern: connection-per-call with try/finally close"
  - "Tags validated against VALID_TAGS frozenset, case-insensitive input, canonical casing stored"
  - "Symbol UNIQUE constraint in SQLite, stored uppercase, IntegrityError on duplicate"
  - "render_watchlist_table shows N/A for coins without live price data"
  - "cmd_watchlist_add converts None tags to empty list via `args.tag or []`"
metrics:
  duration: 4 min
  completed: "2026-03-07T15:11:29Z"
  tasks: 2
  tests_added: 37
  tests_total: 208
  files_created: 2
  files_modified: 4
---

# Phase 11 Plan 01: Watchlist & Tags -- Backend + CLI Summary

Persistent watchlist with tag-based filtering, SQLite CRUD, Rich table renderer, and full CLI subcommand group.

## One-liner

SQLite-backed watchlist with 6 category tags, CRUD layer, Rich table renderer, and CLI subcommands (add/list/remove/tag) plus --watchlist flag on prices/watch.

## What Was Built

### Task 1: WatchlistEntry model, watchlist_db.py CRUD, and unit tests

- Added `WatchlistEntry` dataclass to `models.py` with `id`, `symbol`, `tags`, `added_at` fields
- Created `watchlist_db.py` with 6 exported functions:
  - `get_watchlist_connection` -- opens DB with WAL mode, schema check
  - `add_watchlist_entry` -- insert with UNIQUE symbol, tag validation
  - `remove_watchlist_entry` -- delete by symbol (case-insensitive)
  - `get_all_watchlist_entries` -- list all, with optional tag filter using SQL LIKE
  - `update_watchlist_tags` -- replace tags on existing entry
  - `get_watchlist_symbols` -- return set of all watched symbols
- Tag validation against `VALID_TAGS` frozenset: Layer1, Layer2, DeFi, Meme, Exchange, Privacy
- Tags are case-insensitive on input, stored with canonical casing, sorted alphabetically
- Duplicate tags in input are deduplicated
- 26 unit tests covering all CRUD operations, edge cases, tag validation, coexistence with holdings/alerts tables

**Commit:** `9b030a2`

### Task 2: Watchlist display renderer, CLI subcommands, --watchlist flag, and CLI tests

- Added `render_watchlist_table` to `display.py` -- Rich table with Symbol, Tags, Price (EUR), 24h%, Volume (EUR), Added columns
- Added 4 watchlist command functions to `cli.py`:
  - `cmd_watchlist_add` -- add with optional tags, ValueError/IntegrityError handling
  - `cmd_watchlist_list` -- list with optional `--tag` filter, best-effort live prices
  - `cmd_watchlist_remove` -- remove by symbol with not-found error
  - `cmd_watchlist_tag` -- update tags on existing entry
- Added watchlist subparser group with add/list/remove/tag subcommands
- Added `--watchlist` flag to prices and watch parsers for filtering to watched coins only
- Wired watchlist dispatch in `main()` with help text for bare `crypto watchlist`
- Added 11 CLI tests covering all subcommands and --watchlist filtering

**Commit:** `0f02680`

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed test_watchlist_add_no_tags assertion mismatch**
- **Found during:** Task 2 test verification
- **Issue:** Plan's test expected `add_watchlist_entry("BTC", None)` but `cmd_watchlist_add` converts None to `[]` via `args.tag or []`
- **Fix:** Updated test assertion to expect `[]` instead of `None` (functionally equivalent -- both produce empty tags)
- **Files modified:** tests/test_cli.py
- **Commit:** Included in `0f02680`

## Verification Results

- Task 1: 26/26 tests pass in test_watchlist_db.py
- Task 2: 37/37 watchlist-related tests pass (26 DB + 11 CLI)
- Full suite: 208/208 tests pass, zero regressions
- Smoke test: `crypto watchlist --help` shows all 4 subcommands

## Self-Check: PASSED

All created files exist, all commits verified.
