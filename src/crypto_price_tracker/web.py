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

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from crypto_price_tracker.api import get_top_coins
from crypto_price_tracker.models import CoinData  # noqa: F401 – re-exported for type hints

STATIC_DIR = Path(__file__).parent / "static"


def create_app() -> FastAPI:
    """Create and return a configured FastAPI application instance."""
    app = FastAPI(title="Crypto Price Tracker", version="0.1.0")

    @app.get("/api/prices")
    def api_prices(top: int = Query(default=20, ge=1, le=100)):
        """Return the top N coins as a JSON array."""
        coins = get_top_coins(top_n=top)
        return [dataclasses.asdict(c) for c in coins]

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
