"""Unit tests for the alert checking logic (pure function, no DB)."""

from __future__ import annotations

import pytest

from crypto_price_tracker.alerts import check_alerts
from crypto_price_tracker.models import CoinData, PriceAlert


def _coin(symbol: str, price: float) -> CoinData:
    """Helper to create a CoinData with only symbol and price set."""
    return CoinData(symbol=symbol, name=symbol, price=price, change_24h=0.0, volume=0.0, volume_eur=0.0)


def _alert(
    id: int = 1,
    symbol: str = "BTC",
    target_price: float = 100000.0,
    direction: str = "above",
    status: str = "active",
) -> PriceAlert:
    """Helper to create a PriceAlert with sensible defaults."""
    return PriceAlert(
        id=id,
        symbol=symbol,
        target_price=target_price,
        direction=direction,
        status=status,
        created_at="2026-03-01T10:00:00",
        triggered_at=None,
    )


def test_check_alerts_no_alerts(sample_prices):
    coins = list(sample_prices.values())
    result = check_alerts(coins, [])
    assert result == []


def test_check_alerts_no_coins(sample_alerts):
    result = check_alerts([], sample_alerts)
    assert result == []


def test_check_alerts_above_triggers():
    alert = _alert(symbol="BTC", target_price=50000.0, direction="above")
    coins = [_coin("BTC", 60000.0)]
    result = check_alerts(coins, [alert])
    assert len(result) == 1
    assert result[0].symbol == "BTC"


def test_check_alerts_above_exact_match():
    alert = _alert(symbol="BTC", target_price=60000.0, direction="above")
    coins = [_coin("BTC", 60000.0)]
    result = check_alerts(coins, [alert])
    assert len(result) == 1


def test_check_alerts_above_not_reached():
    alert = _alert(symbol="BTC", target_price=100000.0, direction="above")
    coins = [_coin("BTC", 60000.0)]
    result = check_alerts(coins, [alert])
    assert result == []


def test_check_alerts_below_triggers():
    alert = _alert(symbol="ETH", target_price=3000.0, direction="below")
    coins = [_coin("ETH", 2500.0)]
    result = check_alerts(coins, [alert])
    assert len(result) == 1


def test_check_alerts_below_exact_match():
    alert = _alert(symbol="ETH", target_price=2500.0, direction="below")
    coins = [_coin("ETH", 2500.0)]
    result = check_alerts(coins, [alert])
    assert len(result) == 1


def test_check_alerts_below_not_reached():
    alert = _alert(symbol="ETH", target_price=1000.0, direction="below")
    coins = [_coin("ETH", 2500.0)]
    result = check_alerts(coins, [alert])
    assert result == []


def test_check_alerts_coin_not_in_prices():
    alert = _alert(symbol="DOGE", target_price=0.1, direction="above")
    coins = [_coin("BTC", 60000.0), _coin("ETH", 2500.0)]
    result = check_alerts(coins, [alert])
    assert result == []


def test_check_alerts_multiple_triggers():
    alerts = [
        _alert(id=1, symbol="BTC", target_price=50000.0, direction="above"),
        _alert(id=2, symbol="ETH", target_price=3000.0, direction="below"),
    ]
    coins = [_coin("BTC", 60000.0), _coin("ETH", 2500.0)]
    result = check_alerts(coins, alerts)
    assert len(result) == 2


def test_check_alerts_only_checks_active_status():
    """The function is stateless — it doesn't filter by status."""
    alert = _alert(symbol="BTC", target_price=50000.0, direction="above", status="triggered")
    coins = [_coin("BTC", 60000.0)]
    result = check_alerts(coins, [alert])
    assert len(result) == 1
