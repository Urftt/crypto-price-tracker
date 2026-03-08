"""FastAPI web server for the crypto price tracker dashboard.

Exposes JSON API endpoints that serve cryptocurrency price data from the
Bitvavo API.  The React SPA frontend (built by Vite) is served via a
catch-all route.  Real-time price updates are pushed via SSE.

Endpoints:
    GET /api/prices          -- Top-N coins as JSON (?top=N, default 20)
    GET /api/prices/stream   -- SSE stream pushing prices every 10s
    GET /api/coin/{sym}      -- Single coin detail; 404 if not in top 100
    GET /{path:path}         -- SPA catch-all (static files + index.html)
"""

from __future__ import annotations

import asyncio
import dataclasses
import io
import json
from collections.abc import AsyncIterable
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.sse import EventSourceResponse, ServerSentEvent
from pydantic import BaseModel, Field

from crypto_price_tracker.alerts import check_alerts
from crypto_price_tracker.alerts_db import (
    add_alert as db_add_alert,
    clear_triggered_alerts as db_clear_triggered,
    get_active_alerts as db_get_active_alerts,
    get_all_alerts as db_get_all_alerts,
    mark_triggered as db_mark_triggered,
    remove_alert as db_remove_alert,
)
from crypto_price_tracker.api import get_candles
from crypto_price_tracker.exchange import get_top_coins_with_fallback
from crypto_price_tracker.models import Candle, CoinData  # noqa: F401 – re-exported for type hints
from crypto_price_tracker.portfolio import aggregate_portfolio
from crypto_price_tracker.portfolio_db import (
    add_holding as db_add_holding,
    get_all_holdings as db_get_all_holdings,
    get_holdings_by_symbol as db_get_holdings_by_symbol,
    remove_holding as db_remove_holding,
    update_holding as db_update_holding,
)
from crypto_price_tracker.watchlist_db import (
    add_watchlist_entry as db_add_watchlist,
    get_all_watchlist_entries as db_get_watchlist,
    get_watchlist_symbols as db_get_watchlist_symbols,
    remove_watchlist_entry as db_remove_watchlist,
    update_watchlist_tags as db_update_watchlist_tags,
    VALID_TAGS as WATCHLIST_VALID_TAGS,
)

STATIC_DIR = Path(__file__).parent / "static"


class HoldingCreate(BaseModel):
    """Request body for creating a new holding."""

    symbol: str
    amount: float = Field(gt=0)
    buy_price: float = Field(gt=0)
    buy_date: str | None = None


class HoldingUpdate(BaseModel):
    """Request body for updating an existing holding."""

    amount: float | None = Field(default=None, gt=0)
    buy_price: float | None = Field(default=None, gt=0)
    buy_date: str | None = None


class AlertCreate(BaseModel):
    """Request body for creating a new price alert."""

    symbol: str
    target_price: float = Field(gt=0)
    direction: str = Field(default="above", pattern="^(above|below)$")


class WatchlistAdd(BaseModel):
    """Request body for adding a coin to the watchlist."""

    symbol: str
    tags: list[str] = Field(default_factory=list)


class WatchlistTagUpdate(BaseModel):
    """Request body for updating tags on a watchlist entry."""

    tags: list[str]


