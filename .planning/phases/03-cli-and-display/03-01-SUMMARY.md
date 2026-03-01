---
phase: 03-cli-and-display
plan: 01
subsystem: ui
tags: [rich, terminal, display, color, table, formatter]

# Dependency graph
requires:
  - phase: 02-api-integration
    provides: CoinData dataclass and BitvavoClient used as input to display functions
provides:
  - render_price_table() function rendering colored terminal table from list[CoinData]
  - render_coin_detail() function rendering single-coin detail view from CoinData
  - rich library installed and integrated
affects: [03-cli-and-display plan 02 — CLI wiring will call these display functions]

# Tech tracking
tech-stack:
  added: [rich>=13.0]
  patterns: [Console injection for testability — optional Console parameter lets tests capture output via StringIO]

key-files:
  created:
    - src/crypto_price_tracker/display.py
    - tests/test_display.py
  modified:
    - pyproject.toml

key-decisions:
  - "Optional Console parameter pattern used in both functions so tests can capture output via rich.console.Console(file=io.StringIO())"
  - "Color applied via rich markup per-cell (not per-column) so negative values can be red and positive green within the same column"
  - "render_coin_detail uses rich.box.SIMPLE for a clean, borderless label/value layout"
  - "uv sync removes dev extras — must use uv sync --extra dev to retain pytest in virtualenv"

patterns-established:
  - "Console injection: pass Console(file=StringIO()) in tests to capture rich output without terminal"
  - "EUR formatting: f'EUR {value:,.2f}' for prices, f'EUR {value:,.0f}' for large volumes"
  - "Color markup: [green]{str}[/green] or [red]{str}[/red] applied inline per-cell"

requirements-completed: [DISP-01, DISP-02, DISP-03]

# Metrics
duration: 2min
completed: 2026-03-01
---

# Phase 3 Plan 01: Terminal Display Module Summary

**Rich-powered terminal display with color-coded price table and single-coin detail view using Console injection for testability**

## Performance

- **Duration:** 2 min
- **Started:** 2026-03-01T07:03:25Z
- **Completed:** 2026-03-01T07:05:22Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments

- Created `display.py` with `render_price_table()` and `render_coin_detail()` functions
- Table shows rank, symbol, name, EUR price (thousands-separated), color-coded 24h %, EUR volume
- Positive 24h changes rendered in green, negative in red using rich markup
- Detail view uses `rich.box.SIMPLE` for clean label/value layout
- 8 unit tests all passing, covering formatting, colors, edge cases (empty list)

## Task Commits

Each task was committed atomically:

1. **Task 1: Add rich dependency and create display module** - `22d827e` (feat)
2. **Task 2: Add unit tests for display module** - `8f3aaf2` (feat)

**Plan metadata:** (docs commit — TBD after SUMMARY creation)

## Files Created/Modified

- `src/crypto_price_tracker/display.py` — Terminal display module with render_price_table() and render_coin_detail()
- `tests/test_display.py` — 8 unit tests for display formatting, colors, EUR formatting, and edge cases
- `pyproject.toml` — Added rich>=13.0 to dependencies

## Decisions Made

- **Console injection pattern:** Both functions accept an optional `Console` parameter. Tests pass `Console(file=io.StringIO(), force_terminal=True, color_system="truecolor")` to capture output as a string for assertions without needing a real terminal.
- **Per-cell color markup:** Rich color is applied inline in the cell string (`[green]+1.67%[/green]`) rather than as a column style, so each row can independently be green or red based on its value.
- **SIMPLE box style for detail view:** `rich.box.SIMPLE` provides a clean borderless table with spacing, appropriate for a key/value detail layout.
- **Dev extras discovery:** Running `uv sync` without `--extra dev` removes pytest. Tests require `uv sync --extra dev` to retain the dev dependencies.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Added one additional test for volume formatting**
- **Found during:** Task 2 (writing tests)
- **Issue:** Plan specified 7 tests; an 8th test (`test_render_price_table_volume_formatting`) was added to also verify EUR volume uses thousands separators (e.g. "120,339,407") which is a stated requirement but not covered by the 7 planned tests
- **Fix:** Added `test_render_price_table_volume_formatting` as a bonus test
- **Files modified:** tests/test_display.py
- **Verification:** All 8 tests pass
- **Committed in:** 8f3aaf2 (Task 2 commit)

---

**Total deviations:** 1 minor addition (bonus test for completeness)
**Impact on plan:** Strictly additive. No plan behavior changed.

## Issues Encountered

- `uv sync` without `--extra dev` removes pytest from the virtualenv (dev dependencies are in `[project.optional-dependencies]`). Required `uv sync --extra dev` to run tests. No code changes needed.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `render_price_table(coins, console)` and `render_coin_detail(coin, console)` are ready for Plan 03-02 to wire into CLI subcommands
- Both functions follow the Console injection pattern, so the CLI simply calls them without passing a console (defaults to real terminal)
- No blockers

---
*Phase: 03-cli-and-display*
*Completed: 2026-03-01*

## Self-Check: PASSED

- FOUND: src/crypto_price_tracker/display.py
- FOUND: tests/test_display.py
- FOUND: .planning/phases/03-cli-and-display/03-01-SUMMARY.md
- FOUND: commit 22d827e (Task 1)
- FOUND: commit 8f3aaf2 (Task 2)
