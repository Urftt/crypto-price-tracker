"""Bitvavo public REST API client.

Fetches live EUR cryptocurrency prices from the Bitvavo exchange using only
public endpoints — no API key or authentication required.

Ranking note: Bitvavo's public API does not provide market cap data. This
client uses `volumeQuote` (24h EUR trading volume) as a market cap proxy.
High-volume coins strongly correlate with high-market-cap coins and represent
the most relevant/liquid assets for a user checking prices.
"""

from __future__ import annotations

import httpx

from crypto_price_tracker.models import Candle, CoinData

BASE_URL = "https://api.bitvavo.com/v2"


class BitvavoClient:
    """Client for the Bitvavo public REST API.

    Retrieves the top N EUR-denominated cryptocurrencies sorted by 24h EUR
    trading volume (volumeQuote), which serves as a market cap proxy because
    Bitvavo's public API does not expose market cap figures.

    Usage:
        with BitvavoClient(top_n=20) as client:
            coins = client.get_top_coins()

    Args:
        top_n: Number of top coins to return (default 20).
    """

    def __init__(self, top_n: int = 20) -> None:
        self.top_n = top_n
        self._client = httpx.Client(
            timeout=10.0,
            headers={"User-Agent": "crypto-price-tracker/0.1.0"},
        )

    @property
    def name(self) -> str:
        return "Bitvavo"

    def __enter__(self) -> "BitvavoClient":
        self._client.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._client.__exit__(exc_type, exc_val, exc_tb)

    def _fetch_assets(self) -> dict[str, str]:
        """Fetch asset metadata and return a symbol-to-name mapping.

        Returns:
            dict mapping ticker symbol to human-readable name,
            e.g. {"BTC": "Bitcoin", "ETH": "Ethereum", ...}

        Raises:
            httpx.HTTPStatusError: on non-2xx HTTP responses.
        """
        response = self._client.get(f"{BASE_URL}/assets")
        response.raise_for_status()
        assets: list[dict] = response.json()
        return {asset["symbol"]: asset["name"] for asset in assets}

    def _fetch_ticker_24h(self) -> list[dict]:
        """Fetch 24h ticker data for all markets.

        Returns:
            Raw JSON list of ticker objects from Bitvavo /ticker/24h.

        Raises:
            httpx.HTTPStatusError: on non-2xx HTTP responses.
        """
        response = self._client.get(f"{BASE_URL}/ticker/24h")
        response.raise_for_status()
        return response.json()

    def get_top_coins(self, top_n: int | None = None) -> list[CoinData]:
        """Return the top N coins by 24h EUR trading volume.

        Fetches ticker data and asset metadata, filters to EUR pairs only,
        computes 24h change percentage, and sorts by volumeQuote descending.

        Returns:
            List of CoinData instances, sorted by volume_eur descending,
            length <= self.top_n.
        """
        ticker_data = self._fetch_ticker_24h()
        assets = self._fetch_assets()

        coins: list[CoinData] = []
        for entry in ticker_data:
            market: str = entry.get("market", "")

            # Only process EUR-denominated pairs
            if not market.endswith("-EUR"):
                continue

            symbol = market.split("-")[0]

            raw_last = entry.get("last", "0") or "0"
            raw_open = entry.get("open", "0") or "0"
            raw_volume = entry.get("volume", "0") or "0"
            raw_volume_quote = entry.get("volumeQuote", "0") or "0"

            # Skip entries with zero or missing open price to avoid ZeroDivisionError
            if not raw_open or raw_open == "0":
                continue

            last = float(raw_last)
            open_price = float(raw_open)
            volume = float(raw_volume)
            volume_eur = float(raw_volume_quote)

            change_24h = ((last - open_price) / open_price) * 100

            name = assets.get(symbol, symbol)

            coins.append(
                CoinData(
                    symbol=symbol,
                    name=name,
                    price=last,
                    change_24h=change_24h,
                    volume=volume,
                    volume_eur=volume_eur,
                )
            )

        # Sort by 24h EUR volume descending — highest volume = most relevant coins
        coins.sort(key=lambda c: c.volume_eur, reverse=True)

        limit = top_n if top_n is not None else self.top_n
        return coins[:limit]

    def get_candles(self, market: str, interval: str = "4h", limit: int = 42) -> list[Candle]:
        """Fetch OHLCV candles for a market, returned in chronological order.

        Args:
            market:   Market pair (e.g. "BTC-EUR").
            interval: Candle interval (e.g. "4h", "1d").
            limit:    Number of candles to return.

        Returns:
            List of Candle instances sorted oldest-first (chronological).

        Raises:
            httpx.HTTPStatusError: on non-2xx HTTP responses (e.g. 400 for invalid market).
        """
        response = self._client.get(
            f"{BASE_URL}/{market}/candles",
            params={"interval": interval, "limit": limit},
        )
        response.raise_for_status()
        raw: list[list] = response.json()
        candles = [
            Candle(
                timestamp=entry[0],
                open=float(entry[1]),
                high=float(entry[2]),
                low=float(entry[3]),
                close=float(entry[4]),
                volume=float(entry[5]),
            )
            for entry in raw
        ]
        candles.reverse()  # API returns newest-first; we want chronological
        return candles


def get_candles(market: str, interval: str = "4h", limit: int = 42) -> list[Candle]:
    """Fetch OHLCV candles for a market from Bitvavo.

    Convenience function that opens a client, fetches candles, and closes
    the connection automatically.

    Args:
        market:   Market pair (e.g. "BTC-EUR").
        interval: Candle interval (e.g. "4h", "1d").
        limit:    Number of candles to return.

    Returns:
        List of Candle instances sorted oldest-first (chronological).
    """
    with BitvavoClient() as client:
        return client.get_candles(market, interval, limit)
