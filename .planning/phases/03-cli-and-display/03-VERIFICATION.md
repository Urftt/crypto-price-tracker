---
phase: 03-cli-and-display
verified: 2026-03-01T08:00:00Z
status: gaps_found
score: 8/9 must-haves verified
re_verification: false
gaps:
  - truth: "`crypto prices` prints a formatted table of the top 20 coins with price, 24h change %, market cap, and volume, then exits"
    status: partial
    reason: "The price table renders price, 24h %, and volume correctly, but the roadmap success criterion and DISP-01 requirement both explicitly list 'market cap' as a required column. The CoinData model has no market_cap field and the display table has no Market Cap column. The API client documents that Bitvavo's public API does not expose market cap data and uses volume_eur as a proxy — but neither the model, nor the table, nor the detail view surface a market cap figure (even a labeled proxy). The requirement text is not met as written."
    artifacts:
      - path: "src/crypto_price_tracker/display.py"
        issue: "render_price_table has no Market Cap column; table columns are #, Symbol, Name, Price (EUR), 24h %, Volume (EUR)"
      - path: "src/crypto_price_tracker/models.py"
        issue: "CoinData dataclass has no market_cap field"
    missing:
      - "Either: add a market_cap field to CoinData (could be volume_eur renamed or supplemented), add a 'Market Cap (proxy)' column to render_price_table, and add it to render_coin_detail — OR update REQUIREMENTS.md DISP-01 and ROADMAP.md Phase 3 success criterion 1 to accurately reflect that market cap is not available from Bitvavo's public API and EUR volume is used instead"
human_verification:
  - test: "Run `crypto prices` against the live Bitvavo API and visually inspect the table"
    expected: "A rich-formatted color table appears with rank, symbol, name, EUR price with thousands separators, color-coded 24h %, and EUR volume. Positive changes are green, negative are red."
    why_human: "Color rendering cannot be programmatically verified in CI; requires a real terminal or careful ANSI escape inspection"
  - test: "Run `crypto info BTC` against the live Bitvavo API"
    expected: "A detail view appears showing BTC / Bitcoin header, then a label/value table with Price, 24h Change (color-coded), Volume, and Volume (EUR)"
    why_human: "Live API behavior and visual formatting require human confirmation"
  - test: "Run `crypto watch --interval 5` and wait for one refresh"
    expected: "Terminal clears, table re-renders, footer shows 'Refreshing every 5s — Ctrl+C to stop'. Ctrl+C exits cleanly with 'Stopped.'"
    why_human: "Interactive loop behavior and ANSI screen-clearing require manual observation"
---

# Phase 3: CLI and Display Verification Report

**Phase Goal:** Users can run all three subcommands and see formatted, color-coded crypto prices in the terminal
**Verified:** 2026-03-01T08:00:00Z
**Status:** gaps_found
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | "`crypto prices` prints a formatted table of the top 20 coins with price, 24h change %, market cap, and volume, then exits" | PARTIAL | Table renders with price, 24h %, and volume but **no market cap column**. DISP-01 and roadmap SC-1 both require market cap. CoinData has no `market_cap` field; Bitvavo public API does not expose it. |
| 2 | "`crypto watch` refreshes the price table every 30 seconds by default; `--interval N` overrides the refresh period" | VERIFIED | `cmd_watch` loop calls `get_top_coins`, `render_price_table`, then `time.sleep(args.interval)`. Default is 30s. `--interval` flag registered on watch subparser. Test `test_watch_command_parses_interval` passes. |
| 3 | "`crypto info BTC` shows a detailed single-coin view with expanded information" | VERIFIED | `cmd_info` normalises symbol to uppercase, fetches top 100, finds match, calls `render_coin_detail`. Detail view shows Price, 24h Change, Volume, Volume (EUR). |
| 4 | "Positive 24h change is displayed in green and negative in red in the terminal" | VERIFIED | `display.py` lines 35-38 apply `[green]...[/green]` for `change_24h >= 0` and `[red]...[/red]` for negative, in both table and detail view. Tests confirm the change values appear in captured output. |
| 5 | "A list of CoinData objects can be rendered as a formatted terminal table showing symbol, name, price, 24h change %, and volume" | VERIFIED | `render_price_table` builds a rich Table with all listed columns and iterates `coins` adding formatted rows. 8 display tests pass. |
| 6 | "A single CoinData object can be rendered as a detailed single-coin view with expanded information" | VERIFIED | `render_coin_detail` prints header then a SIMPLE-box table with Price, 24h Change, Volume, Volume (EUR). |
| 7 | "All EUR prices are formatted with 2 decimal places and a EUR prefix" | VERIFIED | `f"EUR {coin.price:,.2f}"` used for prices in both functions. `test_render_price_table_formats_prices_with_eur` asserts "EUR", "56,754.00", "2,345.50". |
| 8 | "Large numbers (volume, market cap) use thousands separators for readability" | PARTIAL | Volume uses `f"EUR {coin.volume_eur:,.0f}"` with thousands separator (verified by test checking "120,339,407"). Market cap is not present in the model or display. |
| 9 | "`crypto --help` lists all three subcommands with descriptions" | VERIFIED | `crypto --help` output shows `{prices,watch,info}` with descriptions "Display top cryptocurrency prices", "Auto-refresh cryptocurrency prices", "Show detailed info for a single coin". |

