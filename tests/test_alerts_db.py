"""Unit tests for the SQLite alerts storage layer."""

from __future__ import annotations

from pathlib import Path

import pytest

from crypto_price_tracker.models import PriceAlert
from crypto_price_tracker.alerts_db import (
    add_alert,
    clear_triggered_alerts,
    get_active_alerts,
    get_alert_connection,
    get_all_alerts,
    mark_triggered,
    remove_alert,
)


def test_get_alert_connection_creates_db_file(tmp_db_path):
    conn = get_alert_connection(tmp_db_path)
    try:
        assert tmp_db_path.exists()
    finally:
        conn.close()


def test_alert_schema_created_on_connect(tmp_db_path):
    conn = get_alert_connection(tmp_db_path)
    try:
        conn.row_factory = None
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='alerts'"
        )
        assert cursor.fetchone() is not None
    finally:
        conn.close()


def test_alert_wal_mode_enabled(tmp_db_path):
    conn = get_alert_connection(tmp_db_path)
    try:
        conn.row_factory = None
        cursor = conn.execute("PRAGMA journal_mode")
        mode = cursor.fetchone()[0]
        assert mode == "wal"
    finally:
        conn.close()


def test_add_alert_returns_id(tmp_db_path):
    id1 = add_alert("BTC", 100000.0, "above", db_path=tmp_db_path)
    assert id1 == 1
    id2 = add_alert("ETH", 1500.0, "below", db_path=tmp_db_path)
    assert id2 == 2


def test_add_alert_uppercases_symbol(tmp_db_path):
    add_alert("btc", 100000.0, "above", db_path=tmp_db_path)
    alerts = get_all_alerts(db_path=tmp_db_path)
    assert alerts[0].symbol == "BTC"


def test_add_alert_default_direction(tmp_db_path):
    add_alert("BTC", 100000.0, db_path=tmp_db_path)
    alerts = get_all_alerts(db_path=tmp_db_path)
    assert alerts[0].direction == "above"


def test_add_alert_below_direction(tmp_db_path):
    add_alert("ETH", 1500.0, "below", db_path=tmp_db_path)
    alerts = get_all_alerts(db_path=tmp_db_path)
    assert alerts[0].direction == "below"


def test_add_alert_rejects_invalid_direction(tmp_db_path):
    with pytest.raises(ValueError):
        add_alert("BTC", 100000.0, "sideways", db_path=tmp_db_path)


def test_get_active_alerts_empty(tmp_db_path):
    alerts = get_active_alerts(db_path=tmp_db_path)
    assert alerts == []


def test_get_active_alerts_returns_only_active(tmp_db_path):
    id1 = add_alert("BTC", 100000.0, "above", db_path=tmp_db_path)
    add_alert("ETH", 1500.0, "below", db_path=tmp_db_path)
    mark_triggered(id1, db_path=tmp_db_path)
    active = get_active_alerts(db_path=tmp_db_path)
    assert len(active) == 1
    assert active[0].status == "active"


def test_get_all_alerts_ordering(tmp_db_path):
    id1 = add_alert("BTC", 100000.0, "above", db_path=tmp_db_path)
    add_alert("ETH", 1500.0, "below", db_path=tmp_db_path)
    mark_triggered(id1, db_path=tmp_db_path)
    all_alerts = get_all_alerts(db_path=tmp_db_path)
    assert len(all_alerts) == 2
    assert all_alerts[0].status == "active"
    assert all_alerts[1].status == "triggered"


def test_remove_alert_success(tmp_db_path):
    alert_id = add_alert("BTC", 100000.0, "above", db_path=tmp_db_path)
    assert remove_alert(alert_id, db_path=tmp_db_path) is True
    assert get_all_alerts(db_path=tmp_db_path) == []


def test_remove_alert_not_found(tmp_db_path):
    assert remove_alert(999, db_path=tmp_db_path) is False


def test_mark_triggered_success(tmp_db_path):
    alert_id = add_alert("BTC", 100000.0, "above", db_path=tmp_db_path)
    assert mark_triggered(alert_id, db_path=tmp_db_path) is True
    all_alerts = get_all_alerts(db_path=tmp_db_path)
    assert all_alerts[0].status == "triggered"
    assert all_alerts[0].triggered_at is not None


def test_mark_triggered_already_triggered(tmp_db_path):
    alert_id = add_alert("BTC", 100000.0, "above", db_path=tmp_db_path)
    assert mark_triggered(alert_id, db_path=tmp_db_path) is True
    assert mark_triggered(alert_id, db_path=tmp_db_path) is False


def test_mark_triggered_not_found(tmp_db_path):
    assert mark_triggered(999, db_path=tmp_db_path) is False


def test_clear_triggered_alerts(tmp_db_path):
    id1 = add_alert("BTC", 100000.0, "above", db_path=tmp_db_path)
    id2 = add_alert("ETH", 1500.0, "below", db_path=tmp_db_path)
    mark_triggered(id1, db_path=tmp_db_path)
    mark_triggered(id2, db_path=tmp_db_path)
    assert clear_triggered_alerts(db_path=tmp_db_path) == 2
    assert get_all_alerts(db_path=tmp_db_path) == []


def test_clear_triggered_alerts_preserves_active(tmp_db_path):
    id1 = add_alert("BTC", 100000.0, "above", db_path=tmp_db_path)
    add_alert("ETH", 1500.0, "below", db_path=tmp_db_path)
    mark_triggered(id1, db_path=tmp_db_path)
    assert clear_triggered_alerts(db_path=tmp_db_path) == 1
    remaining = get_all_alerts(db_path=tmp_db_path)
    assert len(remaining) == 1
    assert remaining[0].status == "active"


def test_row_factory_returns_price_alert_instances(tmp_db_path):
    add_alert("BTC", 100000.0, "above", db_path=tmp_db_path)
    alerts = get_all_alerts(db_path=tmp_db_path)
    assert isinstance(alerts, list)
    assert isinstance(alerts[0], PriceAlert)
    assert alerts[0].symbol == "BTC"
    assert alerts[0].target_price == 100000.0
    assert alerts[0].direction == "above"
    assert alerts[0].status == "active"


def test_both_tables_coexist_in_same_db(tmp_db_path):
    from crypto_price_tracker.portfolio_db import get_connection

    conn_portfolio = get_connection(tmp_db_path)
    conn_alerts = get_alert_connection(tmp_db_path)
    try:
        conn_portfolio.row_factory = None
        conn_alerts.row_factory = None
        tables_p = conn_portfolio.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('holdings', 'alerts') ORDER BY name"
        ).fetchall()
        tables_a = conn_alerts.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('holdings', 'alerts') ORDER BY name"
        ).fetchall()
        table_names_p = [t[0] for t in tables_p]
        table_names_a = [t[0] for t in tables_a]
        assert "holdings" in table_names_p
        assert "alerts" in table_names_p
        assert "holdings" in table_names_a
        assert "alerts" in table_names_a
    finally:
        conn_portfolio.close()
        conn_alerts.close()
