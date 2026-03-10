# Phase 17: Mobile-Optimized Data Views — Context

**Phase Goal:** Data-heavy tables transform into scannable card layouts on mobile
**Requirements:** MOB-01 through MOB-06
**Depends on:** Phase 15 (UI primitives), Phase 16 (responsive layout, touch targets)

## Requirements

| ID | Description | Priority |
|----|-------------|----------|
| MOB-01 | Price table switches to card-based layout on mobile (< 640px) — one card per coin with key stats | Must |
| MOB-02 | Portfolio table switches to card layout on mobile with expandable lot details | Must |
| MOB-03 | Watchlist table switches to card layout on mobile with tag pills | Must |
| MOB-04 | Alerts display as stacked cards on mobile (already card-based, ensure proper spacing) | Must |
| MOB-05 | Loading skeleton placeholders shown while data is fetching (matching card/table layout) | Must |
| MOB-06 | Empty state illustrations/messages for tables with no data (portfolio, watchlist, alerts) | Must |

## Success Criteria

1. PriceTable shows cards below 640px, table above
2. PortfolioTable shows cards below 640px with expandable lots
3. WatchlistPage shows cards below 640px with tag pills
4. Loading skeletons match the layout (cards on mobile, table rows on desktop)
5. Empty states show a message and visual cue when no data exists
6. All card layouts are touch-friendly with adequate spacing

## Plan Split

| Plan | Scope | Requirements |
|------|-------|-------------|
| 17-01 | Skeleton + EmptyState primitives, card layouts for PriceTable, PortfolioTable, WatchlistPage, AlertList spacing | MOB-01, MOB-02, MOB-03, MOB-04 |
| 17-02 | Loading skeleton integration across all pages, empty state integration across all pages | MOB-05, MOB-06 |

## Technical Decisions

1. **CSS-only layout toggle** — Use `sm:hidden` / `hidden sm:block` to switch between card and table views. No `useMediaQuery` hook needed.
2. **Card styling convention** — Reuse `bg-card border border-border rounded p-3` from AlertList. No Card primitive component.
3. **Skeleton primitive** — New `Skeleton.jsx` in `ui/` using Tailwind `animate-pulse bg-border rounded`. Simple div wrapper.
4. **EmptyState primitive** — New `EmptyState.jsx` in `ui/` with title + optional description. Text-centered layout.
5. **Fixed skeleton count** — 5 skeletons per view (don't try to match actual data length).
6. **PriceTable card columns** — Show symbol, name, price, 24h% change. Omit rank and volume on mobile. Keep star button.
7. **PortfolioTable card** — Show symbol, amount, value, P&L. Lot expansion via accordion pattern within card using existing `expandedSymbol` state.
8. **WatchlistPage card** — Show symbol, name, tag Badge pills, price, change. Edit/Remove actions.
9. **Touch feedback** — Add `active:bg-border/50` to clickable cards, `cursor-pointer` on all.
10. **Event propagation** — Preserve `e.stopPropagation()` on PriceTable star button in card layout.

## Key Files

### To Create
- `frontend/src/components/ui/Skeleton.jsx`
- `frontend/src/components/ui/__tests__/Skeleton.test.jsx`
- `frontend/src/components/ui/EmptyState.jsx`
- `frontend/src/components/ui/__tests__/EmptyState.test.jsx`

### To Modify
- `frontend/src/components/PriceTable.jsx` — Add card layout
- `frontend/src/components/PortfolioTable.jsx` — Add card layout with expandable lots
- `frontend/src/pages/WatchlistPage.jsx` — Add card layout with tag pills
- `frontend/src/components/AlertList.jsx` — Spacing adjustments
- `frontend/src/pages/PricesPage.jsx` — Skeleton loading + empty state
- `frontend/src/pages/PortfolioPage.jsx` — Skeleton loading + empty state
- `frontend/src/pages/AlertsPage.jsx` — Skeleton loading + empty state

## Research Reference

See: `.planning/phases/17/17-RESEARCH.md`
