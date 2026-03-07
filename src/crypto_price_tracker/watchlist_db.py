"""SQLite storage layer for watchlist entries.

Every public function accepts an optional ``db_path`` parameter so tests can
pass a temporary file path.  When *None*, the default path is resolved via
``portfolio_db._get_default_db_path()`` (same DB file as portfolio/alerts).
"""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

from crypto_price_tracker.models import WatchlistEntry
from crypto_price_tracker import portfolio_db

VALID_TAGS = frozenset({"Layer1", "Layer2", "DeFi", "Meme", "Exchange", "Privacy"})


def _watchlist_factory(cursor: sqlite3.Cursor, row: tuple) -> WatchlistEntry:
    """Row factory that returns *WatchlistEntry* instances."""
    names = [description[0] for description in cursor.description]
    return WatchlistEntry(**dict(zip(names, row)))


def _ensure_watchlist_schema(conn: sqlite3.Connection) -> None:
    """Create the watchlist table if it does not exist."""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS watchlist (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol   TEXT NOT NULL UNIQUE,
            tags     TEXT NOT NULL DEFAULT '',
            added_at TEXT NOT NULL
        )
        """
    )


def get_watchlist_connection(db_path: Path | None = None) -> sqlite3.Connection:
    """Open a connection with WAL mode, foreign keys, and watchlist schema check."""
    path = db_path or portfolio_db._get_default_db_path()
    conn = sqlite3.connect(str(path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = _watchlist_factory
    _ensure_watchlist_schema(conn)
    return conn


def _normalize_tags(tags: list[str]) -> str:
    """Validate and normalize a list of tag strings to a comma-separated string.

    Tags are case-insensitive on input but stored with canonical casing from VALID_TAGS.
    Invalid tags raise ValueError.
    """
    if not tags:
        return ""
    normalized = []
    tag_lookup = {t.lower(): t for t in VALID_TAGS}
    for tag in tags:
        canonical = tag_lookup.get(tag.lower())
        if canonical is None:
            raise ValueError(
                f"Invalid tag: {tag!r}. Valid tags: {', '.join(sorted(VALID_TAGS))}"
            )
        if canonical not in normalized:
            normalized.append(canonical)
    return ",".join(sorted(normalized))


def add_watchlist_entry(
    symbol: str,
    tags: list[str] | None = None,
    *,
    db_path: Path | None = None,
) -> int:
    """Insert a new watchlist entry and return its row ID.

    Raises sqlite3.IntegrityError if symbol already exists.
    Raises ValueError if any tag is invalid.
    """
    symbol = symbol.upper()
    tags_str = _normalize_tags(tags or [])
    added_at = datetime.now().isoformat()
    conn = get_watchlist_connection(db_path)
    try:
        with conn:
            cursor = conn.execute(
                "INSERT INTO watchlist (symbol, tags, added_at) VALUES (?, ?, ?)",
                (symbol, tags_str, added_at),
            )
            return cursor.lastrowid
    finally:
        conn.close()


def remove_watchlist_entry(symbol: str, *, db_path: Path | None = None) -> bool:
    """Delete a watchlist entry by symbol. Return *True* if a row was deleted."""
    conn = get_watchlist_connection(db_path)
    try:
        with conn:
            cursor = conn.execute(
                "DELETE FROM watchlist WHERE symbol = ?", (symbol.upper(),)
            )
            return cursor.rowcount > 0
    finally:
        conn.close()


def get_all_watchlist_entries(
    *, tag: str | None = None, db_path: Path | None = None
) -> list[WatchlistEntry]:
    """Return all watchlist entries, optionally filtered by tag.

    When tag is provided, only entries whose tags column contains
    the tag (case-insensitive match) are returned.
    """
    conn = get_watchlist_connection(db_path)
    try:
        if tag:
            # Match tag as substring within comma-separated list
            # Use LIKE with the canonical tag form for correctness
            tag_lookup = {t.lower(): t for t in VALID_TAGS}
            canonical = tag_lookup.get(tag.lower(), tag)
            cursor = conn.execute(
                "SELECT * FROM watchlist WHERE ',' || tags || ',' LIKE ? ORDER BY added_at",
                (f"%,{canonical},%",),
            )
        else:
            cursor = conn.execute(
                "SELECT * FROM watchlist ORDER BY added_at"
            )
        return cursor.fetchall()
    finally:
        conn.close()


def update_watchlist_tags(
    symbol: str, tags: list[str], *, db_path: Path | None = None
) -> bool:
    """Replace all tags on a watchlist entry. Return *True* if a row was updated.

    Raises ValueError if any tag is invalid.
    """
    tags_str = _normalize_tags(tags)
    conn = get_watchlist_connection(db_path)
    try:
        with conn:
            cursor = conn.execute(
                "UPDATE watchlist SET tags = ? WHERE symbol = ?",
                (tags_str, symbol.upper()),
            )
            return cursor.rowcount > 0
    finally:
        conn.close()


def get_watchlist_symbols(*, db_path: Path | None = None) -> set[str]:
    """Return the set of all symbols currently on the watchlist."""
    conn = get_watchlist_connection(db_path)
    try:
        conn.row_factory = None  # Override to get raw tuples
        cursor = conn.execute("SELECT symbol FROM watchlist")
        return {row[0] for row in cursor.fetchall()}
    finally:
        conn.close()
