---
phase: "06"
plan: "01"
subsystem: portfolio-backend
tags: [sqlite, portfolio, aggregation, export, dataclass]
dependency_graph:
  requires: [models.py (CoinData)]
  provides: [Holding, portfolio_db, portfolio]
  affects: [tests/conftest.py]
tech_stack:
  added: [sqlite3 (stdlib)]
  patterns: [connection-per-call, WAL journal mode, XDG path resolution, row factory]
key_files:
  created:
    - src/crypto_price_tracker/portfolio_db.py
    - src/crypto_price_tracker/portfolio.py
    - tests/conftest.py
    - tests/test_portfolio_db.py
    - tests/test_portfolio.py
  modified:
    - src/crypto_price_tracker/models.py
decisions:
  - "stdlib sqlite3 only -- no ORM, no new dependencies"
  - "Connection-per-call with try/finally close for CLI/web concurrency safety"
  - "WAL journal mode set on every connection open"
  - "XDG_DATA_HOME with fallback to ~/.local/share for DB path"
  - "Row factory returns Holding instances directly from queries"
  - "Unpriced coins included at cost basis in total_value"
metrics:
  duration: "~3 min"
  completed: "2026-03-06"
  tasks_completed: 5
  tasks_total: 5
  tests_added: 28
  tests_total: 61
---

# Phase 6 Plan 1: Backend -- Storage Layer, Aggregation Service, and Export Summary

SQLite CRUD with WAL mode and XDG path resolution, P&L aggregation with allocation percentages, CSV/JSON export -- all tested with 28 new tests (61 total, zero regressions).

## What Was Built

### Holding Dataclass (models.py)
Added `Holding` dataclass with `slots=True` alongside existing `CoinData`. Fields: `id`, `symbol`, `amount`, `buy_price`, `buy_date` (ISO 8601 string).

### SQLite Storage Layer (portfolio_db.py)
Complete CRUD module with 9 functions:
- `_get_default_db_path()` -- XDG_DATA_HOME resolution with mkdir
- `_holding_factory()` -- Custom row factory returning Holding instances
- `get_connection()` -- WAL mode, foreign keys, schema bootstrap
- `_ensure_schema()` -- CREATE TABLE IF NOT EXISTS with CHECK constraints
- `add_holding()` -- INSERT with date validation, symbol uppercasing, auto-date default
- `remove_holding()` -- DELETE by ID, returns bool
- `update_holding()` -- Dynamic SET clause from non-None kwargs
- `get_all_holdings()` -- SELECT ordered by symbol, buy_date
- `get_holdings_by_symbol()` -- Filtered SELECT with uppercase normalization

Every function uses connection-per-call pattern with try/finally cleanup.

### Aggregation Service (portfolio.py)
- `PortfolioRow` and `PortfolioSummary` dataclasses (slots=True)
- `aggregate_portfolio()` -- Groups holdings by symbol, computes per-coin totals, avg buy price, current value, P&L (EUR + %), allocation %, handles unpriced coins (None fields, cost basis in total)
- `export_csv()` -- DictWriter with StringIO
- `export_json()` -- json.dumps with indent=2

### Test Infrastructure
- `tests/conftest.py` -- Shared fixtures: `tmp_db_path`, `sample_holdings`, `sample_prices`
- `tests/test_portfolio_db.py` -- 17 tests covering all CRUD operations, schema, WAL mode, XDG path, row factory, edge cases
- `tests/test_portfolio.py` -- 11 tests covering aggregation, multi-lot, allocation %, unpriced coins, sorting, CSV/JSON export, summary totals

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed row factory conflict in schema test**
- **Found during:** Task 5 (test execution)
- **Issue:** `test_schema_created_on_connect` queried `sqlite_master` through the custom `_holding_factory` row factory, which tried to construct a `Holding` from a metadata row (column `name` is not a Holding field)
- **Fix:** Added `conn.row_factory = None` before the metadata query in the test, same pattern already used in `test_wal_mode_enabled`
- **Files modified:** tests/test_portfolio_db.py
- **Commit:** ac53a83

## Decisions Made

1. **stdlib sqlite3 only** -- No ORM or external DB library needed
2. **Connection-per-call** -- Each function opens and closes its own connection for safe concurrent use
3. **WAL journal mode** -- Set on every connection for CLI/web concurrency
4. **XDG path resolution** -- Manual 3-line implementation, no platformdirs dependency
5. **Row factory pattern** -- `_holding_factory` returns Holding instances directly, but requires `conn.row_factory = None` override for non-Holding queries
6. **Unpriced coins at cost basis** -- Coins not in top 100 contribute their cost basis to total_value

## Test Results

```
61 passed in 3.70s
- 17 storage tests (test_portfolio_db.py)
- 11 aggregation/export tests (test_portfolio.py)
- 33 existing tests (API, CLI, display, web) -- zero regressions
```

## Interfaces Created (for Plan 06-02)

```python
# models.py
Holding(id, symbol, amount, buy_price, buy_date)

# portfolio_db.py
add_holding(symbol, amount, buy_price, buy_date?, *, db_path?) -> int
remove_holding(holding_id, *, db_path?) -> bool
update_holding(holding_id, *, amount?, buy_price?, buy_date?, db_path?) -> bool
get_all_holdings(*, db_path?) -> list[Holding]
get_holdings_by_symbol(symbol, *, db_path?) -> list[Holding]

# portfolio.py
aggregate_portfolio(holdings, prices) -> PortfolioSummary
export_csv(holdings) -> str
export_json(holdings) -> str
```

## Self-Check: PASSED

All 7 files verified on disk. Commit ac53a83 confirmed in git log.
