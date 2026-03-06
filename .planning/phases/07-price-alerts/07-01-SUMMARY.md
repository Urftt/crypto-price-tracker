---
phase: "07"
plan: "01"
subsystem: alerts-backend
tags: [sqlite, alerts, price-alerts, dataclass, pure-function]
dependency_graph:
  requires: [models.py (CoinData), portfolio_db.py (_get_default_db_path)]
  provides: [PriceAlert, alerts_db, alerts]
  affects: [tests/conftest.py]
tech_stack:
  added: []
  patterns: [connection-per-call, WAL journal mode, module-level import for patchability, pure checking function, race-condition guard]
key_files:
  created:
    - src/crypto_price_tracker/alerts_db.py
    - src/crypto_price_tracker/alerts.py
    - tests/test_alerts_db.py
    - tests/test_alerts.py
  modified:
    - src/crypto_price_tracker/models.py
    - tests/conftest.py
decisions:
  - "alerts_db.py imports portfolio_db as module (not from-import) so test patches propagate"
  - "Both alerts and holdings tables share the same SQLite DB file"
  - "check_alerts() is pure -- no DB side effects, caller handles mark_triggered"
  - "Race condition guard: UPDATE WHERE status='active' prevents double-triggering"
  - "Direction validated in Python (ValueError) AND via SQLite CHECK constraint"
  - "get_all_alerts orders active-first then triggered for display readiness"
metrics:
  duration: "~2 min"
  completed: "2026-03-06"
  tasks_completed: 3
  tasks_total: 3
  tests_added: 31
  tests_total: 161
---

# Phase 7 Plan 1: Backend -- PriceAlert Model, SQLite CRUD, Alert Checking Logic, and Unit Tests Summary

PriceAlert dataclass with SQLite CRUD mirroring portfolio_db.py patterns, pure check_alerts() function for above/below price triggers, plus 31 comprehensive tests (20 DB + 11 checking logic) -- all passing with zero regressions.

## What Was Built

### PriceAlert Dataclass (models.py)
Added `PriceAlert` dataclass with `slots=True` alongside existing `CoinData` and `Holding`. Fields: `id`, `symbol`, `target_price`, `direction` ("above"/"below"), `status` ("active"/"triggered"), `created_at` (ISO 8601), `triggered_at` (ISO 8601 or None).

### SQLite Storage Layer (alerts_db.py)
Complete CRUD module with 9 functions mirroring portfolio_db.py patterns:
- `_alert_factory()` -- Custom row factory returning PriceAlert instances
- `_ensure_alert_schema()` -- CREATE TABLE IF NOT EXISTS with CHECK constraints on direction, status, and target_price
- `get_alert_connection()` -- WAL mode, foreign keys, schema bootstrap, uses `portfolio_db._get_default_db_path()` via module reference
- `add_alert()` -- INSERT with direction validation (ValueError), symbol uppercasing, auto-timestamp
- `get_active_alerts()` -- SELECT WHERE status='active' ordered by created_at
- `get_all_alerts()` -- SELECT ordered active-first then triggered (CASE WHEN), then by created_at
- `remove_alert()` -- DELETE by ID, returns bool
- `mark_triggered()` -- UPDATE with AND status='active' race condition guard, sets triggered_at timestamp
- `clear_triggered_alerts()` -- DELETE WHERE status='triggered', returns count

Every function uses connection-per-call pattern with try/finally cleanup, identical to portfolio_db.py.

### Alert Checking Service (alerts.py)
- `check_alerts(coins, active_alerts) -> list[PriceAlert]` -- Pure function that builds a price lookup dict from coins, then checks each alert: "above" triggers at `>=`, "below" triggers at `<=`. Coins not in fetched data are skipped (alert stays active). Function is stateless -- caller is responsible for passing only active alerts and calling mark_triggered() on results.

### Test Infrastructure
- `tests/conftest.py` -- Added `PriceAlert` import and `sample_alerts` fixture (3 alerts: active BTC above, active ETH below, triggered BTC above)
- `tests/test_alerts_db.py` -- 20 tests covering: connection/schema/WAL creation, add with ID/uppercase/default direction/below/invalid direction, get active empty/filtered/only-active, get all ordering, remove success/not-found, mark triggered success/double-trigger/not-found, clear triggered/preserves-active, row factory type check, both tables coexist in same DB
- `tests/test_alerts.py` -- 11 tests covering: no alerts/no coins, above triggers/exact match/not reached, below triggers/exact match/not reached, coin not in prices, multiple triggers, stateless status check

## Deviations from Plan

None -- plan executed exactly as written.

## Decisions Made

1. **Module-level import for patchability** -- `from crypto_price_tracker import portfolio_db` ensures test patches to `portfolio_db._get_default_db_path` propagate to alerts_db
2. **Same DB file** -- Alerts table lives in `portfolio.db` alongside holdings, avoiding multi-DB complexity
3. **Pure checking function** -- `check_alerts()` has zero side effects, making it trivially testable without DB fixtures
4. **Race condition guard** -- `WHERE id=? AND status='active'` prevents double-triggering in concurrent requests
5. **Dual validation** -- Direction validated in Python (ValueError on bad input) AND via SQLite CHECK constraint (defense in depth)
6. **Active-first ordering** -- `get_all_alerts()` sorts active before triggered for direct display use

## Test Results

```
161 passed in 14.36s
- 20 alerts DB tests (test_alerts_db.py)
- 11 alerts checking tests (test_alerts.py)
- 130 existing tests (API, CLI, display, web, portfolio DB, portfolio, charts) -- zero regressions
```

## Interfaces Created (for Plan 07-02)

```python
# models.py
PriceAlert(id, symbol, target_price, direction, status, created_at, triggered_at)

# alerts_db.py
get_alert_connection(db_path?) -> Connection
add_alert(symbol, target_price, direction="above", *, db_path?) -> int
get_active_alerts(*, db_path?) -> list[PriceAlert]
get_all_alerts(*, db_path?) -> list[PriceAlert]
remove_alert(alert_id, *, db_path?) -> bool
mark_triggered(alert_id, *, db_path?) -> bool
clear_triggered_alerts(*, db_path?) -> int

# alerts.py
check_alerts(coins, active_alerts) -> list[PriceAlert]
```

## Self-Check: PASSED

All 6 files verified on disk. Commit 97da428 confirmed in git log.
