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


def test_api_prices_returns_json_list(client, mock_coins):
    """GET /api/prices returns a JSON array with all expected fields."""
    with patch("crypto_price_tracker.web.get_top_coins", return_value=mock_coins):
        response = client.get("/api/prices")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3

    first = data[0]
    assert set(["symbol", "name", "price", "change_24h", "volume", "volume_eur"]).issubset(first.keys())
    assert first["symbol"] == "BTC"


def test_api_prices_respects_top_param(client, mock_coins):
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
    """GET / response body contains the 30-second auto-refresh logic (WEB-02)."""
    response = client.get("/")

    body = response.text
    assert "setInterval" in body
    assert "30000" in body


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
