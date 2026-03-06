"""Alert checking service.

Contains the pure alert-checking function.  It does NOT touch the database —
it takes a coins list and active alerts list, and returns which alerts
triggered.  The caller is responsible for calling ``mark_triggered()`` on
each returned alert.
"""

from __future__ import annotations

from crypto_price_tracker.models import CoinData, PriceAlert


def check_alerts(
    coins: list[CoinData],
    active_alerts: list[PriceAlert],
) -> list[PriceAlert]:
    """Check active alerts against current prices.  Return those that triggered."""
    prices = {c.symbol: c.price for c in coins}
    triggered = []
    for alert in active_alerts:
        current_price = prices.get(alert.symbol)
        if current_price is None:
            continue
        if alert.direction == "above" and current_price >= alert.target_price:
            triggered.append(alert)
        elif alert.direction == "below" and current_price <= alert.target_price:
            triggered.append(alert)
    return triggered
