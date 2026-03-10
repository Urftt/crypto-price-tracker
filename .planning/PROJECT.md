# Crypto Price Tracker

## What This Is

A full-featured cryptocurrency tracking tool with both CLI and web interfaces. Displays live crypto prices from Bitvavo and Binance APIs, manages portfolios with P&L tracking, supports price alerts, watchlists with tags, historical charts, PDF reports, and works as a Progressive Web App.

## Core Value

Instant, glanceable crypto prices in the terminal — one command, no browser needed.

## Current State

**v2.0 shipped** (2026-03-10):
- Everything in v1.0, plus:
- **UI Components**: Shared Button, Input, Table, Modal, Badge, NavTab primitives
- **Responsive**: Mobile bottom nav, responsive forms, full-screen modal, 44px touch targets
- **Mobile Views**: Card layouts for all tables on mobile, loading skeletons, empty states
- **Animations**: Page transitions, modal/toast animations, price flash, button press feedback
- **Tests**: 332 passing (61 frontend + 271 backend) | **Commits**: 117

<details>
<summary>v1.0 (2026-03-09)</summary>

- **CLI**: 10 subcommands — prices, watch, info, chart, portfolio, alert, watchlist, export, summary, web
- **Web**: React SPA with SSE real-time updates, Recharts charts, GitHub-dark theme
- **Data**: SQLite persistence for portfolio holdings, price alerts, and watchlist
- **Exchanges**: Bitvavo + Binance with auto-fallback
- **PWA**: Offline support, install-to-home-screen
- **Export**: PDF reports, CSV/JSON, Telegram/email notifications
- **Tests**: 271 passing | **LOC**: ~34,600 | **Commits**: 96
</details>

## Tech Stack

- **Runtime**: Python 3.12+ with uv
- **Backend**: FastAPI + uvicorn
- **Frontend**: Vite + React + Tailwind CSS + Recharts
- **Storage**: SQLite (WAL mode, XDG_DATA_HOME)
- **APIs**: Bitvavo (primary), Binance (secondary)
- **Export**: xhtml2pdf for PDF generation
- **PWA**: vite-plugin-pwa + Workbox

## Context

- Bitvavo is a European crypto exchange with a public REST API for market data
- Binance used as secondary source with USDT→EUR conversion
- All prices in EUR via native trading pairs
- No authentication required — public data only

## Next Milestone

Not yet defined. Run `/gsd:new-milestone` to start planning the next version.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Bitvavo API over CoinGecko/CMC | EUR-native exchange, no API key | Validated |
| Dynamic top N from API | Accurate ranking, stays current | Validated |
| Configurable refresh interval | 30s default, --interval override | Validated |
| Public endpoints only | No auth complexity | Validated |
| uv for project management | Fast dependency resolution | Validated |
| SQLite for persistence | No external DB server needed | Validated |
| React + Vite SPA | Modern frontend, SSE for real-time | Validated |
| Binance as fallback exchange | USDT→EUR conversion, broader coverage | Validated |
| xhtml2pdf for reports | Pure Python, no system dependencies | Validated |
| vite-plugin-pwa | Workbox integration, auto-update | Validated |
| Shared UI primitives | Eliminated style duplication, improved consistency | Validated |
| CSS-only animations | No third-party library, Tailwind v4 theme vars | Validated |
| CSS card/table toggle | sm:hidden/hidden sm:block, no JS media queries | Validated |

---
*Last updated: 2026-03-10 — v2.0 milestone completed*
