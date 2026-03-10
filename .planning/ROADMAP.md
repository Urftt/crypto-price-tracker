# Roadmap: Crypto Price Tracker

## Completed Milestones

- **v1.0** — Full CLI + React SPA + SQLite persistence + multi-exchange + PWA (14 phases, 271 tests) — [Archive](milestones/v1.0-ROADMAP.md)

## Current Milestone: v2.0 — Slick UI

**Goal:** Mobile-first UI redesign with shared component library, responsive layouts, and visual polish.
**Scope:** 4 phases, frontend-only, no backend changes.

| # | Phase | Goal | Requirements | Status |
|---|-------|------|--------------|--------|
| 15 | UI Component Library | Extract shared primitives (Button, Input, Table, Modal, Badge, NavTab) and fix form accessibility | COMP-01 → COMP-08 | Complete (2/2) |
| 16 | Responsive Layout & Mobile Nav | Add responsive breakpoints, mobile bottom nav, full-screen modal, touch targets | RESP-01 → RESP-07 | Complete (2/2) |
| 17 | Mobile Data Views | Card-based table layouts on mobile, loading skeletons, empty states | MOB-01 → MOB-06 | Complete (2/2) |
| 18 | Visual Polish & Animations | Page transitions, modal/toast animations, typography, spacing, price flash | VIS-01 → VIS-08 | Complete (2/2) |

### Phase 15: UI Component Library
**Goal**: A set of shared, accessible UI primitives that eliminate style duplication and improve form UX
**Requirements**: COMP-01 through COMP-08
**Plans:** 2 plans

Plans:
- [x] 15-01-PLAN.md — Create 6 UI primitive components (Button, Input, Table, Modal, Badge, NavTab) + test infrastructure + unit tests
- [x] 15-02-PLAN.md — Refactor all existing components to use UI primitives, add visible labels, add form loading states

**Success Criteria**:
  1. `<Button>`, `<Input>`, `<Table>/<Th>/<Td>`, `<Modal>`, `<Badge>`, `<NavTab>` components exist in `src/components/ui/`
  2. All forms use `<Input>` with visible labels (not just placeholders)
  3. All buttons use `<Button>` with consistent variants
  4. Modal supports Escape key, click-outside, and focus trap
  5. No duplicate `inputClass` or button style strings remain anywhere in the codebase
  6. All 271+ existing tests still pass

### Phase 16: Responsive Layout & Mobile Navigation
**Goal**: The app looks good and is fully usable on mobile screens (320px-768px)
**Requirements**: RESP-01 through RESP-07
**Plans:** 2 plans

Plans:
- [x] 16-01-PLAN.md — Mobile bottom nav, responsive header, table overflow, responsive breakpoints, full-screen mobile modal (RESP-01, RESP-02, RESP-03, RESP-04, RESP-06)
- [x] 16-02-PLAN.md — Responsive forms, touch targets for all interactive elements (RESP-05, RESP-07)

**Success Criteria**:
  1. Mobile bottom tab bar appears below 768px, top tabs remain on desktop
  2. No horizontal overflow on any page at 320px viewport width
  3. Forms stack vertically on mobile, expand horizontally on desktop
  4. Modal fills the screen on mobile, remains a centered card on desktop
  5. All interactive elements meet 44x44px minimum tap target on mobile
  6. Header stacks vertically on narrow screens

### Phase 17: Mobile-Optimized Data Views
**Goal**: Data-heavy tables transform into scannable card layouts on mobile
**Requirements**: MOB-01 through MOB-06
**Plans:** 2 plans

Plans:
- [x] 17-01-PLAN.md — Mobile card layouts for PriceTable, PortfolioTable, WatchlistPage, AlertList spacing (MOB-01, MOB-02, MOB-03, MOB-04)
- [x] 17-02-PLAN.md — Skeleton + EmptyState primitives, loading skeletons and empty states across all pages (MOB-05, MOB-06)

**Success Criteria**:
  1. PriceTable shows cards below 640px, table above
  2. PortfolioTable shows cards below 640px with expandable lots
  3. WatchlistPage shows cards below 640px with tag pills
  4. Loading skeletons match the layout (cards on mobile, table rows on desktop)
  5. Empty states show a message and visual cue when no data exists
  6. All card layouts are touch-friendly with adequate spacing

### Phase 18: Visual Polish & Animations
**Goal**: Smooth transitions and consistent visual hierarchy make the app feel polished and professional
**Requirements**: VIS-01 through VIS-08
**Plans:** 2 plans

Plans:
- [x] 18-01-PLAN.md — CSS animation foundation, page transitions, modal enter/exit, toast animations, button press feedback, price flash (VIS-01, VIS-02, VIS-03, VIS-04, VIS-07)
- [x] 18-02-PLAN.md — Typography/spacing standardization, PriceChart CSS custom properties (VIS-05, VIS-06, VIS-08)

**Success Criteria**:
  1. Tab switching has a subtle transition animation
  2. Modal opens with fade+scale, closes with reverse
  3. Toasts slide in and fade out
  4. Buttons have smooth hover/active transitions
  5. Typography uses a consistent size scale (not ad-hoc)
  6. PriceChart reads theme colors from CSS custom properties
  7. Price changes flash briefly when updated via SSE
