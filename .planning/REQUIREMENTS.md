# Requirements: Crypto Price Tracker — v2.0

**Defined:** 2026-03-09
**Core Value:** A slick, mobile-first UI that looks and feels great on every screen size.
**Theme:** UI polish — shared components, responsive design, mobile-optimized views, visual refinements.

## UI Component Library (Phase 15)

- [x] **COMP-01**: Shared `<Button>` component with variant props (primary, secondary, danger, ghost) replacing all inline button styles
- [x] **COMP-02**: Shared `<Input>` component with label, error state, and disabled state replacing all inline input styles
- [x] **COMP-03**: Shared `<Table>`, `<Th>`, `<Td>` primitives replacing duplicated table cell styles across PriceTable, WatchlistPage, and PortfolioTable
- [x] **COMP-04**: Shared `<Modal>` component with Escape-to-close, click-outside-to-close, focus trap, and enter/exit animation
- [x] **COMP-05**: Shared `<Badge>` component for tags, status indicators, and exchange labels
- [x] **COMP-06**: Shared `<NavTab>` component replacing duplicated NavLink className logic in App.jsx
- [x] **COMP-07**: All form fields have visible `<label>` elements (not just placeholder text)
- [x] **COMP-08**: Forms show a loading/disabled state during submission (prevent double-submit)

## Responsive Layout & Mobile Navigation (Phase 16)

- [x] **RESP-01**: Bottom tab bar navigation on mobile (< 768px) replacing the top tab bar
- [x] **RESP-02**: Responsive header that stacks title and controls vertically on narrow screens
- [x] **RESP-03**: All tables wrapped in `overflow-x-auto` containers to prevent horizontal overflow
- [x] **RESP-04**: Responsive breakpoints (`sm:`, `md:`, `lg:`) applied to page layouts, forms, and grid areas
- [x] **RESP-05**: Form inputs stack vertically on mobile, expand horizontally on desktop
- [x] **RESP-06**: Modal is full-screen on mobile (< 640px), centered card on desktop
- [x] **RESP-07**: Touch-friendly tap targets — all interactive elements are at least 44x44px on mobile

## Mobile-Optimized Data Views (Phase 17)

- [x] **MOB-01**: Price table switches to a card-based layout on mobile (< 640px) — one card per coin with key stats
- [x] **MOB-02**: Portfolio table switches to a card layout on mobile with expandable lot details
- [x] **MOB-03**: Watchlist table switches to a card layout on mobile with tag pills
- [x] **MOB-04**: Alerts display as stacked cards on mobile (already card-based, ensure proper spacing)
- [x] **MOB-05**: Loading skeleton placeholders shown while data is fetching (matching card/table layout)
- [x] **MOB-06**: Empty state illustrations/messages for tables with no data (portfolio, watchlist, alerts)

## Visual Polish & Animations (Phase 18)

- [ ] **VIS-01**: Page transition animations when switching tabs (subtle fade or slide)
- [ ] **VIS-02**: Modal open/close animations (fade + scale)
- [ ] **VIS-03**: Toast enter/exit animations (slide in from top-right, fade out)
- [ ] **VIS-04**: Button hover and active state transitions (smooth color shifts)
- [ ] **VIS-05**: Improved typography hierarchy — section headers, subheaders, body text sizes standardized
- [ ] **VIS-06**: Consistent spacing scale applied across all pages (no ad-hoc padding/margin values)
- [ ] **VIS-07**: Price change flash animation — brief highlight when a price updates via SSE
- [ ] **VIS-08**: PriceChart uses CSS custom property values instead of hardcoded hex colors

## Out of Scope (v2.0)

| Feature | Reason |
|---------|--------|
| Light mode / theme toggle | Dark-only, polish the existing theme |
| New backend features | Pure frontend milestone |
| New CLI features | Focus is web UI only |
| Component library package (npm) | Keep components in-app, not a separate package |
| Storybook or component docs | Unnecessary for this project size |

## Coverage

- **Total requirements:** 28
- **Complete:** 21
- **Incomplete:** 7
- **Coverage:** 75%

---
*Created: 2026-03-09*
