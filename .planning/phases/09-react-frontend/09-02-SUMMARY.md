---
phase: 9
plan: 2
subsystem: frontend
tags: [react, portfolio, alerts, toast, crud, sse]
dependency_graph:
  requires: [09-01]
  provides: [portfolio-page, alerts-page, toast-notifications]
  affects: [frontend/, tests/test_web.py]
tech_stack:
  added: []
  patterns: [crud-forms, expandable-table-rows, toast-auto-dismiss, url-param-prefill, sse-triggered-alerts]
key_files:
  created:
    - frontend/src/pages/PortfolioPage.jsx
    - frontend/src/pages/AlertsPage.jsx
    - frontend/src/components/AddHoldingForm.jsx
    - frontend/src/components/PortfolioTable.jsx
    - frontend/src/components/AddAlertForm.jsx
    - frontend/src/components/AlertList.jsx
    - frontend/src/components/Toast.jsx
  modified:
    - frontend/src/pages/PricesPage.jsx
    - frontend/src/App.jsx
decisions:
  - useApi hook shared across all CRUD forms for consistent fetch wrapper usage
  - PortfolioTable uses inline lots expansion (click row to toggle) rather than separate modal
  - Toast notifications use module-level counter for unique IDs, seenAlertIds ref prevents duplicates across SSE pushes
  - AlertsPage reads and immediately clears URL symbol param for clean browser history
  - Tests unchanged -- Plan 09-01 already updated all 13 HTML-content tests to 4 SPA-appropriate tests
metrics:
  duration: 3m 10s
  completed: 2026-03-07
  tasks: 2
  tests_total: 152
---

# Phase 9 Plan 2: PortfolioPage, AlertsPage, Toast Notifications Summary

Full CRUD portfolio page with add form, aggregated holdings table, expandable lots, and delete; alerts page with add form, active/triggered sections, remove/clear-all; toast notifications for SSE-triggered alerts with deduplication and auto-dismiss.

## What Was Done

### Task 1: Build PortfolioPage with holdings table, add form, lots toggle, and delete
- Created `AddHoldingForm.jsx`: Form with symbol (uppercase), amount, buy price, buy date fields; POST to /api/portfolio on submit; error display; onAdded callback
- Created `PortfolioTable.jsx`: Aggregated holdings table with 8 columns (Symbol, Amount, Avg Buy, Current, Value, P&L EUR, P&L %, Alloc %); click row to expand/collapse individual lots fetched from /api/portfolio/lots/{symbol}; delete button per lot; color-coded P&L
- Created `PortfolioPage.jsx`: Loads portfolio data on mount, provides loadPortfolio callback to form and table for refresh, summary footer with total value and total P&L
- Updated `App.jsx`: Imported PortfolioPage, replaced portfolio placeholder route
- Build verified: `npm run build` succeeds

### Task 2: Build AlertsPage with form, active/triggered sections, toasts, and update tests
- Created `Toast.jsx`: Fixed-position toast with auto-dismiss via setTimeout, color by type (info/success/error), close button, accepts style prop for stacking
- Created `AddAlertForm.jsx`: Form with symbol, target price, direction (above/below select); POST to /api/alerts; defaultSymbol prop for pre-fill from CoinModal
- Created `AlertList.jsx`: Renders alert cards with symbol, target price, direction badge (color-coded), timestamps, remove button
- Created `AlertsPage.jsx`: Fetches alerts and splits by status (active/triggered); reads ?symbol= URL param via useSearchParams for pre-fill; remove individual alerts; clear all triggered
- Updated `PricesPage.jsx`: Added toast state array and seenAlertIds ref; when SSE data includes triggered_alerts, creates toast for each new alert ID; toasts stack with incrementing top offset
- Updated `App.jsx`: Imported AlertsPage, replaced alerts placeholder route
- Rebuilt frontend: `npm run build` succeeds
- All 152 Python tests pass (tests were already SPA-compatible from Plan 09-01)

## Deviations from Plan

None -- plan executed exactly as written. Tests did not need updating since Plan 09-01 already converted all HTML-content tests to SPA-appropriate tests.

## Verification

1. **Frontend build:** `npm run build` succeeds, output in `src/crypto_price_tracker/static/`
2. **Python tests:** All 152 tests pass (`uv run pytest tests/ -x -q`)
3. **All routes wired:** App.jsx has PricesPage (/), PortfolioPage (/portfolio), AlertsPage (/alerts)
4. **CoinModal Set Alert flow:** Navigates to /alerts?symbol=X, AlertsPage reads and pre-fills form

## Self-Check: PASSED

All 9 key files verified present. Both task commits (89ca6c3, 5ee112b) verified in git history.
