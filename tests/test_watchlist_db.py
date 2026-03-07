"""Unit tests for the SQLite watchlist storage layer."""

from __future__ import annotations

import pytest

from crypto_price_tracker.models import WatchlistEntry
from crypto_price_tracker.watchlist_db import (
    VALID_TAGS,
    add_watchlist_entry,
    get_all_watchlist_entries,
    get_watchlist_connection,
    get_watchlist_symbols,
    remove_watchlist_entry,
    update_watchlist_tags,
)


def test_get_watchlist_connection_creates_db_file(tmp_db_path):
    conn = get_watchlist_connection(tmp_db_path)
    try:
        assert tmp_db_path.exists()
    finally:
        conn.close()


def test_watchlist_schema_created_on_connect(tmp_db_path):
    conn = get_watchlist_connection(tmp_db_path)
    try:
        conn.row_factory = None
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='watchlist'"
        )
        assert cursor.fetchone() is not None
    finally:
        conn.close()


def test_watchlist_wal_mode_enabled(tmp_db_path):
    conn = get_watchlist_connection(tmp_db_path)
    try:
        conn.row_factory = None
        cursor = conn.execute("PRAGMA journal_mode")
        mode = cursor.fetchone()[0]
        assert mode == "wal"
    finally:
        conn.close()


def test_add_watchlist_entry_returns_id(tmp_db_path):
    id1 = add_watchlist_entry("ETH", db_path=tmp_db_path)
    assert id1 == 1
    id2 = add_watchlist_entry("BTC", db_path=tmp_db_path)
    assert id2 == 2


def test_add_watchlist_entry_uppercases_symbol(tmp_db_path):
    add_watchlist_entry("eth", db_path=tmp_db_path)
    entries = get_all_watchlist_entries(db_path=tmp_db_path)
    assert entries[0].symbol == "ETH"


def test_add_watchlist_entry_with_tags(tmp_db_path):
    add_watchlist_entry("ETH", ["DeFi", "Layer1"], db_path=tmp_db_path)
    entries = get_all_watchlist_entries(db_path=tmp_db_path)
    assert entries[0].tags == "DeFi,Layer1"


def test_add_watchlist_entry_no_tags(tmp_db_path):
    add_watchlist_entry("BTC", db_path=tmp_db_path)
    entries = get_all_watchlist_entries(db_path=tmp_db_path)
    assert entries[0].tags == ""


def test_add_watchlist_entry_duplicate_symbol_raises(tmp_db_path):
    add_watchlist_entry("ETH", db_path=tmp_db_path)
    import sqlite3
    with pytest.raises(sqlite3.IntegrityError):
        add_watchlist_entry("ETH", db_path=tmp_db_path)


def test_add_watchlist_entry_invalid_tag_raises(tmp_db_path):
    with pytest.raises(ValueError, match="Invalid tag"):
        add_watchlist_entry("ETH", ["InvalidTag"], db_path=tmp_db_path)


def test_add_watchlist_entry_tag_case_insensitive(tmp_db_path):
    add_watchlist_entry("ETH", ["defi", "LAYER1"], db_path=tmp_db_path)
    entries = get_all_watchlist_entries(db_path=tmp_db_path)
    assert entries[0].tags == "DeFi,Layer1"


def test_remove_watchlist_entry_success(tmp_db_path):
    add_watchlist_entry("ETH", db_path=tmp_db_path)
    assert remove_watchlist_entry("ETH", db_path=tmp_db_path) is True
    assert get_all_watchlist_entries(db_path=tmp_db_path) == []


def test_remove_watchlist_entry_not_found(tmp_db_path):
    assert remove_watchlist_entry("ETH", db_path=tmp_db_path) is False


def test_remove_watchlist_entry_case_insensitive(tmp_db_path):
    add_watchlist_entry("ETH", db_path=tmp_db_path)
    assert remove_watchlist_entry("eth", db_path=tmp_db_path) is True


def test_get_all_watchlist_entries_empty(tmp_db_path):
    entries = get_all_watchlist_entries(db_path=tmp_db_path)
    assert entries == []


def test_get_all_watchlist_entries_returns_ordered(tmp_db_path):
    add_watchlist_entry("BTC", db_path=tmp_db_path)
    add_watchlist_entry("ETH", db_path=tmp_db_path)
    entries = get_all_watchlist_entries(db_path=tmp_db_path)
    assert len(entries) == 2
    assert entries[0].symbol == "BTC"
    assert entries[1].symbol == "ETH"


