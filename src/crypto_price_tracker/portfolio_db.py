"""SQLite storage layer for portfolio holdings.

Every public function accepts an optional ``db_path`` parameter so tests can
pass a temporary file path.  When *None*, the default XDG data directory is
used (``~/.local/share/crypto-tracker/portfolio.db``).
"""

from __future__ import annotations

import os
import sqlite3
from datetime import date
from pathlib import Path

from crypto_price_tracker.models import Holding


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_default_db_path() -> Path:
    """Return the default database path, creating parent dirs if needed."""
    xdg = os.environ.get("XDG_DATA_HOME")
    base = Path(xdg) if xdg else Path.home() / ".local" / "share"
    db_path = base / "crypto-tracker" / "portfolio.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return db_path


def _holding_factory(cursor: sqlite3.Cursor, row: tuple) -> Holding:
    """Row factory that returns *Holding* instances."""
    names = [description[0] for description in cursor.description]
    return Holding(**dict(zip(names, row)))


def _ensure_schema(conn: sqlite3.Connection) -> None:
    """Create the holdings table if it does not exist."""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS holdings (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol    TEXT NOT NULL,
            amount    REAL NOT NULL CHECK(amount > 0),
            buy_price REAL NOT NULL CHECK(buy_price > 0),
            buy_date  TEXT NOT NULL
        )
        """
    )


# ---------------------------------------------------------------------------
# Connection management
# ---------------------------------------------------------------------------

def get_connection(db_path: Path | None = None) -> sqlite3.Connection:
    """Open a connection with WAL mode, foreign keys, and schema check."""
    path = db_path or _get_default_db_path()
    conn = sqlite3.connect(str(path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = _holding_factory
    _ensure_schema(conn)
    return conn


# ---------------------------------------------------------------------------
# CRUD operations
# ---------------------------------------------------------------------------

def add_holding(
    symbol: str,
    amount: float,
    buy_price: float,
    buy_date: str | None = None,
    *,
    db_path: Path | None = None,
) -> int:
    """Insert a new holding and return its row ID."""
    if buy_date is None:
        buy_date = date.today().isoformat()
    # Validate date format (raises ValueError on bad input)
    date.fromisoformat(buy_date)
    symbol = symbol.upper()
    conn = get_connection(db_path)
    try:
        with conn:
            cursor = conn.execute(
                "INSERT INTO holdings (symbol, amount, buy_price, buy_date) VALUES (?, ?, ?, ?)",
                (symbol, amount, buy_price, buy_date),
            )
            return cursor.lastrowid
    finally:
        conn.close()


def remove_holding(holding_id: int, *, db_path: Path | None = None) -> bool:
    """Delete a holding by ID.  Return *True* if a row was deleted."""
    conn = get_connection(db_path)
    try:
        with conn:
            cursor = conn.execute("DELETE FROM holdings WHERE id = ?", (holding_id,))
            return cursor.rowcount > 0
    finally:
        conn.close()


def update_holding(
    holding_id: int,
    *,
    amount: float | None = None,
    buy_price: float | None = None,
    buy_date: str | None = None,
    db_path: Path | None = None,
) -> bool:
    """Update selected fields of a holding.  Return *True* if a row changed."""
    fields: list[str] = []
    values: list[object] = []
    if amount is not None:
        fields.append("amount = ?")
        values.append(amount)
    if buy_price is not None:
        fields.append("buy_price = ?")
        values.append(buy_price)
    if buy_date is not None:
        date.fromisoformat(buy_date)  # validate
        fields.append("buy_date = ?")
        values.append(buy_date)
    if not fields:
        return False
    values.append(holding_id)
    conn = get_connection(db_path)
    try:
        with conn:
            cursor = conn.execute(
                f"UPDATE holdings SET {', '.join(fields)} WHERE id = ?",
                tuple(values),
            )
            return cursor.rowcount > 0
    finally:
        conn.close()


def get_all_holdings(*, db_path: Path | None = None) -> list[Holding]:
    """Return all holdings ordered by symbol then buy date."""
    conn = get_connection(db_path)
    try:
        cursor = conn.execute("SELECT * FROM holdings ORDER BY symbol, buy_date")
        return cursor.fetchall()
    finally:
        conn.close()


def get_holdings_by_symbol(symbol: str, *, db_path: Path | None = None) -> list[Holding]:
    """Return holdings for a single symbol, ordered by buy date."""
    conn = get_connection(db_path)
    try:
        cursor = conn.execute(
            "SELECT * FROM holdings WHERE symbol = ? ORDER BY buy_date",
            (symbol.upper(),),
        )
        return cursor.fetchall()
    finally:
        conn.close()
