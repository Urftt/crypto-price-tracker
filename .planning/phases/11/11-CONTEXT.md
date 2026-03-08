# Phase 11 Context: Watchlist & Tags

**Phase Goal:** Let users tag coins (DeFi, Layer1, Meme) and filter by tag. Persistent watchlist separate from portfolio. CLI: `crypto watchlist add ETH --tag defi`, web: Watchlist tab with tag filter pills.

## Decisions

### 1. CLI Command Structure

| Decision | Choice |
|----------|--------|
| Command name | **`crypto watchlist`** — avoids conflict with existing `crypto watch` (auto-refresh) |
| Subcommands | `crypto watchlist add <SYMBOL> [--tag <TAG>...]`, `crypto watchlist list [--tag <TAG>]`, `crypto watchlist remove <SYMBOL>` |
| Live prices | **Yes** — `crypto watchlist list` fetches current prices and shows same columns as `crypto prices` (price, 24h change, volume) |
| Tag filtering | **Yes** — `crypto watchlist list --tag defi` filters by tag in CLI |
| Prices integration | **`--watchlist` flag** — `crypto prices --watchlist` and `crypto watch --watchlist` filter the main table to show only watched coins |

**Rationale:** `crypto watchlist` follows the same pattern as `crypto portfolio` and `crypto alert` (noun-based subcommand groups). Live prices make the watchlist immediately useful without switching commands. The `--watchlist` flag on `prices`/`watch` lets users see their watched coins in the familiar table format without learning new commands.

### 2. Tag System Design

| Decision | Choice |
|----------|--------|
| Tag source | **Pre-defined set** — ship with 6 built-in tag categories |
| Tag list | **Layer1, Layer2, DeFi, Meme, Exchange, Privacy** |
| Multi-tag | **Yes** — a coin can have multiple tags (e.g., ETH = Layer1 + DeFi) |
| Assignment | **Manual only** — user explicitly assigns tags via `--tag` flag |
| Tag scope | **Watchlist only** — tags are a property of watchlist entries; coin must be on watchlist to be tagged |
| Storage | Same SQLite DB file as portfolio/alerts (established pattern) |

**Rationale:** Pre-defined tags keep the UI clean and avoid tag proliferation. 6 categories cover the major crypto sectors without over-complicating. Multi-tag is essential since most coins span categories. Manual assignment keeps it simple — no external data source needed. Tying tags to watchlist entries avoids a separate tag management system.

### 3. Web UI Integration

| Decision | Choice |
|----------|--------|
| Watchlist location | **New "Watchlist" tab** — 4th tab in nav bar (Prices, Watchlist, Portfolio, Alerts) |
| Tag filter UI | **Clickable tag pills** — colored pills above the watchlist table, click to toggle, multiple active = OR logic |
| Add to watchlist | **Star icon on Prices tab rows** — click star on any coin in the price table to add/remove from watchlist |
| Watchlist table | Same columns as Prices tab + tags column showing colored tag pills per row |
| Tag assignment on web | Tag selection when starring (or editable on Watchlist tab) |

**Rationale:** A dedicated tab gives the watchlist a clear home and separates it from the dynamic top-N ranking on the Prices page. Star icons are the most intuitive UX for bookmarking — users expect it from other financial apps. Tag pills provide visual categorization and one-click filtering without consuming screen space.

## Code Context

### What gets modified
- **New: `src/crypto_price_tracker/watchlist_db.py`** — SQLite CRUD for watchlist entries + tags (same DB file via `portfolio_db._get_default_db_path()`)
- **`src/crypto_price_tracker/models.py`** — add `WatchlistEntry` dataclass
- **`src/crypto_price_tracker/cli.py`** — add `watchlist` subcommand group + `--watchlist` flag on `prices`/`watch`
- **`src/crypto_price_tracker/display.py`** — watchlist table renderer (reuse `render_price_table` pattern with tags column)
- **`src/crypto_price_tracker/web.py`** — REST API endpoints: `/api/watchlist` (GET/POST/DELETE), `/api/watchlist/tags` (GET)
- **`frontend/src/pages/WatchlistPage.jsx`** — new page with tag pills and watchlist table
- **`frontend/src/components/PriceTable.jsx`** — add star icon column
- **`frontend/src/App.jsx`** — add Watchlist tab to nav router

### What stays unchanged
- `src/crypto_price_tracker/exchange.py` — watchlist is display-layer, not exchange-layer
- `src/crypto_price_tracker/portfolio_db.py`, `alerts_db.py` — independent features
- `src/crypto_price_tracker/api.py` — no new external API calls needed
- Chart/candle endpoints — unrelated

### Key integration points
- Watchlist uses same SQLite DB file and connection pattern as portfolio/alerts
- `crypto watchlist list` calls `get_top_coins_with_fallback()` for live prices, then filters to watched symbols
- Star icon on PriceTable needs watchlist state (fetched on page load, toggled via API)
- `--watchlist` flag on `prices`/`watch` filters the `coins` list before rendering
- Tag pills are pre-defined constants (no CRUD for tag definitions themselves)

### DB schema (indicative)
- `watchlist` table: `id`, `symbol` (UNIQUE), `created_at`
- `watchlist_tags` table: `id`, `watchlist_id` (FK), `tag` (CHECK IN pre-defined list)
- Or single table with comma-separated tags (simpler, since tags are pre-defined and few)

## Deferred Ideas

None raised during discussion.

---
*Created: 2026-03-07 via /gsd:discuss-phase 11*
