"""Unit tests for the SQLite portfolio storage layer."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from crypto_price_tracker.models import Holding
from crypto_price_tracker.portfolio_db import (
    _get_default_db_path,
    add_holding,
    get_all_holdings,
    get_connection,
    get_holdings_by_symbol,
    remove_holding,
    update_holding,
)


def test_get_connection_creates_db_file(tmp_db_path):
    conn = get_connection(tmp_db_path)
    assert tmp_db_path.exists()
    conn.close()


def test_schema_created_on_connect(tmp_db_path):
    conn = get_connection(tmp_db_path)
    # Override row factory for metadata query (not a Holding row)
    conn.row_factory = None
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='holdings'")
    assert cursor.fetchone() is not None
    conn.close()


def test_wal_mode_enabled(tmp_db_path):
    conn = get_connection(tmp_db_path)
    # Need a raw cursor without the custom row factory for pragma queries
    conn.row_factory = None
    cursor = conn.execute("PRAGMA journal_mode")
    result = cursor.fetchone()
    assert result[0] == "wal"
    conn.close()


def test_add_holding_returns_id(tmp_db_path):
    hid1 = add_holding("BTC", 0.5, 45000.0, "2026-01-15", db_path=tmp_db_path)
    assert hid1 == 1
    hid2 = add_holding("ETH", 1.0, 2000.0, "2026-01-20", db_path=tmp_db_path)
    assert hid2 == 2


def test_add_holding_defaults_date(tmp_db_path):
    add_holding("ETH", 1.0, 2000.0, db_path=tmp_db_path)
    holdings = get_all_holdings(db_path=tmp_db_path)
    assert holdings[0].buy_date == date.today().isoformat()


def test_add_holding_uppercases_symbol(tmp_db_path):
    add_holding("btc", 1.0, 100.0, "2026-01-01", db_path=tmp_db_path)
    holdings = get_all_holdings(db_path=tmp_db_path)
    assert holdings[0].symbol == "BTC"


def test_add_holding_rejects_invalid_date(tmp_db_path):
    with pytest.raises(ValueError):
        add_holding("BTC", 1.0, 100.0, "not-a-date", db_path=tmp_db_path)


def test_get_all_holdings_empty(tmp_db_path):
    holdings = get_all_holdings(db_path=tmp_db_path)
    assert holdings == []


def test_get_all_holdings_returns_holdings(tmp_db_path):
    add_holding("BTC", 0.5, 45000.0, "2026-01-15", db_path=tmp_db_path)
    add_holding("ETH", 1.0, 2000.0, "2026-01-20", db_path=tmp_db_path)
    holdings = get_all_holdings(db_path=tmp_db_path)
    assert len(holdings) == 2
    assert all(isinstance(h, Holding) for h in holdings)


def test_get_holdings_by_symbol(tmp_db_path):
    add_holding("BTC", 0.5, 45000.0, "2026-01-15", db_path=tmp_db_path)
    add_holding("ETH", 1.0, 2000.0, "2026-01-20", db_path=tmp_db_path)
    add_holding("BTC", 0.3, 50000.0, "2026-02-01", db_path=tmp_db_path)
    btc_holdings = get_holdings_by_symbol("BTC", db_path=tmp_db_path)
    assert len(btc_holdings) == 2
    assert all(h.symbol == "BTC" for h in btc_holdings)


def test_remove_holding_success(tmp_db_path):
    hid = add_holding("BTC", 0.5, 45000.0, "2026-01-15", db_path=tmp_db_path)
    assert remove_holding(hid, db_path=tmp_db_path) is True
    assert get_all_holdings(db_path=tmp_db_path) == []


def test_remove_holding_not_found(tmp_db_path):
    assert remove_holding(999, db_path=tmp_db_path) is False


def test_update_holding_amount(tmp_db_path):
    hid = add_holding("BTC", 0.5, 45000.0, "2026-01-15", db_path=tmp_db_path)
    assert update_holding(hid, amount=0.3, db_path=tmp_db_path) is True
    holdings = get_all_holdings(db_path=tmp_db_path)
    assert holdings[0].amount == 0.3


def test_update_holding_not_found(tmp_db_path):
    assert update_holding(999, amount=1.0, db_path=tmp_db_path) is False


def test_update_holding_no_fields(tmp_db_path):
    add_holding("BTC", 0.5, 45000.0, "2026-01-15", db_path=tmp_db_path)
    assert update_holding(1, db_path=tmp_db_path) is False


def test_row_factory_returns_holding_instances(tmp_db_path):
    add_holding("BTC", 0.5, 45000.0, "2026-01-15", db_path=tmp_db_path)
    holdings = get_all_holdings(db_path=tmp_db_path)
    assert isinstance(holdings, list)
    assert isinstance(holdings[0], Holding)
    assert holdings[0].symbol == "BTC"
    assert holdings[0].amount == 0.5
    assert holdings[0].buy_price == 45000.0
    assert holdings[0].buy_date == "2026-01-15"


def test_xdg_path_default(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    result = _get_default_db_path()
    assert result == tmp_path / "crypto-tracker" / "portfolio.db"
    assert result.parent.exists()
