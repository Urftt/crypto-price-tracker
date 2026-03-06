"""FastAPI web server for the crypto price tracker dashboard.

Exposes JSON API endpoints that serve cryptocurrency price data from the
Bitvavo API.  The frontend (Plan 04-02) consumes these endpoints from the
same origin so no CORS middleware is needed.

Endpoints:
    GET /               -- Serve static index.html or JSON fallback
    GET /api/prices     -- Top-N coins as JSON array (?top=N, default 20)
    GET /api/coin/{sym} -- Single coin detail; 404 if not in top 100
"""

from __future__ import annotations

import dataclasses
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
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
from crypto_price_tracker.api import get_top_coins
from crypto_price_tracker.models import CoinData  # noqa: F401 – re-exported for type hints
from crypto_price_tracker.portfolio import aggregate_portfolio
from crypto_price_tracker.portfolio_db import (
    add_holding as db_add_holding,
    get_all_holdings as db_get_all_holdings,
    get_holdings_by_symbol as db_get_holdings_by_symbol,
    remove_holding as db_remove_holding,
    update_holding as db_update_holding,
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


def create_app() -> FastAPI:
    """Create and return a configured FastAPI application instance."""
    app = FastAPI(title="Crypto Price Tracker", version="0.1.0")

    @app.get("/api/prices")
    def api_prices(top: int = Query(default=20, ge=1, le=100)):
        """Return top N coins with triggered alerts flagged."""
        coins = get_top_coins(top_n=top)
        # Passive alert checking
        active = db_get_active_alerts()
        triggered_alerts = check_alerts(coins, active)
        for alert in triggered_alerts:
            db_mark_triggered(alert.id)
        return {
            "coins": [dataclasses.asdict(c) for c in coins],
            "triggered_alerts": [dataclasses.asdict(a) for a in triggered_alerts],
        }

    @app.get("/api/coin/{symbol}")
    def api_coin(symbol: str):
        """Return detailed data for a single coin; 404 if not found in top 100."""
        symbol = symbol.upper()
        coins = get_top_coins(top_n=100)
        match = next((c for c in coins if c.symbol == symbol), None)
        if match is None:
            raise HTTPException(
                status_code=404,
                detail=f"Coin '{symbol}' not found in top 100 EUR pairs",
            )
        return dataclasses.asdict(match)

    # --- Portfolio endpoints ---

    @app.get("/api/portfolio")
    def api_portfolio_list():
        """Return aggregated portfolio with live prices."""
        holdings = db_get_all_holdings()
        prices: dict = {}
        try:
            coins = get_top_coins(top_n=100)
            prices = {c.symbol: c for c in coins}
        except (httpx.HTTPStatusError, httpx.ConnectError):
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

    @app.get("/")
    def index():
        """Serve the static index.html, or a JSON fallback if not yet built."""
        index_path = STATIC_DIR / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        return {"message": "Crypto Price Tracker API", "docs": "/docs"}

    # Mount static directory for CSS/JS assets once the frontend is built
    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    return app


# Module-level instance so `uvicorn crypto_price_tracker.web:app` works directly
app = create_app()


def run_server(host: str = "0.0.0.0", port: int = 8000) -> None:
    """Start the uvicorn development server."""
    import uvicorn

    uvicorn.run(app, host=host, port=port)
