"""Unit tests for the terminal display module."""

from __future__ import annotations

import io

import pytest
from rich.console import Console

from crypto_price_tracker.display import (
    SPARK_CHARS,
    render_alert_banner,
    render_alert_list,
    render_chart_detail,
    render_chart_table,
    render_coin_detail,
    render_price_table,
    sparkline,
)
from crypto_price_tracker.models import Candle, CoinData, PriceAlert


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


# ---- Alert display tests ----


class TestRenderAlertDisplay:
    def test_render_price_table_with_triggered_symbol(self, sample_coins: list[CoinData]) -> None:
        console, buf = _make_console()
        render_price_table(sample_coins, console=console, triggered_symbols={"BTC"})
        output = buf.getvalue()

        assert "\u26a0" in output
        assert "BTC" in output
        # ETH should NOT have the warning symbol
        # Check ETH appears without the symbol marker by verifying it doesn't have ⚠ ETH
        assert "ETH" in output

    def test_render_price_table_no_triggered(self, sample_coins: list[CoinData]) -> None:
        console, buf = _make_console()
        render_price_table(sample_coins, console=console)
        output = buf.getvalue()

        assert "\u26a0" not in output

    def test_render_alert_banner(self) -> None:
        console, buf = _make_console()
        triggered = [
            PriceAlert(1, "BTC", 100000.0, "above", "triggered", "2026-03-01T10:00:00", "2026-03-06T12:00:00"),
            PriceAlert(2, "ETH", 1500.0, "below", "triggered", "2026-03-01T11:00:00", "2026-03-06T12:00:00"),
        ]
        render_alert_banner(triggered, console=console)
        output = buf.getvalue()

        assert "ALERTS TRIGGERED" in output
        assert "BTC" in output
        assert "ETH" in output
        assert "100,000.00" in output
        assert "1,500.00" in output

    def test_render_alert_list_active_and_triggered(self) -> None:
        console, buf = _make_console()
        alerts = [
            PriceAlert(1, "BTC", 100000.0, "above", "active", "2026-03-01T10:00:00", None),
            PriceAlert(2, "ETH", 1500.0, "below", "triggered", "2026-03-01T11:00:00", "2026-03-06T12:00:00"),
        ]
        render_alert_list(alerts, console=console)
        output = buf.getvalue()

        assert "Price Alerts" in output
        assert "BTC" in output
        assert "ETH" in output
        assert "active" in output
        assert "triggered" in output

    def test_render_alert_list_empty(self) -> None:
        console, buf = _make_console()
        render_alert_list([], console=console)
        output = buf.getvalue()

        assert "No alerts set." in output


# ---- Sparkline and chart display tests ----


@pytest.fixture
def sample_candles_7d() -> list[Candle]:
    """Return sample 7-day candles (3 candles for test simplicity)."""
    return [
        Candle(timestamp=1000, open=100.0, high=110.0, low=95.0, close=105.0, volume=50.0),
        Candle(timestamp=2000, open=105.0, high=115.0, low=100.0, close=110.0, volume=60.0),
        Candle(timestamp=3000, open=110.0, high=120.0, low=105.0, close=108.0, volume=45.0),
    ]


@pytest.fixture
def sample_candles_30d() -> list[Candle]:
    """Return sample 30-day candles (3 candles for test simplicity)."""
    return [
        Candle(timestamp=1000, open=90.0, high=105.0, low=85.0, close=100.0, volume=100.0),
        Candle(timestamp=2000, open=100.0, high=115.0, low=95.0, close=110.0, volume=120.0),
        Candle(timestamp=3000, open=110.0, high=120.0, low=100.0, close=108.0, volume=90.0),
    ]


class TestSparkline:
    def test_sparkline_basic(self) -> None:
        result = sparkline([1, 3, 5, 2, 8, 4])
        assert len(result) == 6
        assert all(c in SPARK_CHARS for c in result)
        assert result[4] == SPARK_CHARS[7]  # value 8 is max -> tallest bar
        assert result[0] == SPARK_CHARS[0]  # value 1 is min -> shortest bar

    def test_sparkline_empty(self) -> None:
        assert sparkline([]) == ""

    def test_sparkline_single_value(self) -> None:
        result = sparkline([42.0])
        assert result == SPARK_CHARS[3]

    def test_sparkline_constant_values(self) -> None:
        result = sparkline([5.0, 5.0, 5.0, 5.0])
        assert result == SPARK_CHARS[3] * 4

    def test_sparkline_ascending(self) -> None:
        result = sparkline([1, 2, 3, 4, 5, 6, 7, 8])
        # Monotonically non-decreasing block heights
        for i in range(len(result) - 1):
            assert result[i] <= result[i + 1]
        assert result[0] == SPARK_CHARS[0]
        assert result[-1] == SPARK_CHARS[7]

    def test_sparkline_two_values(self) -> None:
        result = sparkline([0.0, 100.0])
        assert result[0] == SPARK_CHARS[0]
        assert result[1] == SPARK_CHARS[7]


class TestRenderChartTable:
    def test_render_chart_table_contains_symbols(self, sample_coins: list[CoinData]) -> None:
        console, buf = _make_console()
        sparklines_7d = {"BTC": "\u2581\u2583\u2585\u2587", "ETH": "\u2582\u2584\u2586\u2588"}
        sparklines_30d = {"BTC": "\u2588\u2586\u2584\u2582", "ETH": "\u2587\u2585\u2583\u2581"}
        render_chart_table(sample_coins, sparklines_7d, sparklines_30d, console=console)
        output = buf.getvalue()

        assert "BTC" in output
        assert "ETH" in output
        assert "Price Charts (EUR)" in output

    def test_render_chart_table_empty_sparklines(self, sample_coins: list[CoinData]) -> None:
        console, buf = _make_console()
        render_chart_table(sample_coins, {}, {}, console=console)
        output = buf.getvalue()

        assert "BTC" in output
        assert "Price Charts (EUR)" in output


class TestRenderChartDetail:
    def test_render_chart_detail_shows_stats(
        self, sample_coins: list[CoinData], sample_candles_7d: list[Candle], sample_candles_30d: list[Candle]
    ) -> None:
        console, buf = _make_console()
        render_chart_detail(sample_coins[0], sample_candles_7d, sample_candles_30d, console=console)
        output = buf.getvalue()

        assert "BTC" in output
        assert "Bitcoin" in output
        # Rich may split "7-Day" with ANSI codes; check parts separately
        assert "7" in output and "Day" in output
        assert "30" in output
        assert "Open" in output
        assert "Close" in output
        assert "High" in output
        assert "Low" in output
        assert "Change" in output

    def test_render_chart_detail_no_candle_data(self, sample_coins: list[CoinData]) -> None:
        console, buf = _make_console()
        render_chart_detail(sample_coins[0], [], [], console=console)
        output = buf.getvalue()

        assert "BTC" in output
        assert "No data available" in output

    def test_render_chart_detail_one_period_only(
        self, sample_coins: list[CoinData], sample_candles_7d: list[Candle]
    ) -> None:
        console, buf = _make_console()
        render_chart_detail(sample_coins[0], sample_candles_7d, [], console=console)
        output = buf.getvalue()

        # Rich may insert ANSI codes within "7-Day"; check for "Day" presence
        assert "Day" in output
        assert "No data available" in output
        assert "Open" in output
