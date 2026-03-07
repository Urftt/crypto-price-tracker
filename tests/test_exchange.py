"""Unit tests for the exchange abstraction layer."""

from __future__ import annotations

import time
from contextlib import contextmanager
from unittest.mock import MagicMock, patch

import httpx
import pytest
from pytest_httpx import HTTPXMock

from crypto_price_tracker.exchange import (
    BinanceClient,
    get_exchange_client,
    get_top_coins_with_fallback,
)
from crypto_price_tracker.models import CoinData

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

BINANCE_TICKER_URL = "https://api.binance.com/api/v3/ticker/24hr"
BINANCE_FX_URL = "https://api.binance.com/api/v3/ticker/price?symbol=EURUSDT"

# EURUSDT = 1.10 means 1 EUR = 1.10 USDT, so 1 USDT = 1/1.10 ~ 0.909 EUR
FX_RESPONSE = {"symbol": "EURUSDT", "price": "1.10"}
FX_RATE = 1.0 / 1.10  # ~ 0.90909


def make_binance_ticker(
    symbol: str,
    last: str,
    open_: str,
    volume: str,
    quote_volume: str,
) -> dict:
    """Build a minimal Binance 24hr ticker entry."""
    return {
        "symbol": symbol,
        "lastPrice": last,
        "openPrice": open_,
        "volume": volume,
        "quoteVolume": quote_volume,
        "priceChange": "0",
        "priceChangePercent": "0",
        "weightedAvgPrice": "0",
        "prevClosePrice": "0",
        "bidPrice": "0",
        "askPrice": "0",
    }


# ---------------------------------------------------------------------------
# BinanceClient tests
# ---------------------------------------------------------------------------


def test_binance_name_property() -> None:
    """BinanceClient.name returns 'Binance'."""
    client = BinanceClient()
    assert client.name == "Binance"


def test_binance_get_top_coins_converts_to_eur(httpx_mock: HTTPXMock) -> None:
    """BinanceClient converts USDT prices to EUR using the FX rate."""
    httpx_mock.add_response(url=BINANCE_FX_URL, json=FX_RESPONSE)
    httpx_mock.add_response(
        url=BINANCE_TICKER_URL,
        json=[
            make_binance_ticker("BTCUSDT", last="55000", open_="50000", volume="100", quote_volume="5500000"),
        ],
    )

    with BinanceClient(top_n=10) as client:
        coins = client.get_top_coins()

    assert len(coins) == 1
    assert coins[0].symbol == "BTC"
    assert coins[0].price == pytest.approx(55000 * FX_RATE, rel=1e-4)
    assert coins[0].volume_eur == pytest.approx(5500000 * FX_RATE, rel=1e-4)


def test_binance_filters_usdt_only(httpx_mock: HTTPXMock) -> None:
    """Only USDT pairs are included; EUR and BTC pairs are excluded."""
    httpx_mock.add_response(url=BINANCE_FX_URL, json=FX_RESPONSE)
    httpx_mock.add_response(
        url=BINANCE_TICKER_URL,
        json=[
            make_binance_ticker("BTCUSDT", last="55000", open_="50000", volume="100", quote_volume="5500000"),
            make_binance_ticker("BTCEUR", last="50000", open_="49000", volume="50", quote_volume="2500000"),
            make_binance_ticker("ETHBTC", last="0.05", open_="0.049", volume="200", quote_volume="10"),
        ],
    )

    with BinanceClient(top_n=10) as client:
        coins = client.get_top_coins()

    assert len(coins) == 1
    assert coins[0].symbol == "BTC"


def test_binance_filters_stablecoins(httpx_mock: HTTPXMock) -> None:
    """Stablecoin USDT pairs (USDCUSDT, BUSDUSDT, etc.) are excluded."""
    httpx_mock.add_response(url=BINANCE_FX_URL, json=FX_RESPONSE)
    httpx_mock.add_response(
        url=BINANCE_TICKER_URL,
        json=[
            make_binance_ticker("BTCUSDT", last="55000", open_="50000", volume="100", quote_volume="5500000"),
            make_binance_ticker("USDCUSDT", last="1.00", open_="1.00", volume="1000000", quote_volume="1000000"),
            make_binance_ticker("BUSDUSDT", last="1.00", open_="1.00", volume="500000", quote_volume="500000"),
            make_binance_ticker("DAIUSDT", last="1.00", open_="1.00", volume="200000", quote_volume="200000"),
        ],
    )

    with BinanceClient(top_n=10) as client:
        coins = client.get_top_coins()

    symbols = [c.symbol for c in coins]
    assert "BTC" in symbols
    assert "USDC" not in symbols
    assert "BUSD" not in symbols
    assert "DAI" not in symbols
    assert len(coins) == 1


