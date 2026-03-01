---
phase: 04-web-dashboard
plan: 01
subsystem: api
tags: [fastapi, uvicorn, starlette, httpx, python]

# Dependency graph
requires:
  - phase: 02-api-integration
    provides: BitvavoClient, get_top_coins, CoinData dataclass
  - phase: 03-cli-display
    provides: cli.py main() with argparse subcommand pattern
provides:
  - FastAPI app with /api/prices and /api/coin/{symbol} JSON endpoints
  - run_server() helper for uvicorn startup
  - crypto web CLI subcommand with --port and --host options
  - 6 unit tests for web API endpoints using TestClient + mocks
affects:
  - 04-02 (frontend will consume /api/prices and /api/coin/{symbol})

# Tech tracking
tech-stack:
  added:
    - fastapi>=0.115
    - uvicorn[standard]>=0.34 (includes uvloop, websockets, watchfiles)
  patterns:
    - create_app() factory function — makes FastAPI app testable via fixture
    - dataclasses.asdict() for CoinData serialization (no Pydantic duplication)
    - Lazy import of run_server inside cmd_web — keeps CLI startup fast
    - TestClient + unittest.mock.patch for API unit tests without real HTTP

key-files:
  created:
    - src/crypto_price_tracker/web.py
    - tests/test_web.py
  modified:
    - pyproject.toml
    - src/crypto_price_tracker/cli.py

key-decisions:
  - "dataclasses.asdict() used for JSON serialization — avoids duplicate Pydantic models for CoinData"
  - "create_app() factory pattern chosen so TestClient can create fresh app per test"
  - "Lazy import of FastAPI/uvicorn inside cmd_web body keeps prices/watch/info startup fast"
  - "Static directory mount only applied if directory exists — safe before Plan 04-02 creates it"
  - "No CORS middleware added — frontend served from same origin"

patterns-established:
  - "create_app() factory: always use factory function for FastAPI apps to enable test isolation"
  - "Lazy CLI imports: import heavy optional deps (FastAPI, uvicorn) inside command functions, not at module top"

requirements-completed: [WEB-01, WEB-04]

# Metrics
duration: 2min
completed: 2026-03-01
---

# Phase 4 Plan 1: Web API Backend Summary

**FastAPI JSON API with /api/prices and /api/coin/{symbol} endpoints wired to Bitvavo via existing CoinData model, plus crypto web CLI subcommand starting uvicorn on configurable port**

## Performance

- **Duration:** 2 min
- **Started:** 2026-03-01T08:18:21Z
- **Completed:** 2026-03-01T08:19:57Z
- **Tasks:** 2
- **Files modified:** 4 (2 created, 2 updated)

## Accomplishments
- FastAPI application in web.py with /api/prices (top-N query param), /api/coin/{symbol} (404 on miss), and / (JSON fallback until static built)
- Module-level `app` instance enables `uvicorn crypto_price_tracker.web:app` directly
- `crypto web` subcommand with --port/-p and --host options, lazy-imported to keep other commands fast
- 6 unit tests covering all endpoints with mocked get_top_coins — no real HTTP calls in CI
- All 26 tests pass (6 new web + 20 existing CLI/display/API tests)

## Task Commits

Each task was committed atomically:

1. **Task 1: Add FastAPI/uvicorn dependencies and create web module** - `73a124a` (feat)
2. **Task 2: Add crypto web subcommand and write API tests** - `e554e2a` (feat)

**Plan metadata:** (docs commit follows)

## Files Created/Modified
- `src/crypto_price_tracker/web.py` - FastAPI app factory, /api/prices, /api/coin/{symbol}, / routes, run_server()
- `tests/test_web.py` - 6 unit tests using TestClient and mock for all endpoints
- `pyproject.toml` - Added fastapi>=0.115 and uvicorn[standard]>=0.34 to dependencies
- `src/crypto_price_tracker/cli.py` - Added cmd_web() function and web subparser registration

## Decisions Made
- Used `dataclasses.asdict()` for serialization rather than introducing Pydantic models — CoinData is already a stdlib dataclass and asdict() works perfectly
- `create_app()` factory pattern keeps the app testable: each test fixture calls create_app() for an isolated instance
- Lazy import of run_server inside cmd_web so fastapi/uvicorn import cost is zero for prices/watch/info commands
- Static directory mount guarded by `if STATIC_DIR.exists()` so the app starts cleanly before Plan 04-02 creates the frontend

## Deviations from Plan

None - plan executed exactly as written.

Minor note: `uv sync --extra dev` was needed to ensure pytest was available in the venv (consistent with the 03-01 decision that dev extras must be synced explicitly).

## Issues Encountered
- `uv run pytest` failed because dev extras had not been synced yet. Fixed by running `uv sync --extra dev` first — consistent with the known project pattern from Plan 03-01.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- JSON API backend is fully operational; /api/prices and /api/coin/{symbol} are ready for the frontend to consume
- `crypto web` launches the server on port 8000 by default
- Static directory mount is pre-wired — once Plan 04-02 creates src/crypto_price_tracker/static/, the server will serve assets automatically without code changes

---
*Phase: 04-web-dashboard*
*Completed: 2026-03-01*
