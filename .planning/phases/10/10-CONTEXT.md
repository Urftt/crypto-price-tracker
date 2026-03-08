# Phase 10 Context: Multi-Exchange Support

**Phase Goal:** Abstract the exchange layer. Add Binance as second source alongside Bitvavo. Auto-fallback if one is down. CLI flag `--exchange binance`.

## Decisions

### 1. EUR Pricing on Binance

| Decision | Choice |
|----------|--------|
| Price source | **USDT pairs + EUR conversion** — Binance has limited EUR pairs, so fetch USDT prices and convert |
| FX rate source | **Binance USDT-EUR pair** — use Binance's own market rate, keeps everything on one exchange |
| FX rate caching | **Cache for 5 minutes** — forex rates don't move fast enough to matter at this timescale |
| Conversion indicator | **None** — no visual distinction between native EUR and converted prices |
| Chart data | **Always from Bitvavo** — candle/chart data stays on Bitvavo regardless of active price exchange |

**Rationale:** Binance has ~20-30 EUR pairs vs hundreds of USDT pairs. Using USDT pairs with conversion ensures the top 20 list is comparable to Bitvavo's. The Binance USDT-EUR market rate is real-time and avoids adding an external forex dependency. 5-minute cache avoids redundant API calls while keeping conversion accurate enough. Charts stay on Bitvavo for simplicity — chart data is historical context, not real-time pricing.

### 2. Exchange Source Visibility

| Decision | Choice |
|----------|--------|
| Source label | **Always show** — display "via Bitvavo" or "via Binance" regardless of how the exchange was selected |
| Fallback styling | **No extra warning** — the label changes to the fallback exchange name, no special color or icon |
| CLI placement | **Consistent with web** — Claude decides exact placement, matching across surfaces |
| Web placement | **Consistent with CLI** — same approach on both surfaces |

**Rationale:** Users should always know where their price data comes from. A simple label is sufficient — no need for alarm-style warnings when fallback activates since the data is still valid.

### 3. Web Dashboard Exchange Switching

| Decision | Choice |
|----------|--------|
| Server startup | **`crypto web --exchange binance`** sets the default exchange for the server |
| Runtime switching | **Dropdown in global nav bar** — users can override per browser session |
| Scope | **Per-session (browser-local)** — each browser tab picks its own exchange independently |
| API mechanism | **`?exchange=` query param** on price endpoints — SSE stream reconnects on switch |
| Dropdown placement | **Global nav bar** — visible on all pages, affects all price-related data |

**Rationale:** Startup flag sets a sensible default. Runtime dropdown gives flexibility without restarting the server. Per-session scope avoids one user's preference affecting others. Global nav placement makes sense since the exchange source is a cross-cutting concern.

## Code Context

### What gets modified
- `src/crypto_price_tracker/api.py` — extract exchange interface, add BinanceClient alongside BitvavoClient
- `src/crypto_price_tracker/cli.py` — add `--exchange` flag to `prices`, `watch`, `info` subcommands
- `src/crypto_price_tracker/web.py` — accept `?exchange=` param on `/api/prices`, `/api/prices/stream`, `/api/coin/{symbol}`
- `frontend/src/App.jsx` — add exchange dropdown to global nav
- `frontend/src/pages/PricesPage.jsx` — pass exchange param to SSE and API calls

### What stays unchanged
- `src/crypto_price_tracker/models.py` — CoinData is already exchange-agnostic
- `src/crypto_price_tracker/portfolio_db.py`, `alerts_db.py` — no exchange dependency
- `src/crypto_price_tracker/display.py` — rendering is data-driven, exchange-independent
- Chart/candle endpoints — always use Bitvavo

### Key integration points
- `get_top_coins()` and `get_candles()` convenience functions are the seam — all callers use them
- SSE endpoint will need to accept exchange param and reconnect cleanly on switch
- Auto-fallback: if primary exchange fails, silently switch to the other and update the source label

## Deferred Ideas

None raised during discussion.

---
*Created: 2026-03-07 via /gsd:discuss-phase 10*
