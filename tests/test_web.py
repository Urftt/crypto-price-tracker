"""Unit tests for the web API endpoints using FastAPI TestClient.

All tests mock ``get_top_coins`` so no real HTTP calls are made.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest
from starlette.testclient import TestClient

from crypto_price_tracker.models import CoinData
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
    """GET /api/prices returns a JSON dict with coins and triggered_alerts."""
    with patch("crypto_price_tracker.web.get_top_coins", return_value=mock_coins):
        response = client.get("/api/prices")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "coins" in data
    assert "triggered_alerts" in data
    assert len(data["coins"]) == 3

    first = data["coins"][0]
    assert set(["symbol", "name", "price", "change_24h", "volume", "volume_eur"]).issubset(first.keys())
    assert first["symbol"] == "BTC"


def test_api_prices_respects_top_param(client, portfolio_db, mock_coins):
    """GET /api/prices?top=2 calls get_top_coins with top_n=2."""
    with patch("crypto_price_tracker.web.get_top_coins", return_value=mock_coins) as mock_fn:
        response = client.get("/api/prices?top=2")

    assert response.status_code == 200
    mock_fn.assert_called_once_with(top_n=2)


def test_api_coin_returns_single_coin(client, mock_coins):
    """GET /api/coin/BTC returns JSON for Bitcoin with correct fields."""
    with patch("crypto_price_tracker.web.get_top_coins", return_value=mock_coins):
        response = client.get("/api/coin/BTC")

    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "BTC"
    assert data["name"] == "Bitcoin"


def test_api_coin_case_insensitive(client, mock_coins):
    """GET /api/coin/btc (lowercase) resolves to the BTC coin."""
    with patch("crypto_price_tracker.web.get_top_coins", return_value=mock_coins):
        response = client.get("/api/coin/btc")

    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "BTC"


def test_api_coin_not_found_returns_404(client, mock_coins):
    """GET /api/coin/DOESNOTEXIST returns HTTP 404."""
    with patch("crypto_price_tracker.web.get_top_coins", return_value=mock_coins):
        response = client.get("/api/coin/DOESNOTEXIST")

    assert response.status_code == 404


def test_index_returns_response(client):
    """GET / returns HTTP 200 (either index.html or JSON fallback)."""
    response = client.get("/")
    assert response.status_code == 200


def test_index_serves_html_with_table(client):
    """GET / returns 200 with text/html containing the price table structure (WEB-01)."""
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")

    body = response.text
    assert "<table" in body
    assert "<th>#</th>" in body
    assert "<th>Symbol</th>" in body
    assert "<th>Name</th>" in body
    assert "<th>Price (EUR)</th>" in body
    assert "<th>24h %</th>" in body
    assert "<th>Volume (EUR)</th>" in body


def test_index_has_auto_refresh(client):
    """GET / response body contains countdown-based auto-refresh logic (WEB-02)."""
    response = client.get("/")

    body = response.text
    assert "setInterval" in body
    assert "REFRESH_SECONDS" in body
    assert "tick" in body


def test_index_has_countdown_timer(client):
    """GET / response body contains countdown timer element and tick function."""
    response = client.get("/")

    body = response.text
    assert 'id="countdown"' in body
    assert "secondsLeft" in body
    assert "tick" in body


def test_index_has_refresh_button(client):
    """GET / response body contains manual refresh button with handler function."""
    response = client.get("/")

    body = response.text
    assert 'id="refresh-btn"' in body
    assert "refreshNow" in body


def test_index_has_detail_modal(client):
    """GET / response body contains the coin detail fetch URL and modal element (WEB-03)."""
    response = client.get("/")

    body = response.text
    assert "/api/coin/" in body
    assert "modal" in body


def test_index_has_color_coding(client):
    """GET / response body contains green and red color codes for 24h change values."""
    response = client.get("/")

    body = response.text
    assert "#3fb950" in body
    assert "#f85149" in body


def test_api_coin_detail_fields_complete(client, mock_coins):
    """GET /api/coin/BTC returns JSON with all 6 CoinData fields matching mock data."""
    with patch("crypto_price_tracker.web.get_top_coins", return_value=mock_coins):
        response = client.get("/api/coin/BTC")

    assert response.status_code == 200
    data = response.json()

    assert data["symbol"] == "BTC"
    assert data["name"] == "Bitcoin"
    assert data["price"] == 56754.0
    assert data["change_24h"] == 1.67
    assert data["volume"] == 2186.73
    assert data["volume_eur"] == 120339407.0


# ---- Portfolio API tests ----


def test_api_portfolio_get_empty(client, portfolio_db, mock_coins):
    """GET /api/portfolio with empty DB returns empty rows and zero totals."""
    with patch("crypto_price_tracker.web.get_top_coins", return_value=mock_coins):
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

    with patch("crypto_price_tracker.web.get_top_coins", return_value=mock_coins):
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


def test_index_has_portfolio_tab(client):
    """GET / should contain Portfolio tab, tab-portfolio div, and switchTab function."""
    response = client.get("/")
    body = response.text
    assert "Portfolio" in body
    assert "tab-portfolio" in body
    assert "switchTab" in body


# ---- Alert API tests ----


def test_api_prices_returns_new_format(client, portfolio_db, mock_coins):
    """GET /api/prices returns dict with coins and triggered_alerts keys."""
    with patch("crypto_price_tracker.web.get_top_coins", return_value=mock_coins):
        response = client.get("/api/prices")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "coins" in data
    assert "triggered_alerts" in data
    assert isinstance(data["coins"], list)
    assert len(data["coins"]) == 3
    assert isinstance(data["triggered_alerts"], list)


def test_api_prices_triggers_alerts(client, portfolio_db, mock_coins):
    """GET /api/prices with active alert triggers and returns it."""
    from crypto_price_tracker.alerts_db import add_alert
    # BTC mock price is 56754.0, alert target is 50000.0 above — should trigger
    add_alert("BTC", 50000.0, "above", db_path=portfolio_db)

    with patch("crypto_price_tracker.web.get_top_coins", return_value=mock_coins):
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


def test_index_has_alerts_tab(client):
    """GET / should contain Alerts tab elements."""
    response = client.get("/")
    body = response.text
    assert "Alerts" in body
    assert "tab-alerts" in body
    assert "alert-symbol" in body
    assert "toast-container" in body


def test_index_has_set_alert_modal_button(client):
    """GET / should contain Set Alert button in modal."""
    response = client.get("/")
    body = response.text
    assert "setAlertFromModal" in body
    assert "Set Alert" in body
