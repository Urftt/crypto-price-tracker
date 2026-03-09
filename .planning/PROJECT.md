# Crypto Price Tracker

## What This Is

A full-featured cryptocurrency tracking tool with both CLI and web interfaces. Displays live crypto prices from Bitvavo and Binance APIs, manages portfolios with P&L tracking, supports price alerts, watchlists with tags, historical charts, PDF reports, and works as a Progressive Web App.

## Core Value

Instant, glanceable crypto prices in the terminal — one command, no browser needed.

## Current State

**Active: v2.0 — Slick UI** (started 2026-03-09)

Mobile-first UI redesign: shared component library, responsive layouts, mobile card views, and visual polish. Frontend-only — no backend changes.

**v1.0 delivered** (2026-03-09):
- **CLI**: 10 subcommands — prices, watch, info, chart, portfolio, alert, watchlist, export, summary, web
- **Web**: React SPA with SSE real-time updates, Recharts charts, GitHub-dark theme
- **Data**: SQLite persistence for portfolio holdings, price alerts, and watchlist
- **Exchanges**: Bitvavo + Binance with auto-fallback
- **PWA**: Offline support, install-to-home-screen
- **Export**: PDF reports, CSV/JSON, Telegram/email notifications
- **Tests**: 271 passing | **LOC**: ~34,600 | **Commits**: 96

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

**v2.0 — Slick UI** (4 phases: 15–18)
- Phase 15: UI Component Library (Button, Input, Table, Modal, Badge, NavTab)
- Phase 16: Responsive Layout & Mobile Navigation
- Phase 17: Mobile-Optimized Data Views (card layouts)
- Phase 18: Visual Polish & Animations

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

---
*Last updated: 2026-03-09 — v2.0 milestone started*