**Score:** 8/9 truths verified (1 partial due to missing market cap)

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/crypto_price_tracker/display.py` | Table renderer and single-coin detail formatter; exports render_price_table, render_coin_detail; min 60 lines | VERIFIED | 79 lines. Exports both functions. No stubs or TODOs. |
| `tests/test_display.py` | Unit tests for display formatting with color and layout assertions; min 50 lines | VERIFIED | 131 lines. 8 tests, all passing. Covers: all coins in output, EUR formatting, positive/negative change strings, empty list safety, volume thousands separator. |
| `src/crypto_price_tracker/cli.py` | CLI entry point with prices, watch, and info subcommands; exports main; min 60 lines | VERIFIED | 123 lines. Exports `main`. All three subcommands fully implemented. |
| `tests/test_cli.py` | CLI integration tests verifying subcommand behavior; min 40 lines | VERIFIED | 122 lines. 7 tests, all passing. API layer fully mocked. |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `display.py` | `models.py` | imports CoinData dataclass | WIRED | Line 9: `from crypto_price_tracker.models import CoinData`. Used as type annotation and attribute access throughout. |
| `display.py` | `rich` | uses rich.table.Table and rich.console.Console | WIRED | Lines 5-7: `import rich.box`, `from rich.console import Console`, `from rich.table import Table`. Both used substantively. |
| `tests/test_display.py` | `display.py` | imports render functions for testing | WIRED | Line 10: `from crypto_price_tracker.display import render_coin_detail, render_price_table`. Both called in tests. |
| `cli.py` | `api.py` | imports get_top_coins for data fetching | WIRED | Line 17: `from crypto_price_tracker.api import get_top_coins`. Called in all three cmd_* functions. |
| `cli.py` | `display.py` | imports render_price_table and render_coin_detail for output | WIRED | Line 18: `from crypto_price_tracker.display import render_coin_detail, render_price_table`. Called in cmd_prices, cmd_watch, cmd_info. |
| `cli.py` | `argparse` | subparsers for prices, watch, info commands | WIRED | Lines 76, 86, 103: `subparsers.add_parser("prices")`, `add_parser("watch")`, `add_parser("info")`. All three registered. |

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| DISP-01 | 03-01-PLAN.md | Prices shown in a formatted terminal table with price, 24h change %, **market cap**, and volume | PARTIAL | Table renders price, 24h %, and volume. Market cap is absent from the data model (CoinData has no `market_cap`), from the API client (Bitvavo public API does not expose market cap), and from the display table. The column requirement is not fully satisfied as written. |
| DISP-02 | 03-01-PLAN.md | 24h change is color-coded green (positive) or red (negative) | SATISFIED | `display.py` lines 35-38 apply rich markup `[green]` / `[red]` inline per-cell. Tests confirm +/- values appear in captured output. |
| DISP-03 | 03-01-PLAN.md | Single-coin detail view shows expanded information for one cryptocurrency | SATISFIED | `render_coin_detail` renders Price, 24h Change (color-coded), Volume, and Volume (EUR) in a SIMPLE-box table with a bold symbol/name header. |
| CLI-01 | 03-02-PLAN.md | `crypto prices` displays the price table once and exits | SATISFIED | `cmd_prices` calls `get_top_coins(top_n=args.top)` then `render_price_table(coins)` and returns. Test `test_prices_command_calls_api_and_renders` verifies with mocked API. |
| CLI-02 | 03-02-PLAN.md | `crypto watch` auto-refreshes the price table (default 30s, configurable via `--interval`) | SATISFIED | `cmd_watch` loops with `time.sleep(args.interval)`, default 30. `--interval` / `-i` flag registered on watch subparser. Test `test_watch_command_parses_interval` verifies. |
| CLI-03 | 03-02-PLAN.md | `crypto info <SYMBOL>` shows detailed info for a single coin | SATISFIED | `cmd_info` normalises to uppercase, fetches top 100, matches symbol, calls `render_coin_detail`. Test verifies match and case-insensitivity. |

**Orphaned requirements check:** REQUIREMENTS.md maps DISP-01, DISP-02, DISP-03, CLI-01, CLI-02, CLI-03 to Phase 3. All six appear in plan frontmatter. No orphaned requirements.

---

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| — | — | — | — | None found |

No TODOs, FIXMEs, placeholder returns, empty handlers, or unimplemented stubs detected in any phase 03 file.

---

### Human Verification Required

#### 1. Live price table visual inspection

**Test:** Run `crypto prices` in a terminal with color support
**Expected:** A rich-formatted table appears with rank numbers, bold symbols, coin names, EUR prices with thousands separators, green/red color-coded 24h % values, and EUR volumes. Command exits immediately after printing.
**Why human:** Color rendering (ANSI escape codes) requires a real terminal to verify visually. Automated tests capture rich output but cannot confirm the colors are perceptually correct.

#### 2. Single-coin detail view

**Test:** Run `crypto info BTC` in a terminal
**Expected:** Header line "BTC — Bitcoin" appears, followed by a clean label/value table showing Price, 24h Change (green or red), Volume (base asset with 4 decimals), and Volume (EUR) with thousands separator.
**Why human:** Layout quality and visual formatting require a human observer.

#### 3. Watch mode loop and graceful exit

**Test:** Run `crypto watch --interval 5`, observe one refresh cycle, then press Ctrl+C
**Expected:** Terminal clears (ANSI escape), table re-renders, footer "Refreshing every 5s — Ctrl+C to stop" appears. On Ctrl+C, prints "Stopped." and returns to shell prompt cleanly.
**Why human:** Interactive loop behavior and ANSI screen-clearing cannot be verified without an actual TTY.

---

### Gaps Summary

**1 gap blocking full requirement satisfaction:**

**DISP-01 / Roadmap SC-1 — Market Cap missing from price table**

The roadmap success criterion for `crypto prices` and DISP-01 both explicitly state that the price table should include "market cap." The CoinData data model has no `market_cap` field, the Bitvavo public API client explicitly documents that market cap data is unavailable from the public API, and the display table omits the column entirely (showing Volume EUR instead).

The API client correctly documents the design decision to use `volume_eur` as a market cap proxy, but this substitution was never surfaced in the table or requirements. As written, DISP-01 is not satisfied.

**Two resolution paths:**

- **Path A (code fix):** Add a `market_cap_proxy` field to CoinData populated from `volume_eur`, add a "Market Cap (EUR, proxy)" column to `render_price_table` and `render_coin_detail`, and update tests.
- **Path B (requirements update):** Update REQUIREMENTS.md DISP-01 and ROADMAP.md Phase 3 success criterion 1 to replace "market cap" with "EUR volume (used as market cap proxy)" — reflecting the known API limitation documented in `api.py`.

Path B is lower effort and matches actual intent; Path A adds a column label that clarifies the proxy nature of the data.

---

_Verified: 2026-03-01T08:00:00Z_
_Verifier: Claude (gsd-verifier)_
