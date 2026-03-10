# Phase 16 Context: Responsive Layout & Mobile Navigation

## Goal
The app looks good and is fully usable on mobile screens (320px-768px).

## Requirements
- RESP-01: Bottom tab bar navigation on mobile (< 768px) replacing the top tab bar
- RESP-02: Responsive header that stacks title and controls vertically on narrow screens
- RESP-03: All tables wrapped in `overflow-x-auto` containers to prevent horizontal overflow
- RESP-04: Responsive breakpoints (`sm:`, `md:`, `lg:`) applied to page layouts, forms, and grid areas
- RESP-05: Form inputs stack vertically on mobile, expand horizontally on desktop
- RESP-06: Modal is full-screen on mobile (< 640px), centered card on desktop
- RESP-07: Touch-friendly tap targets — all interactive elements are at least 44x44px on mobile

## Current State (Post Phase 15)

### Layout (App.jsx)
- Header: `p-5 flex items-center justify-between` — no responsive stacking
- Nav: `flex gap-1 px-5 mb-4` using NavTab — no mobile variant
- Main: `px-5` — no responsive padding
- No responsive breakpoints used anywhere in the codebase

### Navigation
- NavTab component wraps NavLink with `px-4 py-1.5 rounded-t border text-sm`
- 4 tabs: Prices, Watchlist, Portfolio, Alerts
- Always horizontal, no mobile bottom bar

### Tables
- PriceTable: `max-w-4xl` on Table, no overflow wrapper
- WatchlistPage: `max-w-4xl` on Table, no overflow wrapper
- PortfolioTable: Already has `overflow-x-auto` wrapper div
- All tables use Table/Th/Td primitives from phase 15

### Forms
- AddHoldingForm: `flex flex-wrap items-end gap-2` with fixed-width inputs (w-24, w-28, w-32, w-36)
- AddAlertForm: Same pattern with w-24, w-36
- WatchlistPage form: Same pattern with w-24
- Forms do wrap via flex-wrap but don't stack properly (items-end misaligns labels when wrapping)

### Modal
- Modal primitive: `max-w-xl w-full mx-4` — reasonable on mobile but not full-screen
- CoinModal: `grid grid-cols-2 gap-3` for info — does not stack on mobile

### Touch Targets
- Button sizes: xs=`px-1 py-0.5`, sm=`px-2.5 py-0.5`, md=`px-4 py-1.5`
- sm and xs are well below 44x44px minimum
- NavTab: `px-4 py-1.5` — below 44px height

## Tech Stack
- Tailwind CSS v4 with @theme variables (no tailwind.config.js)
- Default breakpoints: sm=640px, md=768px, lg=1024px
- React Router v7 for navigation
- Vite + React

## Decisions
- Use md (768px) as mobile/desktop breakpoint for navigation (matches RESP-01 spec)
- Use sm (640px) as mobile/desktop breakpoint for modal full-screen (matches RESP-06 spec)
- Bottom nav uses fixed positioning at viewport bottom
- Add padding-bottom to main content when bottom nav is visible to prevent content being hidden behind it
- Keep NavTab component unchanged — create new BottomNav component for mobile
- Form inputs use `w-full` on mobile, fixed width on desktop via responsive classes
