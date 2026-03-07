# Phase 9 Context: React Frontend

**Phase Goal:** Replace the static HTML/JS dashboard with a Vite + React + Tailwind app with real-time updates. Keep FastAPI backend.

## Decisions

### 1. Real-time Update Mechanism

| Decision | Choice |
|----------|--------|
| Transport | **SSE (Server-Sent Events)** — server pushes updates via `StreamingResponse` |
| Push cadence | **Fixed interval, every 10 seconds** |
| Push scope | **Prices only** — portfolio and alerts refresh on tab switch (unchanged) |
| Countdown timer | **Keep it** — shows "next update in Xs" like current dashboard |
| Change detection | Not needed — fixed interval push regardless of price changes |

**Rationale:** SSE is simpler than WebSocket (one-directional, auto-reconnect, works through proxies). 10s interval is snappier than current 30s polling. Only prices need real-time updates.

### 2. Navigation Structure

| Decision | Choice |
|----------|--------|
| Routing | **React Router with URL paths** — `/`, `/portfolio`, `/alerts` |
| Nav layout | **Top tabs** (same as current — horizontal Prices / Portfolio / Alerts) |
| Coin detail | **Modal overlay** (keep current pattern) |
| Cross-tab update indicator | **None** — prices update silently, user sees fresh data on tab switch |

**Rationale:** URL-based routing gives deep linking, back/forward support, and bookmarking. Top tabs work well for 3 sections. Modal is quick for coin inspection without losing context.

### 3. Chart Library

| Decision | Choice |
|----------|--------|
| Library | **Recharts** (~200KB, React-native, composable components) |
| Chart type | **Line chart** (closing prices, same as current) |
| Period toggle | **7D / 30D** (same as current) |
| API | Existing `/api/candles/{symbol}` endpoint, no changes needed |

**Rationale:** Recharts is lighter than Plotly (~200KB vs ~3MB), more React-idiomatic with component composition, and covers line/area charts well. Line chart keeps the clean, glanceable feel.

### 4. Theme & Styling

| Decision | Choice |
|----------|--------|
| Approach | **Tailwind utility classes** replicating current GitHub-dark theme |
| Colors | Same palette: `#0d1117` (bg), `#161b22` (cards), `#58a6ff` (accent), `#3fb950` (up), `#f85149` (down) |
| Font | Monospace (same as current) |
| Number formatting | nl-NL locale for EUR (same as current) |

## Code Context

### What gets replaced
- `src/crypto_price_tracker/static/index.html` (814 lines, inline CSS + JS)
- Plotly CDN dependency removed

### What stays unchanged
- `src/crypto_price_tracker/web.py` — FastAPI backend (all endpoints stay)
- All Python backend modules (api.py, models.py, portfolio_db.py, alerts_db.py, etc.)
- `crypto web` CLI subcommand

### What gets added (server-side)
- SSE endpoint on FastAPI (e.g., `/api/prices/stream`) — pushes price JSON every 10s
- Static file serving updated to serve Vite build output

### Frontend features to port (1:1 from current HTML)
1. **Prices tab** — top 20 table with rank, symbol, name, EUR price, 24h %, volume
2. **Auto-refresh** — via SSE now (10s), countdown timer UI stays
3. **Manual refresh button** — triggers immediate fetch
4. **Coin detail modal** — click row → modal with price, change, volume, chart
5. **Recharts line chart** — 7D/30D toggle, same data from `/api/candles/{symbol}`
6. **Portfolio tab** — add holding form, aggregated table, lots toggle, delete, summary footer
7. **Alerts tab** — add alert form (coin dropdown, target, direction), active/triggered sections, remove/clear
8. **Set Alert from modal** — button in coin detail → switches to alerts tab with symbol pre-filled
9. **Toast notifications** — alert trigger toasts (auto-dismiss ~10s)
10. **Color coding** — green/red for 24h change and P&L throughout

### Integration points
- Vite dev server proxies `/api/*` to FastAPI during development
- Vite build output goes to `src/crypto_price_tracker/static/` (replaces index.html)
- FastAPI serves the built React app at `/` (same as current `FileResponse`)

## Deferred Ideas

None raised during discussion.

---
*Created: 2026-03-07 via /gsd:discuss-phase 9*
