"""Exchange abstraction layer for multi-exchange support.

Defines the ExchangeClient protocol and provides concrete implementations
for Bitvavo and Binance exchanges.  Includes a factory function and
automatic fallback logic that silently switches to the other exchange
when the primary is unavailable.

Exports:
    ExchangeClient      -- Protocol for exchange client implementations
    BinanceClient       -- Client for the public Binance REST API
    get_exchange_client  -- Factory returning the right client instance
    get_top_coins_with_fallback -- Fetch with automatic exchange fallback
"""

from __future__ import annotations

import time
from typing import Protocol

import httpx

from crypto_price_tracker.models import CoinData

BINANCE_BASE_URL = "https://api.binance.com/api/v3"

EXCHANGES = {"bitvavo", "binance"}
DEFAULT_EXCHANGE = "bitvavo"


class ExchangeClient(Protocol):
    """Protocol for exchange clients that fetch cryptocurrency prices."""

    @property
    def name(self) -> str:
        """Human-readable exchange name (e.g. 'Bitvavo', 'Binance')."""
        ...

    def get_top_coins(self, top_n: int = 20) -> list[CoinData]:
        """Return the top N coins by volume."""
        ...

    def __enter__(self) -> "ExchangeClient":
        ...

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        ...


class BinanceClient:
    """Client for the public Binance REST API.

    Fetches USDT-denominated prices and converts to EUR using
    Binance's own USDT/EUR market rate. The FX rate is cached
    for 5 minutes to avoid redundant API calls.
    """

    _STABLECOIN_SYMBOLS = frozenset(
        {"USDC", "BUSD", "DAI", "TUSD", "FDUSD", "USDD", "USDP"}
    )

    def __init__(self, top_n: int = 20) -> None:
        self.top_n = top_n
        self._client = httpx.Client(
            timeout=10.0,
            headers={"User-Agent": "crypto-price-tracker/0.1.0"},
        )
        self._fx_rate: float | None = None
        self._fx_rate_time: float = 0.0
        self._FX_CACHE_TTL = 300  # 5 minutes

    @property
    def name(self) -> str:
        return "Binance"

    def __enter__(self) -> "BinanceClient":
        self._client.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._client.__exit__(exc_type, exc_val, exc_tb)

    def _get_usdt_eur_rate(self) -> float:
        """Fetch USDT/EUR conversion rate from Binance, with 5-minute caching."""
        now = time.monotonic()
        if self._fx_rate is not None and (now - self._fx_rate_time) < self._FX_CACHE_TTL:
            return self._fx_rate
        response = self._client.get(
            f"{BINANCE_BASE_URL}/ticker/price",
            params={"symbol": "EURUSDT"},
        )
        response.raise_for_status()
        # EURUSDT gives EUR-per-USDT price -- we need USDT-to-EUR which is 1/EURUSDT
        eur_per_usdt = 1.0 / float(response.json()["price"])
        self._fx_rate = eur_per_usdt
        self._fx_rate_time = now
        return eur_per_usdt

    def _fetch_tickers(self) -> list[dict]:
        """Fetch 24h ticker data for all markets."""
        response = self._client.get(f"{BINANCE_BASE_URL}/ticker/24hr")
        response.raise_for_status()
        return response.json()

    def get_top_coins(self, top_n: int | None = None) -> list[CoinData]:
        """Return top N coins by 24h USDT volume, converted to EUR."""
        if top_n is None:
            top_n = self.top_n
        fx_rate = self._get_usdt_eur_rate()
        tickers = self._fetch_tickers()

        coins: list[CoinData] = []
        for entry in tickers:
            symbol_pair: str = entry.get("symbol", "")

            # Only process USDT pairs
            if not symbol_pair.endswith("USDT"):
                continue

            # Extract base symbol (e.g. "BTC" from "BTCUSDT")
            base_symbol = symbol_pair[:-4]

            # Skip stablecoins
            if base_symbol in self._STABLECOIN_SYMBOLS:
                continue

            raw_last = entry.get("lastPrice", "0") or "0"
            raw_open = entry.get("openPrice", "0") or "0"
            raw_volume = entry.get("volume", "0") or "0"
            raw_quote_volume = entry.get("quoteVolume", "0") or "0"

            if not raw_open or raw_open == "0" or float(raw_open) == 0:
                continue

            last_usdt = float(raw_last)
            open_usdt = float(raw_open)
            volume = float(raw_volume)
            volume_usdt = float(raw_quote_volume)

            # Convert USDT prices to EUR
            price_eur = last_usdt * fx_rate
            volume_eur = volume_usdt * fx_rate

            change_24h = ((last_usdt - open_usdt) / open_usdt) * 100

            coins.append(
                CoinData(
                    symbol=base_symbol,
                    name=base_symbol,  # Binance doesn't expose human names in ticker
                    price=price_eur,
                    change_24h=change_24h,
                    volume=volume,
                    volume_eur=volume_eur,
                )
            )

        coins.sort(key=lambda c: c.volume_eur, reverse=True)
        return coins[:top_n]


def get_exchange_client(exchange: str = DEFAULT_EXCHANGE, top_n: int = 20) -> ExchangeClient:
    """Return an exchange client instance for the given exchange name."""
    from crypto_price_tracker.api import BitvavoClient

    if exchange == "binance":
        return BinanceClient(top_n=top_n)
    return BitvavoClient(top_n=top_n)


def get_top_coins_with_fallback(
    exchange: str = DEFAULT_EXCHANGE,
    top_n: int = 20,
) -> tuple[list[CoinData], str]:
    """Fetch top coins with automatic fallback to the other exchange.

    Returns:
        Tuple of (coins list, exchange name that was actually used).
    """
    primary = exchange
    fallback = "binance" if primary == "bitvavo" else "bitvavo"

    # Try primary
    try:
        with get_exchange_client(primary, top_n=top_n) as client:
            coins = client.get_top_coins(top_n)
            return coins, client.name
    except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException):
        pass

    # Try fallback -- if this also fails, the exception propagates to the caller
    with get_exchange_client(fallback, top_n=top_n) as client:
        coins = client.get_top_coins(top_n)
        return coins, client.name
