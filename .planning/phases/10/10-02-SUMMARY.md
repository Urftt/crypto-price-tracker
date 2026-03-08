---
phase: 10-multi-exchange
plan: 02
subsystem: web-exchange
tags: [exchange, web, api, react, sse, dropdown, frontend]
dependency_graph:
  requires: [exchange-abstraction, auto-fallback]
  provides: [exchange-api-param, exchange-dropdown, exchange-sse-reconnect, exchange-source-label]
  affects: [web, frontend, prices-page]
tech_stack:
  added: []
  patterns: [query-param-routing, prop-drilling, sse-reconnect-on-url-change]
key_files:
  created:
    - frontend/src/components/ExchangeDropdown.jsx
  modified:
    - src/crypto_price_tracker/web.py
    - frontend/src/App.jsx
    - frontend/src/pages/PricesPage.jsx
    - tests/test_web.py
decisions:
  - "Exchange param uses regex pattern validation (bitvavo|binance) returning 422 on invalid values"
  - "Effective exchange falls back to app.state.default_exchange when param omitted"
  - "Exchange state is per-session React useState (not persisted to localStorage)"
  - "Source label shown inline next to countdown timer and refresh button"
  - "useSSE.js unchanged -- URL dependency in useCallback handles reconnection automatically"
metrics:
  duration: "4 min"
  completed: "2026-03-07"
  tasks_completed: 3
  tasks_total: 3
  tests_before: 168
  tests_after: 172
---

# Phase 10 Plan 02: Web API and React Exchange Integration Summary

Exchange query param on all price API endpoints, ExchangeDropdown in React nav bar, SSE reconnect on exchange change, and "via Bitvavo/Binance" source label on Prices page.

## What Was Built

### Task 1: Update FastAPI Endpoints and Web Tests
Updated `src/crypto_price_tracker/web.py`:
- All price endpoints (/api/prices, /api/coin/{symbol}, /api/prices/stream) accept `?exchange=bitvavo|binance` query param with regex validation
- Responses include `"exchange"` field with actual source name (e.g., "Bitvavo", "Binance")
- Import changed from `get_top_coins` to `get_top_coins_with_fallback` from exchange module
- `app.state.default_exchange = "bitvavo"` set on app creation
- Portfolio endpoint updated to use `get_top_coins_with_fallback` with TimeoutException in exception list
- All 34 existing test mocks updated to `get_top_coins_with_fallback` returning `(coins, "Bitvavo")` tuple
- 4 new tests: exchange param on prices, default exchange, exchange param on coin, invalid exchange 422
- Commit: `b53875e`

### Task 2: ExchangeDropdown Component and App State
Created `frontend/src/components/ExchangeDropdown.jsx`:
- Simple select dropdown with Bitvavo/Binance options
- Styled with Tailwind classes matching existing component design
Updated `frontend/src/App.jsx`:
- Added `useState('bitvavo')` for exchange state management
- Dropdown placed in header with flex justify-between layout
- PricesPage receives exchange prop; PortfolioPage and AlertsPage unchanged
- Commit: `f74eaf7`

### Task 3: Exchange-Aware PricesPage with SSE Reconnect
Updated `frontend/src/pages/PricesPage.jsx`:
- Accepts `exchange` prop and builds SSE URL: `/api/prices/stream?exchange=${exchange}`
- When exchange changes, URL changes, useSSE's useCallback dependency triggers reconnection automatically
- Manual refresh includes exchange param in fetch URL
- Source label "via {exchange}" shown next to countdown timer
- useSSE.js required zero changes (existing URL dependency pattern handled it)
- Frontend rebuilt successfully
- All 172 tests pass
- Commit: `113c599`

## Deviations from Plan

None - plan executed exactly as written.

## Decisions Made

1. **Regex pattern validation**: Used FastAPI's `Query(pattern="^(bitvavo|binance)$")` for clean 422 rejection of invalid exchange values
2. **getattr fallback**: Used `getattr(app.state, "default_exchange", "bitvavo")` for safe attribute access
3. **No useSSE changes needed**: Confirmed the existing `useCallback([url])` dependency chain handles reconnection automatically when exchange prop changes
4. **Source label placement**: Inline with countdown timer and refresh button in the status bar area

## Verification Results

1. Full Python test suite: 172 passed (0 failed) -- 168 original + 4 new exchange tests
2. Frontend build: Vite build succeeds with no errors
3. Backward compatibility: All endpoints work without `?exchange=` param (defaults to bitvavo)
4. Invalid exchange: `?exchange=invalid` returns HTTP 422