def test_binance_skips_zero_open(httpx_mock: HTTPXMock) -> None:
    """Entries with openPrice=0 are skipped."""
    httpx_mock.add_response(url=BINANCE_FX_URL, json=FX_RESPONSE)
    httpx_mock.add_response(
        url=BINANCE_TICKER_URL,
        json=[
            make_binance_ticker("BTCUSDT", last="55000", open_="50000", volume="100", quote_volume="5500000"),
            make_binance_ticker("BADUSDT", last="100", open_="0", volume="1000", quote_volume="100000"),
        ],
    )

    with BinanceClient(top_n=10) as client:
        coins = client.get_top_coins()

    assert len(coins) == 1
    assert coins[0].symbol == "BTC"


def test_binance_sorted_by_volume(httpx_mock: HTTPXMock) -> None:
    """Results are sorted by volume_eur descending."""
    httpx_mock.add_response(url=BINANCE_FX_URL, json=FX_RESPONSE)
    httpx_mock.add_response(
        url=BINANCE_TICKER_URL,
        json=[
            make_binance_ticker("AAAUSDT", last="10", open_="10", volume="500", quote_volume="5000"),
            make_binance_ticker("BBBUSDT", last="20", open_="20", volume="300", quote_volume="15000"),
            make_binance_ticker("CCCUSDT", last="5", open_="5", volume="1000", quote_volume="10000"),
        ],
    )

    with BinanceClient(top_n=10) as client:
        coins = client.get_top_coins()

    assert coins[0].symbol == "BBB"
    assert coins[1].symbol == "CCC"
    assert coins[2].symbol == "AAA"


def test_binance_respects_top_n(httpx_mock: HTTPXMock) -> None:
    """Only top_n results are returned."""
    httpx_mock.add_response(url=BINANCE_FX_URL, json=FX_RESPONSE)
    httpx_mock.add_response(
        url=BINANCE_TICKER_URL,
        json=[
            make_binance_ticker("AAAUSDT", last="10", open_="10", volume="500", quote_volume="5000"),
            make_binance_ticker("BBBUSDT", last="20", open_="20", volume="300", quote_volume="15000"),
            make_binance_ticker("CCCUSDT", last="5", open_="5", volume="1000", quote_volume="10000"),
        ],
    )

    with BinanceClient(top_n=2) as client:
        coins = client.get_top_coins()

    assert len(coins) == 2
    assert coins[0].symbol == "BBB"
    assert coins[1].symbol == "CCC"


def test_binance_change_24h_calculation(httpx_mock: HTTPXMock) -> None:
    """24h change percentage is computed correctly from open/last prices."""
    httpx_mock.add_response(url=BINANCE_FX_URL, json=FX_RESPONSE)
    httpx_mock.add_response(
        url=BINANCE_TICKER_URL,
        json=[
            make_binance_ticker("UPUSDT", last="110", open_="100", volume="500", quote_volume="55000"),
            make_binance_ticker("DNUSDT", last="190", open_="200", volume="300", quote_volume="57000"),
        ],
    )

    with BinanceClient(top_n=10) as client:
        coins = client.get_top_coins()

    by_symbol = {c.symbol: c for c in coins}
    assert by_symbol["UP"].change_24h == pytest.approx(10.0, abs=0.01)
    assert by_symbol["DN"].change_24h == pytest.approx(-5.0, abs=0.01)


def test_binance_fx_rate_cached(httpx_mock: HTTPXMock) -> None:
    """FX rate is cached; calling get_top_coins twice only fetches FX once."""
    httpx_mock.add_response(url=BINANCE_FX_URL, json=FX_RESPONSE)
    # Two ticker responses for two calls
    tickers = [make_binance_ticker("BTCUSDT", last="55000", open_="50000", volume="100", quote_volume="5500000")]
    httpx_mock.add_response(url=BINANCE_TICKER_URL, json=tickers)
    httpx_mock.add_response(url=BINANCE_TICKER_URL, json=tickers)

    with BinanceClient(top_n=10) as client:
        client.get_top_coins()
        client.get_top_coins()

    # FX URL should only be called once (cached)
    fx_requests = [r for r in httpx_mock.get_requests() if "ticker/price" in str(r.url)]
    assert len(fx_requests) == 1


