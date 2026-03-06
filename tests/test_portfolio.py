"""Unit tests for portfolio aggregation and export."""

from __future__ import annotations

import csv
import io
import json

import pytest

from crypto_price_tracker.models import CoinData, Holding
from crypto_price_tracker.portfolio import (
    PortfolioRow,
    PortfolioSummary,
    aggregate_portfolio,
    export_csv,
    export_json,
)


def test_aggregate_empty_portfolio(sample_prices):
    summary = aggregate_portfolio([], sample_prices)
    assert summary.rows == []
    assert summary.total_value == 0
    assert summary.total_cost == 0
    assert summary.total_pnl_eur == 0


def test_aggregate_single_coin(sample_holdings, sample_prices):
    eth_only = [h for h in sample_holdings if h.symbol == "ETH"]
    summary = aggregate_portfolio(eth_only, sample_prices)
    assert len(summary.rows) == 1
    row = summary.rows[0]
    assert row.total_amount == 10.0
    assert row.avg_buy_price == 2000.0
    assert row.current_value == 25000.0
    assert row.pnl_eur == 5000.0
    assert row.pnl_pct == 25.0


def test_aggregate_multiple_lots(sample_holdings, sample_prices):
    btc_only = [h for h in sample_holdings if h.symbol == "BTC"]
    summary = aggregate_portfolio(btc_only, sample_prices)
    assert len(summary.rows) == 1
    row = summary.rows[0]
    assert row.total_amount == 0.8
    assert row.total_cost == 37500.0  # 0.5*45000 + 0.3*50000
    assert row.avg_buy_price == 46875.0  # 37500 / 0.8
    assert row.current_value == 48000.0  # 0.8 * 60000
    assert row.pnl_eur == 10500.0  # 48000 - 37500


def test_aggregate_allocation_pct(sample_holdings, sample_prices):
    summary = aggregate_portfolio(sample_holdings, sample_prices)
    total_alloc = sum(r.allocation_pct for r in summary.rows if r.allocation_pct is not None)
    assert abs(total_alloc - 100.0) < 0.1


def test_aggregate_coin_not_in_prices(sample_holdings, sample_prices):
    doge = Holding(id=4, symbol="DOGE", amount=1000.0, buy_price=0.1, buy_date="2026-01-01")
    holdings = sample_holdings + [doge]
    summary = aggregate_portfolio(holdings, sample_prices)
    doge_row = next(r for r in summary.rows if r.symbol == "DOGE")
    assert doge_row.current_price is None
    assert doge_row.pnl_eur is None
    assert doge_row.pnl_pct is None
    assert doge_row.allocation_pct is None
    # DOGE cost basis (100.0) should be included in total_value
    assert summary.total_value == 48000.0 + 25000.0 + 100.0


def test_aggregate_sorts_by_value_descending(sample_holdings, sample_prices):
    summary = aggregate_portfolio(sample_holdings, sample_prices)
    priced_rows = [r for r in summary.rows if r.current_value is not None]
    values = [r.current_value for r in priced_rows]
    assert values == sorted(values, reverse=True)


def test_export_csv_format(sample_holdings):
    result = export_csv(sample_holdings)
    reader = csv.reader(io.StringIO(result))
    rows = list(reader)
    assert rows[0] == ["id", "symbol", "amount", "buy_price", "buy_date"]
    assert len(rows) == 4  # header + 3 data rows
    assert rows[1][1] == "BTC"


def test_export_csv_empty():
    result = export_csv([])
    reader = csv.reader(io.StringIO(result))
    rows = list(reader)
    assert len(rows) == 1  # header only


def test_export_json_format(sample_holdings):
    result = export_json(sample_holdings)
    data = json.loads(result)
    assert isinstance(data, list)
    assert len(data) == 3
    assert set(data[0].keys()) == {"id", "symbol", "amount", "buy_price", "buy_date"}


def test_export_json_empty():
    result = export_json([])
    data = json.loads(result)
    assert data == []


def test_summary_totals(sample_holdings, sample_prices):
    summary = aggregate_portfolio(sample_holdings, sample_prices)
    assert summary.total_cost == 57500.0  # 37500 + 20000
    assert summary.total_value == 73000.0  # 48000 + 25000
    assert summary.total_pnl_eur == 15500.0
    expected_pct = (15500.0 / 57500.0) * 100
    assert abs(summary.total_pnl_pct - expected_pct) < 0.01
