---
phase: 17
plan: 1
subsystem: frontend
tags: [mobile, cards, responsive]
dependency_graph:
  requires: [16-02]
  provides: [mobile-card-layouts]
  affects: [PriceTable, PortfolioTable, WatchlistPage, AlertList]
tech_stack:
  added: []
  patterns: [sm:hidden/hidden-sm:block CSS toggle, Fragment wrapper for dual layouts, space-y for card spacing]
key_files:
  modified:
    - frontend/src/components/PriceTable.jsx
    - frontend/src/components/PortfolioTable.jsx
    - frontend/src/pages/WatchlistPage.jsx
    - frontend/src/components/AlertList.jsx
decisions:
  - CSS-only sm:hidden / hidden sm:block toggle for card vs table view
  - Fragment wrapper pattern to hold both mobile card and desktop table views
  - Cards omit rank, volume, and allocation columns for mobile scannability
  - AlertList uses parent space-y-3 instead of per-card mb-2 for spacing
metrics:
  duration: 3 min
  completed: 2026-03-10
  tasks_completed: 2
  tasks_total: 2
  files_modified: 4
---

# Phase 17 Plan 01: Mobile Card Layouts Summary

CSS-only card layouts for PriceTable, PortfolioTable, and WatchlistPage below 640px using sm:hidden/hidden sm:block toggle, with AlertList spacing audit.

## Completed Tasks

### Task 1: Add card layouts to PriceTable and PortfolioTable
- **PriceTable**: Added mobile card view showing symbol, name, price, 24h% change, and star button. Card has `active:bg-border/50` touch feedback and `cursor-pointer`. Star button preserves `e.stopPropagation()` for watchlist toggle. Table wrapped in `hidden sm:block overflow-x-auto`.
- **PortfolioTable**: Added mobile card view with symbol, lot count, value, P&L EUR, P&L%. Card tap expands lots via existing `expandedSymbol` state. Expanded lots section shows lot ID, buy price, amount (with inline edit input), buy date, and Edit/Delete/Save/Cancel buttons. All `e.stopPropagation()` patterns preserved. Table wrapped in `hidden sm:block max-w-4xl overflow-x-auto`.
- **Commit**: d30e2c6

### Task 2: Add card layout to WatchlistPage and audit AlertList spacing
- **WatchlistPage**: Added mobile card view with symbol, name, Badge tag pills (using TAG_COLOR_MAP colorScheme), price, 24h% change, Edit Tags and Remove action buttons. Inline tag editing with toggle buttons + Save/Cancel works identically to table version. Tag toggle buttons retain `min-h-11 md:min-h-0` touch targets from Phase 16.
- **AlertList**: Changed outer container from no spacing class to `space-y-3` for consistent 12px gaps. Removed `mb-2` from individual card divs. All other card styling unchanged.
- **Commit**: d30e2c6

## Decisions Made

1. **CSS-only layout toggle**: Used `sm:hidden` / `hidden sm:block` to switch between card and table views without any JavaScript media query hooks.
2. **Fragment wrapper**: Both mobile cards and desktop table wrapped in React Fragment (`<>...</>`) replacing previous single outer div.
3. **Column omission on mobile**: Cards omit rank (#), volume, allocation %, and other less-scannable columns -- focused on key stats.
4. **AlertList space-y-3**: Parent-level spacing with `space-y-3` instead of per-card `mb-2` for cleaner, more consistent gaps.

## Deviations from Plan

None -- plan executed exactly as written.

## Verification Results

- All 54 frontend tests pass (vitest)
- Frontend build succeeds (vite build)
- `sm:hidden` class present in PriceTable, PortfolioTable, WatchlistPage
- `hidden sm:block` class present in PriceTable, PortfolioTable, WatchlistPage
- `active:bg-border/50` present in PriceTable and PortfolioTable cards
- `stopPropagation` preserved in PriceTable star button
- `space-y-3` present in AlertList outer container
- `mb-2` no longer present in AlertList
- `Badge` component used in WatchlistPage card view

## Commits

| Hash | Message |
|------|---------|
| d30e2c6 | feat(17-01): mobile card layouts for price, portfolio, watchlist tables |

## Self-Check: PASSED

All 4 modified files verified on disk. Commit d30e2c6 verified in git log.
