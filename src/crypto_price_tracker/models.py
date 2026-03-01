"""Data models for the crypto price tracker."""

from dataclasses import dataclass


@dataclass(slots=True)
class CoinData:
    """Represents a single cryptocurrency's market data.

    Fields:
        symbol:     Ticker symbol (e.g. "BTC")
        name:       Human-readable name (e.g. "Bitcoin")
        price:      Current price in EUR (from the `last` field of the Bitvavo ticker)
        change_24h: 24h price change as a percentage (computed: ((last - open) / open) * 100)
        volume:     24h trading volume in the base asset (e.g. BTC amount traded)
        volume_eur: 24h trading volume in EUR (from `volumeQuote` — used for ranking)
    """

    symbol: str
    name: str
    price: float
    change_24h: float
    volume: float
    volume_eur: float
