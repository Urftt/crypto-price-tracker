---
phase: 11-watchlist-tags
plan: 02
subsystem: watchlist-web
tags: [watchlist, tags, fastapi, react, frontend, api]
dependency_graph:
  requires: [watchlist_db, WatchlistEntry, VALID_TAGS, portfolio_db, web.py, PriceTable, App]
  provides: [watchlist-api-endpoints, WatchlistPage, star-icon, watchlist-nav-tab]
  affects: [web.py, PriceTable.jsx, App.jsx, test_web.py]
tech_stack:
  added: []
  patterns: [watchlist-enrichment-with-live-prices, star-icon-toggle, OR-based-tag-filtering, TAG_COLORS-map]
key_files:
  created:
    - frontend/src/pages/WatchlistPage.jsx
  modified:
    - src/crypto_price_tracker/web.py
    - frontend/src/components/PriceTable.jsx
    - frontend/src/App.jsx
    - tests/test_web.py
decisions:
  - "Watchlist endpoints placed before SPA catch-all to avoid route interception"
  - "GET /api/watchlist enriches entries with live prices via get_top_coins_with_fallback best-effort"
  - "Tag filtering uses OR logic on client side: entries matching ANY active tag shown"
  - "Star icon uses e.stopPropagation to prevent coin modal from opening on click"
  - "WatchlistPage uses same useApi hook pattern as PortfolioPage and AlertsPage"
metrics:
  duration: 3 min
  completed: "2026-03-07T15:18:10Z"
  tasks: 2
  tests_added: 16
  tests_total: 223
  files_created: 1
  files_modified: 4
---

# Phase 11 Plan 02: Watchlist & Tags -- Web Integration Summary

Watchlist REST API endpoints with live price enrichment, WatchlistPage with tag filter pills, PriceTable star icon for quick add/remove, and Watchlist nav tab.

## One-liner

FastAPI watchlist API (6 endpoints) with live price enrichment, React WatchlistPage with colored tag pills and OR filtering, and PriceTable star icon for one-click watchlist toggle.

## What Was Built

### Task 1: FastAPI watchlist endpoints and web API tests

- Added watchlist imports to web.py (import watchlist_db functions with aliases)
- Added `WatchlistAdd` and `WatchlistTagUpdate` Pydantic models
- Added 6 endpoints inside create_app() before the SPA catch-all route:
  - `GET /api/watchlist` -- returns entries enriched with live prices (price, change_24h, volume_eur, name), with optional `?tag=` filter
  - `POST /api/watchlist` -- 201 on success, 409 on duplicate, 400 on invalid tag
  - `DELETE /api/watchlist/{symbol}` -- 200 on success, 404 if not found
  - `PUT /api/watchlist/{symbol}/tags` -- 200 on success, 404 if not found, 400 on invalid tag
  - `GET /api/watchlist/tags` -- returns sorted list of 6 valid tags
  - `GET /api/watchlist/symbols` -- returns sorted set of watched symbols
- Added 16 web API tests covering all endpoints, status codes, and edge cases
- All 53 web tests pass

**Commit:** `67c0a6f`

### Task 2: WatchlistPage, PriceTable star icon, App routing, and frontend build

- Created `WatchlistPage.jsx` (213 lines) with:
  - Add-to-watchlist form (symbol input + tag selection pills + submit button)
  - Tag filter pills (6 colored pills, OR-based filtering, clear button)
  - Watchlist table (symbol, name, tags as colored pills, price, 24h%, volume, remove button)
  - TAG_COLORS map for 6 categories (Layer1=blue, Layer2=purple, DeFi=green, Meme=yellow, Exchange=orange, Privacy=red)
- Updated `PriceTable.jsx` with star icon column:
  - Fetches watchlist symbols on mount via `/api/watchlist/symbols`
  - Filled star (gold) for watched, outline for not watched
  - Click toggles via POST/DELETE API, `e.stopPropagation` prevents coin modal
- Updated `App.jsx`:
  - Imported WatchlistPage
  - Added Watchlist NavLink as 2nd tab (Prices, Watchlist, Portfolio, Alerts)
  - Added Route path="watchlist" element={<WatchlistPage />}
- Built frontend via `npm run build` -- Vite build succeeds
- All 223 tests pass with zero regressions

**Commit:** `5acbeda`

## Deviations from Plan

None -- plan executed exactly as written.

## Verification Results

- Task 1: 16/16 new watchlist API tests pass, 53 total web tests pass
- Task 2: Frontend builds without errors, all 223 tests pass across full suite
- SPA catch-all serves React app at /watchlist path
- GET /api/watchlist returns entries with live price data or null if not in top 100
- POST returns 201/409/400, DELETE returns 200/404, PUT tags returns 200/404/400

## Self-Check: PASSED
