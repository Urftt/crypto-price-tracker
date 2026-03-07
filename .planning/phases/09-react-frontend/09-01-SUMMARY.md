---
phase: 9
plan: 1
subsystem: frontend
tags: [react, vite, tailwind, sse, recharts, react-router, spa]
dependency_graph:
  requires: [08-02]
  provides: [sse-endpoint, spa-catch-all, react-shell, prices-page, coin-modal, price-chart]
  affects: [web.py, test_web.py, frontend/]
tech_stack:
  added: [react-19, react-router-7, recharts-3, tailwindcss-4, vite-7, "@tailwindcss/vite"]
  patterns: [sse-endpoint, spa-catch-all, useSSE-hook, css-first-theme, navlink-tabs]
key_files:
  created:
    - frontend/index.html
    - frontend/package.json
    - frontend/vite.config.js
    - frontend/src/main.jsx
    - frontend/src/App.jsx
    - frontend/src/index.css
    - frontend/src/lib/format.js
    - frontend/src/hooks/useSSE.js
    - frontend/src/hooks/useApi.js
    - frontend/src/pages/PricesPage.jsx
    - frontend/src/components/PriceTable.jsx
    - frontend/src/components/CountdownTimer.jsx
    - frontend/src/components/CoinModal.jsx
    - frontend/src/components/PriceChart.jsx
    - frontend/.gitignore
  modified:
    - src/crypto_price_tracker/web.py
    - tests/test_web.py
    - .gitignore
decisions:
  - FastAPI EventSourceResponse for SSE (built-in since 0.135.0, no extra dependency)
  - SPA catch-all replaces both old @app.get("/") and app.mount("/static")
  - Import from 'react-router' not 'react-router-dom' (React Router v7)
  - Tailwind v4 CSS-first @theme config (no tailwind.config.js)
  - nl-NL locale for EUR formatting with Intl.NumberFormat
  - formatPct divides by 100 before formatting (API returns raw percentage)
  - Updated 13 old HTML-content tests to 4 new SPA-appropriate tests
metrics:
  duration: 4m 54s
  completed: 2026-03-07
  tasks: 3
  tests_updated: 13
  tests_total: 152
---

# Phase 9 Plan 1: Backend SSE Endpoint + React Frontend Shell with PricesPage and CoinModal Summary

SSE endpoint pushing prices every 10s via FastAPI EventSourceResponse, Vite + React + Tailwind frontend scaffold with GitHub-dark theme, and full PricesPage with SSE auto-update, countdown timer, manual refresh, clickable price table, and CoinModal with Recharts line chart (7D/30D toggle).

## What Was Done

### Task 1: Add SSE endpoint and SPA catch-all to FastAPI backend
- Added `/api/prices/stream` SSE endpoint using `EventSourceResponse` and `ServerSentEvent`
- SSE pushes price + triggered alert data as JSON every 10 seconds
- Replaced `@app.get("/")` and `app.mount("/static", ...)` with SPA catch-all `@app.get("/{path:path}")`
- Catch-all serves static files first, falls back to `index.html`, then JSON fallback
- Removed `StaticFiles` import (no longer needed)
- Added imports: `asyncio`, `json`, `AsyncIterable`, `EventSourceResponse`, `ServerSentEvent`
- All 43 existing tests passed after this change (before Vite build replaced index.html)

### Task 2: Scaffold Vite + React + Tailwind frontend project
- Created `frontend/` directory with `npm create vite@latest . -- --template react`
- Installed: `tailwindcss`, `@tailwindcss/vite`, `recharts`, `react-router`
- Configured `vite.config.js` with proxy to localhost:8000 and build output to `../src/crypto_price_tracker/static`
- Created `index.css` with Tailwind v4 `@theme` directive defining GitHub-dark color palette
- Created `main.jsx` with BrowserRouter wrapping App
- Created `App.jsx` with NavLink tabs (Prices, Portfolio, Alerts) and Routes
- Created `format.js` with `formatEUR`, `formatEURCompact`, `formatPct` using nl-NL locale
- Created `useSSE.js` hook with EventSource auto-reconnect
- Created `useApi.js` fetch wrapper with get/post/put/del methods
- Updated root `.gitignore` with frontend entries
- Removed Vite boilerplate: App.css, vite.svg, react.svg
- Build succeeded: output to `src/crypto_price_tracker/static/`

### Task 3: Build PricesPage with SSE, countdown, refresh, CoinModal with Recharts chart
- Created `PricesPage.jsx`: SSE subscription via useSSE, manual refresh via fetch, countdown timer, coin selection for modal
- Created `PriceTable.jsx`: 6-column table (#, Symbol, Name, Price EUR, 24h %, Volume EUR) with clickable rows, color-coded 24h change
- Created `CountdownTimer.jsx`: Counts down from 10s, resets on lastUpdate change, shows remaining time with accent color
- Created `CoinModal.jsx`: Modal overlay with coin details (price, 24h change, volume), PriceChart, and "Set Alert" button navigating to /alerts?symbol=X
- Created `PriceChart.jsx`: Recharts LineChart with 7D/30D toggle, fetches from /api/candles/{symbol}, dark theme styling
- Updated `test_web.py`: Replaced 13 old HTML-content tests (checking old monolithic index.html elements) with 4 new SPA-appropriate tests (checking root div, SPA routing for /portfolio and /alerts, static asset references)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Updated HTML-content tests for React SPA**
- **Found during:** Task 3 verification
- **Issue:** Vite build replaced the old monolithic `index.html` with the React SPA, causing 13 tests that checked for old HTML elements (Plotly script, tab divs, modal elements, etc.) to fail
- **Fix:** Replaced 13 old tests with 4 new SPA-appropriate tests checking for React root element, SPA catch-all routing, and static asset references
- **Files modified:** `tests/test_web.py`
- **Commit:** fef29ca

## Verification

1. **Python tests:** All 152 tests pass (`uv run pytest -x -q`)
2. **Frontend build:** `npm run build` succeeds, output in `src/crypto_price_tracker/static/`
3. **API tests:** All 30 API endpoint tests pass (prices, coin, portfolio, alerts, candles)
4. **SPA routing:** Catch-all serves index.html for /, /portfolio, /alerts

## Self-Check: PASSED

All 17 key files verified present. All 3 task commits (c34b6a5, 3238ec1, fef29ca) verified in git history.