def create_app() -> FastAPI:
    """Create and return a configured FastAPI application instance."""
    app = FastAPI(title="Crypto Price Tracker", version="0.1.0")
    app.state.default_exchange = "bitvavo"

    @app.get("/api/prices")
    def api_prices(
        top: int = Query(default=20, ge=1, le=100),
        exchange: str = Query(default=None, pattern="^(bitvavo|binance)$"),
    ):
        """Return top N coins with triggered alerts flagged."""
        effective_exchange = exchange or getattr(app.state, "default_exchange", "bitvavo")
        coins, source = get_top_coins_with_fallback(exchange=effective_exchange, top_n=top)
        active = db_get_active_alerts()
        triggered_alerts = check_alerts(coins, active)
        for alert in triggered_alerts:
            db_mark_triggered(alert.id)
        return {
            "coins": [dataclasses.asdict(c) for c in coins],
            "triggered_alerts": [dataclasses.asdict(a) for a in triggered_alerts],
            "exchange": source,
        }

    @app.get("/api/coin/{symbol}")
    def api_coin(
        symbol: str,
        exchange: str = Query(default=None, pattern="^(bitvavo|binance)$"),
    ):
        """Return detailed data for a single coin; 404 if not found in top 100."""
        symbol = symbol.upper()
        effective_exchange = exchange or getattr(app.state, "default_exchange", "bitvavo")
        coins, source = get_top_coins_with_fallback(exchange=effective_exchange, top_n=100)
        match = next((c for c in coins if c.symbol == symbol), None)
        if match is None:
            raise HTTPException(
                status_code=404,
                detail=f"Coin '{symbol}' not found in top 100 pairs on {source}",
            )
        result = dataclasses.asdict(match)
        result["exchange"] = source
        return result

    # --- Portfolio endpoints ---

    @app.get("/api/portfolio")
    def api_portfolio_list():
        """Return aggregated portfolio with live prices."""
        holdings = db_get_all_holdings()
        prices: dict = {}
        try:
            coins, _ = get_top_coins_with_fallback(top_n=100)
            prices = {c.symbol: c for c in coins}
        except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException):
            pass  # best-effort pricing
        summary = aggregate_portfolio(holdings, prices)
        return {
            "rows": [dataclasses.asdict(r) for r in summary.rows],
            "total_value": summary.total_value,
            "total_cost": summary.total_cost,
            "total_pnl_eur": summary.total_pnl_eur,
            "total_pnl_pct": summary.total_pnl_pct,
        }

    @app.get("/api/portfolio/lots/{symbol}")
    def api_portfolio_lots(symbol: str):
        """Return individual lots for a given coin symbol."""
        lots = db_get_holdings_by_symbol(symbol.upper())
        return [dataclasses.asdict(h) for h in lots]

    @app.post("/api/portfolio", status_code=201)
    def api_portfolio_add(body: HoldingCreate):
        """Add a new holding to the portfolio."""
        try:
            row_id = db_add_holding(body.symbol, body.amount, body.buy_price, body.buy_date)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        return {"id": row_id, "status": "created"}

    @app.put("/api/portfolio/{holding_id}")
    def api_portfolio_update(holding_id: int, body: HoldingUpdate):
        """Update fields of an existing holding."""
        kwargs: dict = {}
        if body.amount is not None:
            kwargs["amount"] = body.amount
        if body.buy_price is not None:
            kwargs["buy_price"] = body.buy_price
        if body.buy_date is not None:
            kwargs["buy_date"] = body.buy_date
        if not kwargs:
            raise HTTPException(status_code=400, detail="No fields to update")
        if not db_update_holding(holding_id, **kwargs):
            raise HTTPException(status_code=404, detail=f"Holding #{holding_id} not found")
        return {"status": "updated"}

    @app.delete("/api/portfolio/{holding_id}")
    def api_portfolio_delete(holding_id: int):
        """Delete a holding by ID."""
        if not db_remove_holding(holding_id):
            raise HTTPException(status_code=404, detail=f"Holding #{holding_id} not found")
        return {"status": "deleted"}

    # --- Alert endpoints ---

    @app.get("/api/alerts")
    def api_alerts():
        """Return all alerts grouped by status."""
        alerts = db_get_all_alerts()
        return [dataclasses.asdict(a) for a in alerts]

    @app.post("/api/alerts", status_code=201)
    def api_alerts_add(body: AlertCreate):
        """Create a new price alert."""
        try:
            alert_id = db_add_alert(body.symbol, body.target_price, body.direction)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        return {"id": alert_id, "status": "created"}

    @app.delete("/api/alerts/triggered")
    def api_alerts_clear_triggered():
        """Remove all triggered alerts."""
        count = db_clear_triggered()
        return {"status": "cleared", "count": count}

    @app.delete("/api/alerts/{alert_id}")
    def api_alerts_delete(alert_id: int):
        """Remove an alert by ID."""
        if not db_remove_alert(alert_id):
            raise HTTPException(status_code=404, detail=f"Alert #{alert_id} not found")
        return {"status": "deleted"}

    # --- Watchlist endpoints ---

    @app.get("/api/watchlist")
    def api_watchlist_list(tag: str | None = Query(default=None)):
        """Return all watchlist entries with live prices, optionally filtered by tag."""
        entries = db_get_watchlist(tag=tag)
        # Fetch live prices (best-effort)
        prices: dict = {}
        try:
            coins, _ = get_top_coins_with_fallback(top_n=100)
            prices = {c.symbol: c for c in coins}
        except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException):
            pass
        result = []
        for entry in entries:
            entry_dict = dataclasses.asdict(entry)
            coin = prices.get(entry.symbol)
            if coin:
                entry_dict["price"] = coin.price
                entry_dict["change_24h"] = coin.change_24h
                entry_dict["volume_eur"] = coin.volume_eur
                entry_dict["name"] = coin.name
            else:
                entry_dict["price"] = None
                entry_dict["change_24h"] = None
                entry_dict["volume_eur"] = None
                entry_dict["name"] = None
            result.append(entry_dict)
        return result

    @app.post("/api/watchlist", status_code=201)
    def api_watchlist_add(body: WatchlistAdd):
        """Add a coin to the watchlist."""
        try:
            row_id = db_add_watchlist(body.symbol, body.tags or None)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            if "UNIQUE constraint" in str(e):
                raise HTTPException(
                    status_code=409,
                    detail=f"{body.symbol.upper()} is already on the watchlist",
                )
            raise
        return {"id": row_id, "status": "created"}

    @app.delete("/api/watchlist/{symbol}")
    def api_watchlist_delete(symbol: str):
        """Remove a coin from the watchlist by symbol."""
        if not db_remove_watchlist(symbol):
            raise HTTPException(
                status_code=404,
                detail=f"{symbol.upper()} not found on watchlist",
            )
        return {"status": "deleted"}

    @app.put("/api/watchlist/{symbol}/tags")
    def api_watchlist_update_tags(symbol: str, body: WatchlistTagUpdate):
        """Replace tags on a watchlist entry."""
        try:
            if not db_update_watchlist_tags(symbol, body.tags):
                raise HTTPException(
                    status_code=404,
                    detail=f"{symbol.upper()} not found on watchlist",
                )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        return {"status": "updated"}

    @app.get("/api/watchlist/tags")
    def api_watchlist_tags():
        """Return the list of valid pre-defined tags."""
        return {"tags": sorted(WATCHLIST_VALID_TAGS)}

    @app.get("/api/watchlist/symbols")
    def api_watchlist_symbols():
        """Return the set of all symbols currently on the watchlist."""
        symbols = db_get_watchlist_symbols()
        return {"symbols": sorted(symbols)}

    # --- Export endpoints ---

    @app.get("/api/export/pdf")
    def api_export_pdf():
        """Generate and return a PDF portfolio report as a download."""
        from datetime import datetime
        from crypto_price_tracker.watchlist_db import get_all_watchlist_entries
        from crypto_price_tracker.alerts_db import get_all_alerts
        from crypto_price_tracker.report import generate_report_html, html_to_pdf

        # Gather data
        holdings = db_get_all_holdings()
        prices: dict = {}
        coins: list = []
        try:
            coins, _ = get_top_coins_with_fallback(top_n=100)
            prices = {c.symbol: c for c in coins}
        except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException):
            pass
        portfolio = aggregate_portfolio(holdings, prices)
        watchlist = get_all_watchlist_entries()
        alerts = get_all_alerts()

        # Generate PDF
        html = generate_report_html(portfolio, coins[:20], watchlist, alerts)
        pdf_bytes = html_to_pdf(html)

        # Return as streaming download
        date_str = datetime.now().strftime("%Y-%m-%d")
        headers = {
            "Content-Disposition": f'attachment; filename="crypto-report-{date_str}.pdf"'
        }
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers=headers,
        )

    # --- Candle/Chart endpoints ---

    @app.get("/api/candles/{symbol}")
    def api_candles(
        symbol: str,
        interval: str = Query(default="4h", pattern="^(1m|5m|15m|30m|1h|2h|4h|6h|8h|12h|1d)$"),
        limit: int = Query(default=42, ge=1, le=1440),
    ):
        """Return OHLCV candle data for a market in chronological order."""
        symbol = symbol.upper()
        market = f"{symbol}-EUR"
        try:
            candles = get_candles(market, interval=interval, limit=limit)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                raise HTTPException(
                    status_code=404,
                    detail=f"No candle data for '{symbol}'",
                )
            raise
        return [dataclasses.asdict(c) for c in candles]

    # --- SSE endpoint ---

    @app.get("/api/prices/stream", response_class=EventSourceResponse)
    async def stream_prices(
        top: int = Query(default=20, ge=1, le=100),
        exchange: str = Query(default=None, pattern="^(bitvavo|binance)$"),
    ) -> AsyncIterable[ServerSentEvent]:
        """Push price updates every 10 seconds via SSE."""
        effective_exchange = exchange or getattr(app.state, "default_exchange", "bitvavo")
        event_id = 0
        while True:
            coins, source = get_top_coins_with_fallback(exchange=effective_exchange, top_n=top)
            active = db_get_active_alerts()
            triggered_alerts = check_alerts(coins, active)
            for alert in triggered_alerts:
                db_mark_triggered(alert.id)
            data = {
                "coins": [dataclasses.asdict(c) for c in coins],
                "triggered_alerts": [dataclasses.asdict(a) for a in triggered_alerts],
                "exchange": source,
            }
            yield ServerSentEvent(
                data=data,
                event="prices",
                id=str(event_id),
                retry=10000,
            )
            event_id += 1
            await asyncio.sleep(10)

    # --- SPA catch-all (must be LAST route) ---

    @app.get("/{path:path}")
    def spa_catch_all(path: str):
        """Serve index.html for all non-API paths (SPA routing)."""
        file_path = STATIC_DIR / path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        index_path = STATIC_DIR / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        return {"message": "Crypto Price Tracker API", "docs": "/docs"}

    return app


# Module-level instance so `uvicorn crypto_price_tracker.web:app` works directly
app = create_app()


def run_server(host: str = "0.0.0.0", port: int = 8000) -> None:
    """Start the uvicorn development server."""
    import uvicorn

    uvicorn.run(app, host=host, port=port)
