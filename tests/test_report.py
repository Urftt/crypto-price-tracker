"""Unit tests for the report generation module."""

from __future__ import annotations

import pytest

from crypto_price_tracker.models import CoinData, PriceAlert, WatchlistEntry
from crypto_price_tracker.portfolio import PortfolioRow, PortfolioSummary
from crypto_price_tracker.report import (
    build_summary_html,
    build_summary_text,
    generate_report_html,
    html_to_pdf,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_portfolio() -> PortfolioSummary:
    """Portfolio with BTC (positive P&L) and ETH (negative P&L)."""
    return PortfolioSummary(
        rows=[
            PortfolioRow(
                symbol="BTC",
                total_amount=0.5,
                avg_buy_price=45000.0,
                current_price=60000.0,
                total_cost=22500.0,
                current_value=30000.0,
                pnl_eur=7500.0,
                pnl_pct=33.33,
                allocation_pct=85.71,
                change_24h=2.5,
            ),
            PortfolioRow(
                symbol="ETH",
                total_amount=2.0,
                avg_buy_price=3000.0,
                current_price=2500.0,
                total_cost=6000.0,
                current_value=5000.0,
                pnl_eur=-1000.0,
                pnl_pct=-16.67,
                allocation_pct=14.29,
                change_24h=-1.2,
            ),
        ],
        total_value=35000.0,
        total_cost=28500.0,
        total_pnl_eur=6500.0,
        total_pnl_pct=22.81,
    )


@pytest.fixture
def empty_portfolio() -> PortfolioSummary:
    """Empty portfolio with no holdings."""
    return PortfolioSummary(
        rows=[], total_value=0, total_cost=0, total_pnl_eur=0, total_pnl_pct=0
    )


@pytest.fixture
def sample_coins() -> list[CoinData]:
    return [
        CoinData(symbol="BTC", name="Bitcoin", price=60000.0, change_24h=2.5, volume=1500.0, volume_eur=90000000.0),
        CoinData(symbol="ETH", name="Ethereum", price=2500.0, change_24h=-1.2, volume=50000.0, volume_eur=125000000.0),
    ]


@pytest.fixture
def sample_watchlist() -> list[WatchlistEntry]:
    return [
        WatchlistEntry(id=1, symbol="SOL", tags="Layer1", added_at="2026-03-01T10:00:00"),
        WatchlistEntry(id=2, symbol="LINK", tags="DeFi", added_at="2026-03-02T11:00:00"),
    ]


@pytest.fixture
def sample_alerts() -> list[PriceAlert]:
    return [
        PriceAlert(id=1, symbol="BTC", target_price=100000.0, direction="above", status="active", created_at="2026-03-01T10:00:00", triggered_at=None),
        PriceAlert(id=2, symbol="ETH", target_price=1500.0, direction="below", status="active", created_at="2026-03-01T11:00:00", triggered_at=None),
    ]


# ---------------------------------------------------------------------------
# generate_report_html tests
# ---------------------------------------------------------------------------

def test_report_html_contains_title(sample_portfolio, sample_coins, sample_watchlist, sample_alerts):
    html = generate_report_html(sample_portfolio, sample_coins, sample_watchlist, sample_alerts)
    assert "Crypto Portfolio Report" in html


def test_report_html_contains_timestamp(sample_portfolio, sample_coins, sample_watchlist, sample_alerts):
    html = generate_report_html(sample_portfolio, sample_coins, sample_watchlist, sample_alerts)
    assert "Generated:" in html


def test_report_html_contains_portfolio_section(sample_portfolio, sample_coins, sample_watchlist, sample_alerts):
    html = generate_report_html(sample_portfolio, sample_coins, sample_watchlist, sample_alerts)
    assert "Portfolio Summary" in html
    assert "EUR 35,000.00" in html  # total value


def test_report_html_contains_holdings_table(sample_portfolio, sample_coins, sample_watchlist, sample_alerts):
    html = generate_report_html(sample_portfolio, sample_coins, sample_watchlist, sample_alerts)
    assert "Holdings" in html
    assert "BTC" in html
    assert "ETH" in html


def test_report_html_contains_prices_section(sample_portfolio, sample_coins, sample_watchlist, sample_alerts):
    html = generate_report_html(sample_portfolio, sample_coins, sample_watchlist, sample_alerts)
    assert "Top Prices" in html
    assert "Bitcoin" in html
    assert "Ethereum" in html


def test_report_html_contains_watchlist_section(sample_portfolio, sample_coins, sample_watchlist, sample_alerts):
    html = generate_report_html(sample_portfolio, sample_coins, sample_watchlist, sample_alerts)
    assert "Watchlist" in html
    assert "SOL" in html
    assert "LINK" in html


def test_report_html_contains_alerts_section(sample_portfolio, sample_coins, sample_watchlist, sample_alerts):
    html = generate_report_html(sample_portfolio, sample_coins, sample_watchlist, sample_alerts)
    assert "Active Alerts" in html
    assert "EUR 100,000.00" in html


def test_report_html_green_for_positive_pnl(sample_portfolio, sample_coins, sample_watchlist, sample_alerts):
    html = generate_report_html(sample_portfolio, sample_coins, sample_watchlist, sample_alerts)
    assert "#3fb950" in html  # green for BTC positive P&L


def test_report_html_red_for_negative_pnl(sample_portfolio, sample_coins, sample_watchlist, sample_alerts):
    html = generate_report_html(sample_portfolio, sample_coins, sample_watchlist, sample_alerts)
    assert "#f85149" in html  # red for ETH negative P&L


def test_report_html_skips_empty_watchlist(sample_portfolio, sample_coins, sample_alerts):
    html = generate_report_html(sample_portfolio, sample_coins, [], sample_alerts)
    assert "Watchlist" not in html


def test_report_html_skips_empty_alerts(sample_portfolio, sample_coins, sample_watchlist):
    html = generate_report_html(sample_portfolio, sample_coins, sample_watchlist, [])
    assert "Active Alerts" not in html


# ---------------------------------------------------------------------------
# html_to_pdf tests
# ---------------------------------------------------------------------------

def test_html_to_pdf_returns_bytes():
    result = html_to_pdf("<html><body><h1>Test</h1></body></html>")
    assert isinstance(result, bytes)


def test_html_to_pdf_starts_with_pdf_header():
    result = html_to_pdf("<html><body><h1>Test</h1></body></html>")
    assert result.startswith(b"%PDF")


def test_html_to_pdf_non_empty():
    result = html_to_pdf("<html><body><h1>Test</h1></body></html>")
    assert len(result) > 100


def test_html_to_pdf_with_report_html(sample_portfolio, sample_coins, sample_watchlist, sample_alerts):
    html = generate_report_html(sample_portfolio, sample_coins, sample_watchlist, sample_alerts)
    result = html_to_pdf(html)
    assert isinstance(result, bytes)
    assert result.startswith(b"%PDF")
    assert len(result) > 100


# ---------------------------------------------------------------------------
# build_summary_text tests
# ---------------------------------------------------------------------------

def test_summary_text_contains_total_value(sample_portfolio):
    text = build_summary_text(sample_portfolio)
    assert "EUR 35,000.00" in text


def test_summary_text_contains_pnl(sample_portfolio):
    text = build_summary_text(sample_portfolio)
    assert "EUR 6,500.00" in text


def test_summary_text_under_4096_chars(sample_portfolio):
    text = build_summary_text(sample_portfolio)
    assert len(text) < 4096


def test_summary_text_empty_portfolio(empty_portfolio):
    text = build_summary_text(empty_portfolio)
    assert "No holdings" in text


# ---------------------------------------------------------------------------
# build_summary_html tests
# ---------------------------------------------------------------------------

def test_summary_html_is_html(sample_portfolio):
    html = build_summary_html(sample_portfolio)
    assert "<table" in html


def test_summary_html_contains_portfolio_data(sample_portfolio):
    html = build_summary_html(sample_portfolio)
    assert "EUR 35,000.00" in html
    assert "BTC" in html
