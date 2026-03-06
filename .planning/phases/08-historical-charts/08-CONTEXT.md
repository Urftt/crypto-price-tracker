# Phase 8: Historical Charts — Context

**Discussed:** 2026-03-06
**Phase goal:** Show 7d/30d price history with ASCII sparklines in CLI (`crypto chart`) and interactive Plotly charts in web dashboard coin modal. Use Bitvavo candles endpoint.

## Locked Decisions

### 1. CLI Chart Output

- **Two modes:**
  - `crypto chart` (no symbol) — compact sparkline table for all top 20 coins, showing rank, symbol, 7d sparkline, and 30d sparkline side by side
  - `crypto chart BTC` (with symbol) — detailed single-coin view with sparkline + stats summary (open, close, high, low, change %)
- **Both timeframes always shown** — 7d and 30d stacked/side-by-side, no `--period` flag needed
- **Sparkline style:** Unicode block characters (▁▂▃▄▅▆▇█) representing closing prices
- **Stats color-coded:** Green for positive change, red for negative — consistent with existing `crypto prices` and `crypto portfolio` styling
- **No inline sparklines** in the `crypto prices` table — charts are a separate `crypto chart` command only

### 2. Web Chart Placement & Interaction

- **In the coin detail modal** — clicking a coin row opens the existing modal, which now includes a Plotly chart below the coin info. No new "Charts" tab.
- **Line chart (closing prices)** — simple, clean line chart. No candlestick/OHLC.
- **Timeframe toggle:** 7D / 30D button group above the chart. Default to 7D.
- **Plotly loaded from CDN** — `<script src="...plotly.min.js">` in `index.html`. Keeps the file small.

### 3. Candle Granularity

- **7-day:** 4-hour candles → ~42 data points (good detail without clutter)
- **30-day:** 1-day candles → 30 data points (one per day)
- **Bitvavo endpoint:** `GET /{market}/candles?interval=4h&limit=42` and `interval=1d&limit=30`
- **Response format:** `[timestamp, open, high, low, close, volume]` arrays, returned newest-first (must reverse for chronological order)

### 4. Multi-Coin Performance

- **Sequential fetching** for `crypto chart` (all top 20) — one candle request per coin, one at a time
- **Progress indicator** — show "Fetching chart data..." or similar while loading (Rich spinner or simple print)
- **~2-3 seconds total** — acceptable for a one-shot CLI command
- No caching, no parallel requests — keep it simple

## Claude's Discretion

- Sparkline rendering algorithm (mapping close prices to 8 unicode block levels)
- Exact Rich table layout for the sparkline overview table
- Plotly chart configuration (colors, hover tooltips, axis formatting, responsive sizing)
- New `candles` method on `BitvavoClient` or standalone function
- API endpoint design for candle data (`/api/candles/{symbol}?interval=4h&limit=42`)
- Error handling for coins with insufficient candle data
- Progress indicator implementation (Rich spinner, print, or status)

## Code Context

### Existing Patterns to Follow
- **API client:** `BitvavoClient` with context manager in `api.py`, httpx with 10s timeout
- **CLI subcommands:** argparse with subparsers in `cli.py`, dispatch via if/elif
- **Web endpoints:** FastAPI `create_app()` factory in `web.py`, `dataclasses.asdict()` for JSON
- **Frontend:** Single self-contained `index.html` with inline CSS/JS, existing coin detail modal
- **Display:** Rich library for terminal tables/panels, console injection for testability
- **Data models:** `@dataclass(slots=True)` in `models.py`

### Bitvavo Candles Endpoint (confirmed working)
- URL: `GET https://api.bitvavo.com/v2/{market}/candles`
- Params: `interval` (1m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d), `limit` (number of candles)
- Response: array of `[timestamp_ms, open, high, low, close, volume]` — all values are strings except timestamp
- Returns newest first — reverse for chronological sparkline rendering
- Public endpoint, no auth required

### Key Files to Modify
- `src/crypto_price_tracker/api.py` — add candle-fetching method to `BitvavoClient`
- `src/crypto_price_tracker/models.py` — add `Candle` dataclass
- `src/crypto_price_tracker/display.py` — add sparkline rendering functions
- `src/crypto_price_tracker/cli.py` — add `chart` subcommand
- `src/crypto_price_tracker/web.py` — add candle data API endpoint
- `src/crypto_price_tracker/static/index.html` — add Plotly chart to coin detail modal

### Integration Points
- `crypto chart` calls `get_top_coins()` for the coin list, then fetches candles per coin
- `crypto chart BTC` fetches candles for one coin only
- Web modal already opens on coin row click — extend it with a chart section that fetches `/api/candles/{symbol}`
- Plotly CDN script tag added to `index.html` `<head>`

## Deferred Ideas

None captured during discussion.
