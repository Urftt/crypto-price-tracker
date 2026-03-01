"""Unit tests for the terminal display module."""

from __future__ import annotations

import io

import pytest
from rich.console import Console

from crypto_price_tracker.display import render_coin_detail, render_price_table
from crypto_price_tracker.models import CoinData


@pytest.fixture
def sample_coins() -> list[CoinData]:
    """Return a small list of sample CoinData objects for testing."""
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


def _make_console() -> tuple[Console, io.StringIO]:
    """Create a Console that writes to an in-memory StringIO buffer."""
    buf = io.StringIO()
    console = Console(file=buf, force_terminal=True, color_system="truecolor")
    return console, buf


class TestRenderPriceTable:
    def test_render_price_table_contains_all_coins(self, sample_coins: list[CoinData]) -> None:
        console, buf = _make_console()
        render_price_table(sample_coins, console=console)
        output = buf.getvalue()

        assert "BTC" in output
        assert "ETH" in output
        assert "XRP" in output
        assert "Bitcoin" in output
        assert "Ethereum" in output
        assert "Ripple" in output
        assert "Crypto Prices (EUR)" in output

    def test_render_price_table_formats_prices_with_eur(self, sample_coins: list[CoinData]) -> None:
        console, buf = _make_console()
        render_price_table(sample_coins, console=console)
        output = buf.getvalue()

        assert "EUR" in output
        # BTC price with thousands separator and 2 decimal places
        assert "56,754.00" in output
        # ETH price
        assert "2,345.50" in output

    def test_render_price_table_colors_positive_green(self, sample_coins: list[CoinData]) -> None:
        console, buf = _make_console()
        render_price_table(sample_coins, console=console)
        output = buf.getvalue()

        # BTC has +1.67% — the formatted string must appear in output
        assert "+1.67%" in output

    def test_render_price_table_colors_negative_red(self, sample_coins: list[CoinData]) -> None:
        console, buf = _make_console()
        render_price_table(sample_coins, console=console)
        output = buf.getvalue()

        # ETH has -3.21%
        assert "-3.21%" in output

    def test_render_price_table_empty_list(self) -> None:
        console, buf = _make_console()
        # Must not raise
        render_price_table([], console=console)
        output = buf.getvalue()

        # Table header (title) still shown even with no rows
        assert "Crypto Prices (EUR)" in output

    def test_render_price_table_volume_formatting(self, sample_coins: list[CoinData]) -> None:
        """Volume (EUR) should have thousands separators and no decimals."""
        console, buf = _make_console()
        render_price_table(sample_coins, console=console)
        output = buf.getvalue()

        # BTC volume_eur = 120,339,407 rounded to 0 decimals
        assert "120,339,407" in output


class TestRenderCoinDetail:
    def test_render_coin_detail_shows_all_fields(self, sample_coins: list[CoinData]) -> None:
        console, buf = _make_console()
        render_coin_detail(sample_coins[0], console=console)
        output = buf.getvalue()

        assert "BTC" in output
        assert "Bitcoin" in output
        assert "Price" in output
        assert "24h Change" in output
        assert "Volume" in output
        assert "EUR 56,754.00" in output
        assert "+1.67%" in output

    def test_render_coin_detail_negative_change_colored_red(self, sample_coins: list[CoinData]) -> None:
        console, buf = _make_console()
        render_coin_detail(sample_coins[1], console=console)  # ETH with -3.21%
        output = buf.getvalue()

        assert "-3.21%" in output
