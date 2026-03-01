"""Unit tests for the Bitvavo API client using mocked HTTP responses."""

import pytest
from pytest_httpx import HTTPXMock

from crypto_price_tracker.api import BitvavoClient
from crypto_price_tracker.models import CoinData

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

DUMMY_TICKER_FIELDS = {
    "bid": "100",
    "bidSize": "1",
    "ask": "101",
    "askSize": "1",
    "timestamp": 1772321424236,
    "startTimestamp": 1772235024236,
    "openTimestamp": 1772235040777,
    "closeTimestamp": 1772321422338,
}


def make_ticker(market: str, last: str, open_: str, volume: str, volume_quote: str) -> dict:
    return {
        "market": market,
        "last": last,
        "open": open_,
        "volume": volume,
        "volumeQuote": volume_quote,
        **DUMMY_TICKER_FIELDS,
    }


def make_assets(*symbols_names: tuple[str, str]) -> list[dict]:
    return [{"symbol": s, "name": n} for s, n in symbols_names]


BITVAVO_TICKER_URL = "https://api.bitvavo.com/v2/ticker/24h"
BITVAVO_ASSETS_URL = "https://api.bitvavo.com/v2/assets"


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_get_top_coins_returns_sorted_by_volume(httpx_mock: HTTPXMock) -> None:
    """Results should be ordered by volumeQuote (EUR volume) descending."""
    ticker = [
        make_ticker("AAA-EUR", last="100", open_="90", volume="1000", volume_quote="50000"),
        make_ticker("BBB-EUR", last="200", open_="210", volume="500", volume_quote="100000"),
        make_ticker("CCC-EUR", last="50", open_="50", volume="2000", volume_quote="75000"),
    ]
    assets = make_assets(("AAA", "AlphaCoin"), ("BBB", "BetaCoin"), ("CCC", "GammaCoin"))

    httpx_mock.add_response(url=BITVAVO_TICKER_URL, json=ticker)
    httpx_mock.add_response(url=BITVAVO_ASSETS_URL, json=assets)

    with BitvavoClient(top_n=3) as client:
        results = client.get_top_coins()

    assert len(results) == 3
    assert results[0].symbol == "BBB"
    assert results[0].volume_eur == 100_000.0
    assert results[1].symbol == "CCC"
    assert results[1].volume_eur == 75_000.0
    assert results[2].symbol == "AAA"
    assert results[2].volume_eur == 50_000.0


def test_get_top_coins_filters_eur_only(httpx_mock: HTTPXMock) -> None:
    """Non-EUR pairs must be excluded from results."""
    ticker = [
        make_ticker("BTC-EUR", last="50000", open_="49000", volume="10", volume_quote="500000"),
        make_ticker("BTC-USDT", last="54000", open_="53000", volume="5", volume_quote="270000"),
        make_ticker("ETH-BTC", last="0.05", open_="0.049", volume="100", volume_quote="2.5"),
    ]
    assets = make_assets(("BTC", "Bitcoin"), ("ETH", "Ethereum"))

    httpx_mock.add_response(url=BITVAVO_TICKER_URL, json=ticker)
    httpx_mock.add_response(url=BITVAVO_ASSETS_URL, json=assets)

    with BitvavoClient(top_n=10) as client:
        results = client.get_top_coins()

    symbols = [c.symbol for c in results]
    assert "BTC" in symbols
    # USDT and BTC pairs should not appear
    assert len(results) == 1  # only BTC-EUR qualifies


def test_get_top_coins_computes_change_percentage(httpx_mock: HTTPXMock) -> None:
    """24h change percentage must be computed correctly from open/last prices."""
    ticker = [
        make_ticker("UP-EUR", last="110", open_="100", volume="500", volume_quote="55000"),
        make_ticker("DN-EUR", last="190", open_="200", volume="300", volume_quote="57000"),
    ]
    assets = make_assets(("UP", "UpCoin"), ("DN", "DownCoin"))

    httpx_mock.add_response(url=BITVAVO_TICKER_URL, json=ticker)
    httpx_mock.add_response(url=BITVAVO_ASSETS_URL, json=assets)

    with BitvavoClient(top_n=10) as client:
        results = client.get_top_coins()

    by_symbol = {c.symbol: c for c in results}
    assert by_symbol["UP"].change_24h == pytest.approx(10.0, abs=0.01)
    assert by_symbol["DN"].change_24h == pytest.approx(-5.0, abs=0.01)


def test_get_top_coins_respects_top_n(httpx_mock: HTTPXMock) -> None:
    """Only top_n results should be returned, and they should be the highest-volume ones."""
    ticker = [
        make_ticker("A-EUR", last="1", open_="1", volume="10", volume_quote="10000"),
        make_ticker("B-EUR", last="2", open_="2", volume="20", volume_quote="50000"),
        make_ticker("C-EUR", last="3", open_="3", volume="30", volume_quote="30000"),
        make_ticker("D-EUR", last="4", open_="4", volume="40", volume_quote="80000"),
        make_ticker("E-EUR", last="5", open_="5", volume="50", volume_quote="20000"),
    ]
    assets = make_assets(("A", "ACoin"), ("B", "BCoin"), ("C", "CCoin"), ("D", "DCoin"), ("E", "ECoin"))

    httpx_mock.add_response(url=BITVAVO_TICKER_URL, json=ticker)
    httpx_mock.add_response(url=BITVAVO_ASSETS_URL, json=assets)

    with BitvavoClient(top_n=2) as client:
        results = client.get_top_coins()

    assert len(results) == 2
    # D (80k) and B (50k) should be the top 2
    assert results[0].symbol == "D"
    assert results[1].symbol == "B"


def test_get_top_coins_skips_zero_open(httpx_mock: HTTPXMock) -> None:
    """Entries with open price of '0' must be excluded to avoid ZeroDivisionError."""
    ticker = [
        make_ticker("GOOD-EUR", last="100", open_="90", volume="500", volume_quote="50000"),
        make_ticker("BAD-EUR", last="100", open_="0", volume="1000", volume_quote="100000"),
    ]
    assets = make_assets(("GOOD", "GoodCoin"), ("BAD", "BadCoin"))

    httpx_mock.add_response(url=BITVAVO_TICKER_URL, json=ticker)
    httpx_mock.add_response(url=BITVAVO_ASSETS_URL, json=assets)

    with BitvavoClient(top_n=10) as client:
        results = client.get_top_coins()

    symbols = [c.symbol for c in results]
    assert "BAD" not in symbols
    assert "GOOD" in symbols
    assert len(results) == 1
