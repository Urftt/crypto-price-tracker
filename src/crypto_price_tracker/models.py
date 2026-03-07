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


@dataclass(slots=True)
class Holding:
    """A single portfolio holding (one lot).

    Fields:
        id:        SQLite row ID (autoincrement primary key)
        symbol:    Coin ticker symbol (e.g. "BTC"), stored uppercase
        amount:    Quantity held (e.g. 0.5)
        buy_price: Purchase price per unit in EUR
        buy_date:  Purchase date as ISO 8601 string "YYYY-MM-DD"
    """

    id: int
    symbol: str
    amount: float
    buy_price: float
    buy_date: str


@dataclass(slots=True)
class PriceAlert:
    """A price alert for a cryptocurrency.

    Fields:
        id:            SQLite row ID (autoincrement primary key)
        symbol:        Coin ticker symbol (e.g. "BTC"), stored uppercase
        target_price:  Target price in EUR
        direction:     "above" or "below"
        status:        "active" or "triggered"
        created_at:    Creation timestamp as ISO 8601 string
        triggered_at:  Trigger timestamp as ISO 8601 string, or None
    """

    id: int
    symbol: str
    target_price: float
    direction: str
    status: str
    created_at: str
    triggered_at: str | None


@dataclass(slots=True)
class Candle:
    """A single OHLCV candle from the Bitvavo candles endpoint.

    Fields:
        timestamp: Unix timestamp in milliseconds
        open:      Opening price in EUR
        high:      Highest price in interval
        low:       Lowest price in interval
        close:     Closing price in EUR
        volume:    Volume traded in the interval
    """

    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(slots=True)
class WatchlistEntry:
    """A watchlist entry with optional category tags.

    Fields:
        id:        SQLite row ID (autoincrement primary key)
        symbol:    Coin ticker symbol (e.g. "ETH"), stored uppercase
        tags:      Comma-separated tag string (e.g. "Layer1,DeFi") or empty string
        added_at:  Timestamp as ISO 8601 string
    """

    id: int
    symbol: str
    tags: str
    added_at: str