def test_get_all_watchlist_entries_filter_by_tag(tmp_db_path):
    add_watchlist_entry("ETH", ["DeFi", "Layer1"], db_path=tmp_db_path)
    add_watchlist_entry("DOGE", ["Meme"], db_path=tmp_db_path)
    add_watchlist_entry("BTC", ["Layer1"], db_path=tmp_db_path)

    defi = get_all_watchlist_entries(tag="DeFi", db_path=tmp_db_path)
    assert len(defi) == 1
    assert defi[0].symbol == "ETH"

    layer1 = get_all_watchlist_entries(tag="Layer1", db_path=tmp_db_path)
    assert len(layer1) == 2
    symbols = {e.symbol for e in layer1}
    assert symbols == {"ETH", "BTC"}


def test_get_all_watchlist_entries_filter_tag_case_insensitive(tmp_db_path):
    add_watchlist_entry("ETH", ["DeFi"], db_path=tmp_db_path)
    entries = get_all_watchlist_entries(tag="defi", db_path=tmp_db_path)
    assert len(entries) == 1


def test_update_watchlist_tags_success(tmp_db_path):
    add_watchlist_entry("ETH", ["DeFi"], db_path=tmp_db_path)
    assert update_watchlist_tags("ETH", ["Layer1", "Layer2"], db_path=tmp_db_path) is True
    entries = get_all_watchlist_entries(db_path=tmp_db_path)
    assert entries[0].tags == "Layer1,Layer2"


def test_update_watchlist_tags_not_found(tmp_db_path):
    assert update_watchlist_tags("ETH", ["DeFi"], db_path=tmp_db_path) is False


def test_update_watchlist_tags_invalid_raises(tmp_db_path):
    add_watchlist_entry("ETH", db_path=tmp_db_path)
    with pytest.raises(ValueError, match="Invalid tag"):
        update_watchlist_tags("ETH", ["BadTag"], db_path=tmp_db_path)


def test_update_watchlist_tags_clear_all(tmp_db_path):
    add_watchlist_entry("ETH", ["DeFi"], db_path=tmp_db_path)
    assert update_watchlist_tags("ETH", [], db_path=tmp_db_path) is True
    entries = get_all_watchlist_entries(db_path=tmp_db_path)
    assert entries[0].tags == ""


def test_get_watchlist_symbols_empty(tmp_db_path):
    assert get_watchlist_symbols(db_path=tmp_db_path) == set()


def test_get_watchlist_symbols_returns_set(tmp_db_path):
    add_watchlist_entry("ETH", db_path=tmp_db_path)
    add_watchlist_entry("BTC", db_path=tmp_db_path)
    symbols = get_watchlist_symbols(db_path=tmp_db_path)
    assert symbols == {"ETH", "BTC"}


def test_row_factory_returns_watchlist_entry_instances(tmp_db_path):
    add_watchlist_entry("ETH", ["DeFi"], db_path=tmp_db_path)
    entries = get_all_watchlist_entries(db_path=tmp_db_path)
    assert isinstance(entries, list)
    assert isinstance(entries[0], WatchlistEntry)
    assert entries[0].symbol == "ETH"
    assert entries[0].tags == "DeFi"
    assert entries[0].added_at is not None


def test_watchlist_table_coexists_with_others(tmp_db_path):
    from crypto_price_tracker.portfolio_db import get_connection
    from crypto_price_tracker.alerts_db import get_alert_connection

    get_connection(tmp_db_path)
    get_alert_connection(tmp_db_path)
    get_watchlist_connection(tmp_db_path)

    import sqlite3
    conn = sqlite3.connect(str(tmp_db_path))
    try:
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name IN ('holdings', 'alerts', 'watchlist') ORDER BY name"
        ).fetchall()
        table_names = [t[0] for t in tables]
        assert "holdings" in table_names
        assert "alerts" in table_names
        assert "watchlist" in table_names
    finally:
        conn.close()


def test_add_watchlist_entry_deduplicates_tags(tmp_db_path):
    add_watchlist_entry("ETH", ["DeFi", "defi", "DeFi"], db_path=tmp_db_path)
    entries = get_all_watchlist_entries(db_path=tmp_db_path)
    assert entries[0].tags == "DeFi"
