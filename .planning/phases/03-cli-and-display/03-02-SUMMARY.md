---
phase: 03-cli-and-display
plan: 02
subsystem: ui
tags: [argparse, cli, httpx, rich, terminal, subcommands]

# Dependency graph
requires:
  - phase: 02-api-integration
    provides: get_top_coins() convenience function and BitvavoClient used for live data fetching
  - phase: 03-cli-and-display
    plan: 01
    provides: render_price_table() and render_coin_detail() display functions
provides:
  - main() CLI entry point with prices, watch, and info subcommands wired to live API and display module
  - cmd_prices(): fetches top N coins and renders table then exits
  - cmd_watch(): ANSI-clearing auto-refresh loop with configurable interval and graceful KeyboardInterrupt exit
  - cmd_info(): normalises symbol, searches top 100, renders detail or exits 1 if not found
  - 7 CLI integration tests covering all command paths
affects: [v1.0 feature-complete -- no further phases required]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "argparse subparsers pattern: three subcommands (prices, watch, info) registered on a single ArgumentParser"
    - "Per-iteration error isolation in watch loop: HTTP errors caught inside while-True so one failure does not kill the watcher"
    - "httpx exception types imported at top-level and used in except clauses across all three command functions"

key-files:
  created:
    - tests/test_cli.py
  modified:
    - src/crypto_price_tracker/cli.py

key-decisions:
  - "argparse retained (no click/typer) per plan -- stdlib only for CLI parsing"
  - "cmd_watch catches errors inside the loop so a transient network failure does not kill the refresh session"
  - "cmd_info fetches top 100 coins (not just 20) to maximise symbol lookup coverage"
  - "ANSI escape sequence used for screen clearing in watch (\\033[2J\\033[H) -- no external dep required"

patterns-established:
  - "CLI dispatch: if args.command == 'X': cmd_X(args) chain rather than setting defaults on subparsers"
  - "Symbol normalisation: args.symbol.upper() before any lookup so input is always case-insensitive"

requirements-completed: [CLI-01, CLI-02, CLI-03]

# Metrics
duration: 2min
completed: 2026-03-01
---

# Phase 3 Plan 02: CLI Subcommands Summary

**argparse-based prices/watch/info subcommands wired to BitvavoClient and rich display module, completing the v1.0 CLI feature set**

## Performance

- **Duration:** 2 min
- **Started:** 2026-03-01T07:07:44Z
- **Completed:** 2026-03-01T07:09:28Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Rewrote `cli.py` with full implementations of all three subcommands using argparse
- `crypto prices` fetches top N coins (default 20, configurable with -n) and renders a rich table then exits
- `crypto watch` clears the terminal and refreshes every N seconds (default 30, configurable with -i/--interval), exits gracefully on Ctrl+C
- `crypto info SYMBOL` normalises the symbol to uppercase, searches the top 100 EUR pairs, renders the detail view or exits with code 1
- All HTTP errors caught and printed to stderr; watch loop isolates per-iteration errors so one failed refresh does not kill the session
- 7 integration tests all passing — no live HTTP calls (API layer fully mocked)

## Task Commits

Each task was committed atomically:

1. **Task 1: Implement prices, watch, and info subcommands in cli.py** - `6f52b19` (feat)
2. **Task 2: Add CLI integration tests** - `92deafd` (feat)

**Plan metadata:** (docs commit follows)

## Files Created/Modified

- `src/crypto_price_tracker/cli.py` - Complete rewrite with cmd_prices, cmd_watch, cmd_info and full argparse subcommand registration
- `tests/test_cli.py` - 7 integration tests covering all subcommand behaviours with mocked API layer

## Decisions Made

- **argparse retained:** No third-party CLI framework (click/typer) as specified. stdlib argparse with `add_subparsers` handles all three subcommands cleanly.
- **Error isolation in watch loop:** The try/except for HTTP errors is placed inside the `while True` loop rather than outside it, so a transient API failure prints an error and retries on the next interval rather than terminating the session.
- **Top-100 search in cmd_info:** The info command fetches 100 coins rather than 20 to increase the chance of finding less-common symbols (BTC and ETH would appear in top 20, but smaller coins might not).
- **ANSI escape for screen clear:** `\033[2J\033[H` used in watch mode. No external dependency needed; works on all common terminals.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `crypto prices`, `crypto watch`, and `crypto info` are all live and working against the Bitvavo API
- v1.0 feature set is complete — all three phases executed successfully
- No blockers

---
*Phase: 03-cli-and-display*
*Completed: 2026-03-01*

## Self-Check: PASSED

- FOUND: src/crypto_price_tracker/cli.py
- FOUND: tests/test_cli.py
- FOUND: .planning/phases/03-cli-and-display/03-02-SUMMARY.md
- FOUND: commit 6f52b19 (Task 1)
- FOUND: commit 92deafd (Task 2)
