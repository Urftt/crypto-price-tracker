"""Unit tests for the web API endpoints using FastAPI TestClient.

All tests mock ``get_top_coins_with_fallback`` so no real HTTP calls are made.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest
from starlette.testclient import TestClient

import httpx

from crypto_price_tracker.models import Candle, CoinData
from crypto_price_tracker.web import create_app


@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)


@pytest.fixture
def portfolio_db(tmp_path):
    """Redirect portfolio DB to a temporary file for test isolation."""
    db_path = tmp_path / "test.db"
    from crypto_price_tracker import portfolio_db
    original = portfolio_db._get_default_db_path
    portfolio_db._get_default_db_path = lambda: db_path
    yield db_path
    portfolio_db._get_default_db_path = original


@pytest.fixture
def mock_coins():
    return [
        CoinData(
            symbol="BTC",
            name="Bitcoin",
            price=56754.0,
            change_24h=1.67,
            volume=2186.73,
            volume_eur=120339407.0,
        ),
        CoinData(
            symbol="ETH",
            name="Ethereum",
            price=2345.50,
            change_24h=-3.21,
            volume=45000.0,
            volume_eur=95000000.0,
        ),
        CoinData(
            symbol="XRP",
            name="Ripple",
            price=0.52,
            change_24h=0.0,
            volume=1000000.0,
            volume_eur=520000.0,
        ),
    ]


def test_api_prices_returns_json_list(client, portfolio_db, mock_coins):
    """GET /api/prices returns a JSON dict with coins, triggered_alerts, and exchange."""
    with patch("crypto_price_tracker.web.get_top_coins_with_fallback", return_value=(mock_coins, "Bitvavo")):
        response = client.get("/api/prices")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "coins" in data
    assert "triggered_alerts" in data
    assert "exchange" in data
    assert data["exchange"] == "Bitvavo"
    assert len(data["coins"]) == 3

    first = data["coins"][0]
    assert set(["symbol", "name", "price", "change_24h", "volume", "volume_eur"]).issubset(first.keys())
    assert first["symbol"] == "BTC"


def test_api_prices_respects_top_param(client, portfolio_db, mock_coins):
    """GET /api/prices?top=2 calls get_top_coins_with_fallback with top_n=2."""
    with patch("crypto_price_tracker.web.get_top_coins_with_fallback", return_value=(mock_coins, "Bitvavo")) as mock_fn:
        response = client.get("/api/prices?top=2")

    assert response.status_code == 200
    mock_fn.assert_called_once_with(exchange="bitvavo", top_n=2)


def test_api_coin_returns_single_coin(client, mock_coins):
    """GET /api/coin/BTC returns JSON for Bitcoin with correct fields."""
    with patch("crypto_price_tracker.web.get_top_coins_with_fallback", return_value=(mock_coins, "Bitvavo")):
        response = client.get("/api/coin/BTC")

    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "BTC"
    assert data["name"] == "Bitcoin"


def test_api_coin_case_insensitive(client, mock_coins):
    """GET /api/coin/btc (lowercase) resolves to the BTC coin."""
    with patch("crypto_price_tracker.web.get_top_coins_with_fallback", return_value=(mock_coins, "Bitvavo")):
        response = client.get("/api/coin/btc")

    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "BTC"


def test_api_coin_not_found_returns_404(client, mock_coins):
    """GET /api/coin/DOESNOTEXIST returns HTTP 404."""
    with patch("crypto_price_tracker.web.get_top_coins_with_fallback", return_value=(mock_coins, "Bitvavo")):
        response = client.get("/api/coin/DOESNOTEXIST")

    assert response.status_code == 404


def test_index_returns_response(client):
    """GET / returns HTTP 200 (either index.html or JSON fallback)."""
    response = client.get("/")
    assert response.status_code == 200


def test_index_serves_react_spa(client):
    """GET / returns 200 with text/html containing the React SPA root element."""
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")

    body = response.text
    assert '<div id="root">' in body
    assert "Crypto Prices" in body


def test_api_coin_detail_fields_complete(client, mock_coins):
    """GET /api/coin/BTC returns JSON with all CoinData fields plus exchange."""
    with patch("crypto_price_tracker.web.get_top_coins_with_fallback", return_value=(mock_coins, "Bitvavo")):
        response = client.get("/api/coin/BTC")

    assert response.status_code == 200
    data = response.json()

    assert data["symbol"] == "BTC"
    assert data["name"] == "Bitcoin"
    assert data["price"] == 56754.0
    assert data["change_24h"] == 1.67
    assert data["volume"] == 2186.73
    assert data["volume_eur"] == 120339407.0
    assert data["exchange"] == "Bitvavo"


# ---- Portfolio API tests ----


def test_api_portfolio_get_empty(client, portfolio_db, mock_coins):
    """GET /api/portfolio with empty DB returns empty rows and zero totals."""
    with patch("crypto_price_tracker.web.get_top_coins_with_fallback", return_value=(mock_coins, "Bitvavo")):
        response = client.get("/api/portfolio")

    assert response.status_code == 200
    data = response.json()
    assert data["rows"] == []
    assert data["total_value"] == 0
    assert data["total_pnl_eur"] == 0


def test_api_portfolio_add_holding(client, portfolio_db):
    """POST /api/portfolio creates a holding and returns its ID."""
    response = client.post("/api/portfolio", json={
        "symbol": "BTC",
        "amount": 0.5,
        "buy_price": 45000.0,
        "buy_date": "2026-01-15",
    })

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["status"] == "created"


def test_api_portfolio_add_then_get(client, portfolio_db, mock_coins):
    """POST then GET /api/portfolio returns aggregated rows with the new holding."""
    client.post("/api/portfolio", json={
        "symbol": "BTC",
        "amount": 0.5,
        "buy_price": 45000.0,
        "buy_date": "2026-01-15",
    })

    with patch("crypto_price_tracker.web.get_top_coins_with_fallback", return_value=(mock_coins, "Bitvavo")):
        response = client.get("/api/portfolio")

    assert response.status_code == 200
    data = response.json()
    assert len(data["rows"]) == 1
    assert data["rows"][0]["symbol"] == "BTC"


def test_api_portfolio_delete_holding(client, portfolio_db):
    """POST then DELETE /api/portfolio/{id} removes the holding."""
    resp = client.post("/api/portfolio", json={
        "symbol": "BTC",
        "amount": 0.5,
        "buy_price": 45000.0,
    })
    holding_id = resp.json()["id"]

    response = client.delete(f"/api/portfolio/{holding_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "deleted"


def test_api_portfolio_delete_not_found(client, portfolio_db):
    """DELETE /api/portfolio/999 returns 404 when holding does not exist."""
    response = client.delete("/api/portfolio/999")
    assert response.status_code == 404


def test_api_portfolio_update_holding(client, portfolio_db):
    """POST then PUT /api/portfolio/{id} updates the holding fields."""
    resp = client.post("/api/portfolio", json={
        "symbol": "ETH",
        "amount": 2.0,
        "buy_price": 2000.0,
    })
    holding_id = resp.json()["id"]

    response = client.put(f"/api/portfolio/{holding_id}", json={"amount": 3.0})
    assert response.status_code == 200
    assert response.json()["status"] == "updated"


def test_api_portfolio_lots(client, portfolio_db):
    """POST BTC then GET /api/portfolio/lots/BTC returns one lot."""
    client.post("/api/portfolio", json={
        "symbol": "BTC",
        "amount": 0.5,
        "buy_price": 45000.0,
        "buy_date": "2026-01-15",
    })

    response = client.get("/api/portfolio/lots/BTC")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["symbol"] == "BTC"


def test_api_portfolio_add_validation(client, portfolio_db):
    """POST /api/portfolio with negative amount returns 422."""
    response = client.post("/api/portfolio", json={
        "symbol": "BTC",
        "amount": -1,
        "buy_price": 45000.0,
    })
    assert response.status_code == 422


def test_index_spa_catch_all(client):
    """GET /portfolio returns the React SPA (catch-all route for client-side routing)."""
    response = client.get("/portfolio")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert '<div id="root">' in response.text


# ---- Alert API tests ----


def test_api_prices_returns_new_format(client, portfolio_db, mock_coins):
    """GET /api/prices returns dict with coins, triggered_alerts, and exchange keys."""
    with patch("crypto_price_tracker.web.get_top_coins_with_fallback", return_value=(mock_coins, "Bitvavo")):
        response = client.get("/api/prices")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "coins" in data
    assert "triggered_alerts" in data
    assert "exchange" in data
    assert isinstance(data["coins"], list)
    assert len(data["coins"]) == 3
    assert isinstance(data["triggered_alerts"], list)


def test_api_prices_triggers_alerts(client, portfolio_db, mock_coins):
    """GET /api/prices with active alert triggers and returns it."""
    from crypto_price_tracker.alerts_db import add_alert
    # BTC mock price is 56754.0, alert target is 50000.0 above — should trigger
    add_alert("BTC", 50000.0, "above", db_path=portfolio_db)

    with patch("crypto_price_tracker.web.get_top_coins_with_fallback", return_value=(mock_coins, "Bitvavo")):
        response = client.get("/api/prices")

    data = response.json()
    assert len(data["triggered_alerts"]) == 1
    assert data["triggered_alerts"][0]["symbol"] == "BTC"


def test_api_alerts_get_empty(client, portfolio_db):
    """GET /api/alerts returns empty list when no alerts exist."""
    response = client.get("/api/alerts")
    assert response.status_code == 200
    assert response.json() == []


def test_api_alerts_add(client, portfolio_db):
    """POST /api/alerts creates an alert and returns its ID."""
    response = client.post("/api/alerts", json={
        "symbol": "BTC",
        "target_price": 100000,
        "direction": "above",
    })
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["status"] == "created"


def test_api_alerts_add_then_get(client, portfolio_db):
    """POST an alert then GET /api/alerts returns it."""
    client.post("/api/alerts", json={
        "symbol": "BTC",
        "target_price": 100000,
        "direction": "above",
    })

    response = client.get("/api/alerts")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["symbol"] == "BTC"


def test_api_alerts_delete(client, portfolio_db):
    """POST then DELETE /api/alerts/{id} removes the alert."""
    resp = client.post("/api/alerts", json={
        "symbol": "BTC",
        "target_price": 100000,
        "direction": "above",
    })
    alert_id = resp.json()["id"]

    response = client.delete(f"/api/alerts/{alert_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "deleted"


def test_api_alerts_delete_not_found(client, portfolio_db):
    """DELETE /api/alerts/999 returns 404."""
    response = client.delete("/api/alerts/999")
    assert response.status_code == 404


def test_api_alerts_clear_triggered(client, portfolio_db):
    """POST alert, mark triggered, DELETE /api/alerts/triggered clears it."""
    from crypto_price_tracker.alerts_db import mark_triggered

    resp = client.post("/api/alerts", json={
        "symbol": "BTC",
        "target_price": 100000,
        "direction": "above",
    })
    alert_id = resp.json()["id"]
    mark_triggered(alert_id, db_path=portfolio_db)

    response = client.delete("/api/alerts/triggered")
    assert response.status_code == 200
    assert response.json()["count"] == 1

    # Verify cleared
    response = client.get("/api/alerts")
    assert response.json() == []


def test_api_alerts_add_validation(client, portfolio_db):
    """POST /api/alerts with negative price returns 422."""
    response = client.post("/api/alerts", json={
        "symbol": "BTC",
        "target_price": -100,
        "direction": "above",
    })
    assert response.status_code == 422


def test_index_spa_alerts_route(client):
    """GET /alerts returns the React SPA (catch-all for client-side routing)."""
    response = client.get("/alerts")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert '<div id="root">' in response.text


# ---- Candle/Chart API tests ----


def make_test_candles() -> list[Candle]:
    """Return a small list of Candle objects for testing."""
    return [
        Candle(timestamp=1000, open=100.0, high=110.0, low=95.0, close=105.0, volume=50.0),
        Candle(timestamp=2000, open=105.0, high=115.0, low=100.0, close=110.0, volume=60.0),
        Candle(timestamp=3000, open=110.0, high=120.0, low=105.0, close=108.0, volume=45.0),
    ]


def test_api_candles_returns_json_list(client):
    """GET /api/candles/BTC returns a JSON list of candle dicts."""
    with patch("crypto_price_tracker.web.get_candles", return_value=make_test_candles()):
        response = client.get("/api/candles/BTC")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3
    first = data[0]
    assert set(["timestamp", "open", "high", "low", "close", "volume"]).issubset(first.keys())
    assert first["timestamp"] == 1000
    assert first["close"] == 105.0


def test_api_candles_case_insensitive(client):
    """GET /api/candles/btc (lowercase) uppercases to BTC-EUR for the API call."""
    with patch("crypto_price_tracker.web.get_candles", return_value=make_test_candles()) as mock_fn:
        response = client.get("/api/candles/btc")

    assert response.status_code == 200
    assert mock_fn.call_args[0][0] == "BTC-EUR"


def test_api_candles_with_interval_param(client):
    """GET /api/candles/BTC?interval=1d&limit=30 passes params through."""
    with patch("crypto_price_tracker.web.get_candles", return_value=make_test_candles()) as mock_fn:
        response = client.get("/api/candles/BTC?interval=1d&limit=30")

    assert response.status_code == 200
    mock_fn.assert_called_once_with("BTC-EUR", interval="1d", limit=30)


def test_api_candles_invalid_market(client):
    """GET /api/candles/INVALID returns 404 when Bitvavo returns 400."""
    mock_request = httpx.Request("GET", "https://api.bitvavo.com/v2/INVALID-EUR/candles")
    mock_response = httpx.Response(400, request=mock_request)
    with patch("crypto_price_tracker.web.get_candles") as mock_fn:
        mock_fn.side_effect = httpx.HTTPStatusError("Bad Request", request=mock_request, response=mock_response)
        response = client.get("/api/candles/INVALID")

    assert response.status_code == 404
    assert "No candle data" in response.json()["detail"]


def test_api_candles_invalid_interval(client):
    """GET /api/candles/BTC?interval=invalid returns 422 from pattern validation."""
    response = client.get("/api/candles/BTC?interval=invalid")
    assert response.status_code == 422


def test_api_candles_empty_response(client):
    """GET /api/candles/BTC returns empty list when no candles available."""
    with patch("crypto_price_tracker.web.get_candles", return_value=[]):
        response = client.get("/api/candles/BTC")

    assert response.status_code == 200
    assert response.json() == []


def test_index_serves_static_assets(client):
    """GET /assets/* serves Vite-built static files (JS/CSS chunks)."""
    # The SPA catch-all should serve static files that exist in the build output
    response = client.get("/")
    body = response.text
    # Vite build output includes link/script references to /assets/*
    assert "/assets/" in body


# ---- Exchange parameter tests ----


def test_api_prices_with_exchange_param(client, portfolio_db, mock_coins):
    """GET /api/prices?exchange=binance passes exchange to get_top_coins_with_fallback."""
    with patch("crypto_price_tracker.web.get_top_coins_with_fallback", return_value=(mock_coins, "Binance")):
        response = client.get("/api/prices?exchange=binance")

    assert response.status_code == 200
    data = response.json()
    assert data["exchange"] == "Binance"


def test_api_prices_default_exchange(client, portfolio_db, mock_coins):
    """GET /api/prices without exchange param uses default (bitvavo)."""
    with patch("crypto_price_tracker.web.get_top_coins_with_fallback", return_value=(mock_coins, "Bitvavo")) as mock_fn:
        response = client.get("/api/prices")

    assert response.status_code == 200
    mock_fn.assert_called_once()


def test_api_coin_with_exchange_param(client, mock_coins):
    """GET /api/coin/BTC?exchange=binance uses Binance."""
    with patch("crypto_price_tracker.web.get_top_coins_with_fallback", return_value=(mock_coins, "Binance")):
        response = client.get("/api/coin/BTC?exchange=binance")

    assert response.status_code == 200
    data = response.json()
    assert data["exchange"] == "Binance"


def test_api_prices_invalid_exchange_rejected(client):
    """GET /api/prices?exchange=invalid returns 422."""
    response = client.get("/api/prices?exchange=invalid")
    assert response.status_code == 422
