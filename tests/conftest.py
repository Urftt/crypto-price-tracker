"""Shared test fixtures for portfolio tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from crypto_price_tracker.models import CoinData, Holding


@pytest.fixture
def tmp_db_path(tmp_path: Path) -> Path:
    """Return a temporary SQLite database file path inside pytest's tmp_path."""
    return tmp_path / "test_portfolio.db"


@pytest.fixture
def sample_holdings() -> list[Holding]:
    """Return a list of sample Holding objects for testing."""
    return [
        Holding(id=1, symbol="BTC", amount=0.5, buy_price=45000.0, buy_date="2026-01-15"),
        Holding(id=2, symbol="BTC", amount=0.3, buy_price=50000.0, buy_date="2026-02-20"),
        Holding(id=3, symbol="ETH", amount=10.0, buy_price=2000.0, buy_date="2026-01-10"),
    ]


@pytest.fixture
def sample_prices() -> dict[str, CoinData]:
    """Return a dict of symbol -> CoinData for testing portfolio aggregation."""
    return {
        "BTC": CoinData(
            symbol="BTC",
            name="Bitcoin",
            price=60000.0,
            change_24h=2.5,
            volume=1500.0,
            volume_eur=90000000.0,
        ),
        "ETH": CoinData(
            symbol="ETH",
            name="Ethereum",
            price=2500.0,
            change_24h=-1.2,
            volume=50000.0,
            volume_eur=125000000.0,
        ),
    }