def test_binance_fx_cache_expires(httpx_mock: HTTPXMock) -> None:
    """After TTL expires, FX rate is fetched again."""
    httpx_mock.add_response(url=BINANCE_FX_URL, json=FX_RESPONSE)
    httpx_mock.add_response(url=BINANCE_FX_URL, json=FX_RESPONSE)
    tickers = [make_binance_ticker("BTCUSDT", last="55000", open_="50000", volume="100", quote_volume="5500000")]
    httpx_mock.add_response(url=BINANCE_TICKER_URL, json=tickers)
    httpx_mock.add_response(url=BINANCE_TICKER_URL, json=tickers)

    with BinanceClient(top_n=10) as client:
        client.get_top_coins()

        # Simulate time passing beyond TTL
        client._fx_rate_time -= 400  # Push cache time back 400 seconds

        client.get_top_coins()

    # FX URL should be called twice now
    fx_requests = [r for r in httpx_mock.get_requests() if "ticker/price" in str(r.url)]
    assert len(fx_requests) == 2


# ---------------------------------------------------------------------------
# Factory tests
# ---------------------------------------------------------------------------


def test_get_exchange_client_bitvavo() -> None:
    """Factory returns BitvavoClient for 'bitvavo'."""
    from crypto_price_tracker.api import BitvavoClient

    client = get_exchange_client("bitvavo")
    assert isinstance(client, BitvavoClient)
    assert client.name == "Bitvavo"


def test_get_exchange_client_binance() -> None:
    """Factory returns BinanceClient for 'binance'."""
    client = get_exchange_client("binance")
    assert isinstance(client, BinanceClient)
    assert client.name == "Binance"


# ---------------------------------------------------------------------------
# Fallback tests
# ---------------------------------------------------------------------------


def _make_mock_client(name: str, coins: list[CoinData], should_fail: bool = False):
    """Create a mock exchange client for fallback testing."""
    mock = MagicMock()
    mock.name = name
    mock.__enter__ = MagicMock(return_value=mock)
    mock.__exit__ = MagicMock(return_value=False)
    if should_fail:
        mock.get_top_coins.side_effect = httpx.ConnectError("Connection refused")
    else:
        mock.get_top_coins.return_value = coins
    return mock


def test_fallback_returns_primary_on_success() -> None:
    """When primary succeeds, returns primary coins and name."""
    coins = [CoinData("BTC", "Bitcoin", 50000.0, 1.5, 100.0, 5000000.0)]
    primary_client = _make_mock_client("Bitvavo", coins)

    with patch(
        "crypto_price_tracker.exchange.get_exchange_client",
        return_value=primary_client,
    ):
        result_coins, result_name = get_top_coins_with_fallback("bitvavo", top_n=20)

    assert result_name == "Bitvavo"
    assert len(result_coins) == 1
    assert result_coins[0].symbol == "BTC"


def test_fallback_uses_secondary_on_primary_failure() -> None:
    """When primary fails, fallback exchange is used and its name returned."""
    primary_coins: list[CoinData] = []
    fallback_coins = [CoinData("ETH", "Ethereum", 2000.0, -1.0, 50.0, 1000000.0)]

    primary_client = _make_mock_client("Bitvavo", primary_coins, should_fail=True)
    fallback_client = _make_mock_client("Binance", fallback_coins)

    def mock_factory(exchange: str, top_n: int = 20):
        if exchange == "bitvavo":
            return primary_client
        return fallback_client

    with patch(
        "crypto_price_tracker.exchange.get_exchange_client",
        side_effect=mock_factory,
    ):
        result_coins, result_name = get_top_coins_with_fallback("bitvavo", top_n=20)

    assert result_name == "Binance"
    assert len(result_coins) == 1
    assert result_coins[0].symbol == "ETH"


def test_fallback_raises_if_both_fail() -> None:
    """When both exchanges fail, the fallback exception propagates."""
    primary_client = _make_mock_client("Bitvavo", [], should_fail=True)
    fallback_client = _make_mock_client("Binance", [], should_fail=True)

    def mock_factory(exchange: str, top_n: int = 20):
        if exchange == "bitvavo":
            return primary_client
        return fallback_client

    with (
        patch(
            "crypto_price_tracker.exchange.get_exchange_client",
            side_effect=mock_factory,
        ),
        pytest.raises(httpx.ConnectError),
    ):
        get_top_coins_with_fallback("bitvavo", top_n=20)
