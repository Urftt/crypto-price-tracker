"""SQLite storage layer for price alerts.

Every public function accepts an optional ``db_path`` parameter so tests can
pass a temporary file path.  When *None*, the default path is resolved via
``portfolio_db._get_default_db_path()`` (same DB file as portfolio holdings).
"""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

from crypto_price_tracker.models import PriceAlert
from crypto_price_tracker import portfolio_db


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _alert_factory(cursor: sqlite3.Cursor, row: tuple) -> PriceAlert:
    """Row factory that returns *PriceAlert* instances."""
    names = [description[0] for description in cursor.description]
    return PriceAlert(**dict(zip(names, row)))


def _ensure_alert_schema(conn: sqlite3.Connection) -> None:
    """Create the alerts table if it does not exist."""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS alerts (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol        TEXT NOT NULL,
            target_price  REAL NOT NULL CHECK(target_price > 0),
            direction     TEXT NOT NULL CHECK(direction IN ('above', 'below')),
            status        TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'triggered')),
            created_at    TEXT NOT NULL,
            triggered_at  TEXT
        )
        """
    )


# ---------------------------------------------------------------------------
# Connection management
# ---------------------------------------------------------------------------

def get_alert_connection(db_path: Path | None = None) -> sqlite3.Connection:
    """Open a connection with WAL mode, foreign keys, and alert schema check."""
    path = db_path or portfolio_db._get_default_db_path()
    conn = sqlite3.connect(str(path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = _alert_factory
    _ensure_alert_schema(conn)
    return conn


# ---------------------------------------------------------------------------
# CRUD operations
# ---------------------------------------------------------------------------

def add_alert(
    symbol: str,
    target_price: float,
    direction: str = "above",
    *,
    db_path: Path | None = None,
) -> int:
    """Insert a new alert and return its row ID."""
    if direction not in ("above", "below"):
        raise ValueError(f"Invalid direction: {direction!r} (must be 'above' or 'below')")
    symbol = symbol.upper()
    created_at = datetime.now().isoformat()
    conn = get_alert_connection(db_path)
    try:
        with conn:
            cursor = conn.execute(
                "INSERT INTO alerts (symbol, target_price, direction, status, created_at) VALUES (?, ?, ?, 'active', ?)",
                (symbol, target_price, direction, created_at),
            )
            return cursor.lastrowid
    finally:
        conn.close()


def get_active_alerts(*, db_path: Path | None = None) -> list[PriceAlert]:
    """Return all active alerts ordered by creation time."""
    conn = get_alert_connection(db_path)
    try:
        cursor = conn.execute("SELECT * FROM alerts WHERE status = 'active' ORDER BY created_at")
        return cursor.fetchall()
    finally:
        conn.close()


def get_all_alerts(*, db_path: Path | None = None) -> list[PriceAlert]:
    """Return all alerts, active first then triggered, ordered by creation time."""
    conn = get_alert_connection(db_path)
    try:
        cursor = conn.execute(
            "SELECT * FROM alerts ORDER BY CASE WHEN status = 'active' THEN 0 ELSE 1 END, created_at"
        )
        return cursor.fetchall()
    finally:
        conn.close()


def remove_alert(alert_id: int, *, db_path: Path | None = None) -> bool:
    """Delete an alert by ID.  Return *True* if a row was deleted."""
    conn = get_alert_connection(db_path)
    try:
        with conn:
            cursor = conn.execute("DELETE FROM alerts WHERE id = ?", (alert_id,))
            return cursor.rowcount > 0
    finally:
        conn.close()


def mark_triggered(alert_id: int, *, db_path: Path | None = None) -> bool:
    """Mark an alert as triggered.  Return *True* if a row was updated.

    The ``AND status = 'active'`` guard prevents double-triggering in
    concurrent requests.
    """
    conn = get_alert_connection(db_path)
    try:
        with conn:
            cursor = conn.execute(
                "UPDATE alerts SET status = 'triggered', triggered_at = ? WHERE id = ? AND status = 'active'",
                (datetime.now().isoformat(), alert_id),
            )
            return cursor.rowcount > 0
    finally:
        conn.close()


def clear_triggered_alerts(*, db_path: Path | None = None) -> int:
    """Delete all triggered alerts.  Return the number of deleted rows."""
    conn = get_alert_connection(db_path)
    try:
        with conn:
            cursor = conn.execute("DELETE FROM alerts WHERE status = 'triggered'")
            return cursor.rowcount
    finally:
        conn.close()
