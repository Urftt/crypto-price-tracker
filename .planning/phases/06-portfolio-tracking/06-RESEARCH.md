# Phase 6: Portfolio Tracking - Research

**Researched:** 2026-03-05
**Domain:** SQLite persistence, CLI sub-subcommands, FastAPI CRUD, vanilla JS tabs
**Confidence:** HIGH

## Summary

Phase 6 adds portfolio tracking (holdings CRUD, P&L aggregation, export) to both CLI and web surfaces. The implementation sits on Python's stdlib `sqlite3` module for persistence, extends the existing argparse CLI with a nested `portfolio` subcommand group, adds POST/PUT/DELETE endpoints to the existing FastAPI app, and introduces a portfolio tab in the single-file HTML frontend.

The project's SQLite build runs in serialized mode (`threadsafety=3`), meaning connections can be safely shared across threads with `check_same_thread=False`. WAL journal mode should be enabled for concurrent read/write from CLI and web simultaneously. The XDG data path (`~/.local/share/crypto-tracker/portfolio.db`) can be resolved with a 3-line manual function rather than adding the `platformdirs` dependency, aligning with the project's minimal-dependencies constraint.

**Primary recommendation:** Use stdlib `sqlite3` with a dataclass-mapped row factory, manual XDG path resolution (no new dependencies), argparse nested subparsers, Pydantic models for FastAPI request bodies, and a tab-based UI in the existing `index.html`.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
1. **Holdings Input**: Both CLI and web; Symbol + amount + buy price + date; Multiple lots per coin; Add/remove/edit operations
2. **Data Persistence**: SQLite database at XDG data dir (`~/.local/share/crypto-tracker/portfolio.db`); Single file shared by CLI and web; Export only (CSV/JSON)
3. **Portfolio Display**: Full summary (total value, P&L EUR+%, cost basis, allocation); Full detail rows; Expandable lots; Both CLI and web

### Claude's Discretion
- SQLite library choice: stdlib `sqlite3` vs lightweight ORM
- XDG path resolution: `platformdirs` library or manual fallback
- Export format details: CSV columns, JSON structure
- Web UI: separate page vs tab within existing dashboard
- CLI `portfolio` subcommand exact syntax and flags

### Deferred Ideas (OUT OF SCOPE)
None captured during discussion.
</user_constraints>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `sqlite3` | stdlib (SQLite 3.45.1) | Holdings persistence, CRUD | Zero dependencies; already bundled; sufficient for single-file DB |
| `argparse` | stdlib | CLI sub-subcommand routing | Already in use; supports nested subparsers natively |
| `fastapi` | 0.135.1 (installed) | Portfolio API endpoints | Already in use; Pydantic integration for request validation |
| `pydantic` | 2.12.5 (installed) | Request body models for add/edit | Already a FastAPI transitive dep; type-safe validation |
| `rich` | 14.3.3 (installed) | Portfolio CLI table display | Already in use for price tables |
| `csv` | stdlib | CSV export | Standard library; no extra dependency needed |
| `json` | stdlib | JSON export | Standard library; no extra dependency needed |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `dataclasses` | stdlib | `Holding` model definition | Same pattern as existing `CoinData` |
| `pathlib` | stdlib | XDG path construction | Already used in `web.py` for `STATIC_DIR` |
| `datetime` | stdlib | Buy date parsing/storage | ISO 8601 format for SQLite TEXT columns |
| `os` | stdlib | `XDG_DATA_HOME` env var lookup | Manual XDG resolution |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `sqlite3` stdlib | `sqlite-utils` | Nicer API, but adds a dependency for a simple schema |
| `sqlite3` stdlib | `sqlalchemy` / `sqlmodel` | Full ORM overkill for 1 table with simple CRUD |
| Manual XDG | `platformdirs` | Cross-platform, but adds dependency for a Linux-only project |
| `argparse` nested | `click` | Better sub-subcommand UX, but project already uses argparse |

**No new dependencies required.** Everything needed is in the stdlib or already installed.

## Architecture Patterns

### Recommended Project Structure
```
src/crypto_price_tracker/
  models.py            # Add Holding dataclass alongside CoinData
  portfolio_db.py      # NEW: SQLite storage layer (CRUD, schema, connection)
  portfolio.py         # NEW: Portfolio service (aggregation, P&L, export)
  cli.py               # Extend: add portfolio subcommand group
  web.py               # Extend: add portfolio API endpoints
  static/index.html    # Extend: add portfolio tab
```

### Pattern 1: Dataclass-Mapped SQLite Row Factory
**What:** Custom `row_factory` that auto-maps SQLite rows to `Holding` dataclass instances.
**When to use:** Every SELECT query on the holdings table.
**Example:**
```python
# Source: Python docs sqlite3 row_factory recipe
from dataclasses import dataclass, fields

@dataclass(slots=True)
class Holding:
    id: int
    symbol: str
    amount: float
    buy_price: float
    buy_date: str  # ISO 8601 date string "YYYY-MM-DD"

def holding_factory(cursor, row):
    """Map a SQLite row to a Holding dataclass."""
    col_names = [desc[0] for desc in cursor.description]
    return Holding(**dict(zip(col_names, row)))

# Usage:
conn.row_factory = holding_factory
holdings = conn.execute("SELECT * FROM holdings WHERE symbol = ?", ("BTC",)).fetchall()
# holdings is list[Holding]
```

### Pattern 2: Connection-Per-Call with Context Manager
**What:** Open a new connection for each storage operation, use `with conn:` for auto-commit/rollback.
**When to use:** Every database operation in both CLI and web contexts.
**Example:**
```python
import sqlite3
from pathlib import Path

def _get_db_path() -> Path:
    import os
    xdg_data = os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")
    db_dir = Path(xdg_data) / "crypto-tracker"
    db_dir.mkdir(parents=True, exist_ok=True)
    return db_dir / "portfolio.db"

def get_connection() -> sqlite3.Connection:
    """Open a connection with WAL mode and row factory."""
    db_path = _get_db_path()
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = holding_factory
    return conn

def add_holding(symbol: str, amount: float, buy_price: float, buy_date: str) -> int:
    conn = get_connection()
    with conn:
        cursor = conn.execute(
            "INSERT INTO holdings (symbol, amount, buy_price, buy_date) VALUES (?, ?, ?, ?)",
            (symbol.upper(), amount, buy_price, buy_date),
        )
        return cursor.lastrowid
    conn.close()
```

### Pattern 3: Argparse Nested Subparsers
**What:** `crypto portfolio add|remove|edit|list|export` via argparse sub-subcommands.
**When to use:** CLI command routing.
**Example:**
```python
# In cli.py main():
portfolio_parser = subparsers.add_parser("portfolio", help="Manage portfolio holdings")
portfolio_sub = portfolio_parser.add_subparsers(dest="portfolio_command")

# add sub-subcommand
add_parser = portfolio_sub.add_parser("add", help="Add a holding")
add_parser.add_argument("symbol", type=str, help="Coin symbol (e.g. BTC)")
add_parser.add_argument("amount", type=float, help="Amount held")
add_parser.add_argument("buy_price", type=float, help="Buy price in EUR")
add_parser.add_argument("--date", type=str, default=None, help="Buy date (YYYY-MM-DD, default: today)")

# remove sub-subcommand
remove_parser = portfolio_sub.add_parser("remove", help="Remove a holding by ID")
remove_parser.add_argument("id", type=int, help="Holding ID to remove")

# edit sub-subcommand
edit_parser = portfolio_sub.add_parser("edit", help="Edit a holding by ID")
edit_parser.add_argument("id", type=int, help="Holding ID to edit")
edit_parser.add_argument("--amount", type=float)
edit_parser.add_argument("--buy-price", type=float)
edit_parser.add_argument("--date", type=str)

# list sub-subcommand
list_parser = portfolio_sub.add_parser("list", help="List portfolio holdings")

# export sub-subcommand
export_parser = portfolio_sub.add_parser("export", help="Export portfolio")
export_parser.add_argument("--format", choices=["csv", "json"], default="csv")
export_parser.add_argument("--output", "-o", type=str, default=None, help="Output file (default: stdout)")
```

### Pattern 4: Pydantic Request Models for FastAPI CRUD
**What:** Typed request bodies for add/edit operations via Pydantic BaseModel.
**When to use:** POST/PUT endpoints that accept a request body.
**Example:**
```python
from pydantic import BaseModel, Field

class HoldingCreate(BaseModel):
    symbol: str
    amount: float = Field(gt=0)
    buy_price: float = Field(gt=0)
    buy_date: str | None = None  # ISO date, defaults to today

class HoldingUpdate(BaseModel):
    amount: float | None = Field(default=None, gt=0)
    buy_price: float | None = Field(default=None, gt=0)
    buy_date: str | None = None

# In web.py:
@app.post("/api/portfolio")
def add_holding(holding: HoldingCreate):
    hid = portfolio_db.add_holding(holding.symbol, holding.amount, holding.buy_price, holding.buy_date)
    return {"id": hid, "status": "created"}

@app.put("/api/portfolio/{holding_id}")
def edit_holding(holding_id: int, update: HoldingUpdate):
    portfolio_db.update_holding(holding_id, update)
    return {"status": "updated"}

@app.delete("/api/portfolio/{holding_id}")
def remove_holding(holding_id: int):
    portfolio_db.delete_holding(holding_id)
    return {"status": "deleted"}

@app.get("/api/portfolio")
def get_portfolio():
    # Returns aggregated portfolio with current prices
    ...
```

### Pattern 5: Tab Switching in Existing Single-File HTML
**What:** Add a portfolio tab to `index.html` with CSS-only visibility toggling plus JS data loading.
**When to use:** Extending the dashboard without adding a build step or separate pages.
**Example:**
```html
<!-- Tab navigation -->
<nav class="tabs">
  <button class="tab active" onclick="switchTab('prices')">Prices</button>
  <button class="tab" onclick="switchTab('portfolio')">Portfolio</button>
</nav>

<!-- Tab content sections -->
<div id="tab-prices" class="tab-content active">
  <!-- existing price table -->
</div>
<div id="tab-portfolio" class="tab-content" style="display:none;">
  <!-- portfolio table + add form -->
</div>

<script>
function switchTab(name) {
  document.querySelectorAll('.tab-content').forEach(el => el.style.display = 'none');
  document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
  document.getElementById('tab-' + name).style.display = '';
  document.querySelector(`.tab[onclick*="${name}"]`).classList.add('active');
  if (name === 'portfolio') loadPortfolio();
}
</script>
```

### Anti-Patterns to Avoid
- **Global singleton connection:** Do NOT store a single `sqlite3.Connection` as a module-level variable shared by CLI and web. Open per-call and close after use to avoid stale locks.
- **String-formatted SQL:** NEVER use f-strings or `.format()` in SQL queries. Always use parameterized queries (`?` placeholders).
- **Skipping WAL mode:** Without WAL, the CLI and web server will block each other on concurrent reads/writes.
- **Storing prices in the portfolio DB:** Current prices come from the API. The portfolio DB only stores holdings (symbol, amount, buy_price, buy_date).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| SQL injection protection | Custom escaping | `?` parameter binding (sqlite3 stdlib) | Impossible to get right manually |
| Date parsing/validation | Regex date parser | `datetime.date.fromisoformat()` | Handles edge cases, raises clear errors |
| EUR number formatting | Custom formatter | `locale`-aware formatting or existing `fmt()` JS function | Consistent with nl-NL locale already used |
| Schema migration | Manual ALTER TABLE scripts | `CREATE TABLE IF NOT EXISTS` + version pragma | Simple enough for 1 table; no migration library needed |
| Request validation | Manual type checking in endpoints | Pydantic `BaseModel` (already available via FastAPI) | Type coercion, error messages, OpenAPI docs for free |

**Key insight:** This project's schema is simple enough (one table, no relations) that a full ORM or migration framework would add complexity without benefit. The stdlib `sqlite3` with careful patterns is the right choice.

## Common Pitfalls

### Pitfall 1: SQLite File Locking Between CLI and Web
**What goes wrong:** CLI writes block web reads (or vice versa), causing `sqlite3.OperationalError: database is locked`.
**Why it happens:** Default journal mode (DELETE) locks the entire database during writes.
**How to avoid:** Enable WAL mode on every connection: `conn.execute("PRAGMA journal_mode=WAL")`. WAL allows concurrent readers with a single writer.
**Warning signs:** Timeout errors when running `crypto portfolio add` while the web server is active.

### Pitfall 2: Missing Database Directory
**What goes wrong:** `sqlite3.connect()` fails because `~/.local/share/crypto-tracker/` does not exist.
**Why it happens:** SQLite creates the file but not parent directories.
**How to avoid:** Always call `db_dir.mkdir(parents=True, exist_ok=True)` before connecting.
**Warning signs:** `FileNotFoundError` on first run.

### Pitfall 3: Schema Not Created on Fresh Install
**What goes wrong:** Queries fail with `sqlite3.OperationalError: no such table: holdings`.
**Why it happens:** The DB file exists but the schema was never applied.
**How to avoid:** Run `CREATE TABLE IF NOT EXISTS` on every connection open (idempotent).
**Warning signs:** Works after manual schema setup but fails on a fresh machine.

### Pitfall 4: Argparse Nested Subparsers Default Behavior
**What goes wrong:** `crypto portfolio` with no sub-subcommand silently does nothing or errors.
**Why it happens:** argparse does not require a subcommand by default.
**How to avoid:** Check `args.portfolio_command` and print help if None: `if not args.portfolio_command: portfolio_parser.print_help()`.
**Warning signs:** User runs `crypto portfolio` and gets no output.

### Pitfall 5: Floating Point Precision in Financial Calculations
**What goes wrong:** P&L calculations show wrong amounts due to float rounding.
**Why it happens:** IEEE 754 floating point cannot represent all decimal values exactly.
**How to avoid:** Store prices as float (matching existing `CoinData` pattern) but round display output to 2 decimal places for EUR amounts. For this project's scope (personal tracker, not accounting software), this is sufficient. Use `round(value, 2)` for display.
**Warning signs:** Totals that are off by 0.01 EUR.

### Pitfall 6: Date Handling Across CLI and Web
**What goes wrong:** Dates are stored inconsistently (different formats, timezones).
**Why it happens:** No standardized format enforced at the storage layer.
**How to avoid:** Store as ISO 8601 TEXT (`YYYY-MM-DD`). Validate with `datetime.date.fromisoformat()` before insert. Default to `datetime.date.today().isoformat()` when not provided.
**Warning signs:** Sort-by-date produces wrong order.

## Code Examples

### SQLite Schema Creation (Idempotent)
```python
# Source: sqlite3 stdlib docs + project conventions
SCHEMA = """
CREATE TABLE IF NOT EXISTS holdings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    amount REAL NOT NULL CHECK(amount > 0),
    buy_price REAL NOT NULL CHECK(buy_price > 0),
    buy_date TEXT NOT NULL
);
"""

def ensure_schema(conn: sqlite3.Connection) -> None:
    """Create the holdings table if it doesn't exist."""
    conn.executescript(SCHEMA)
```

### Portfolio Aggregation Service
```python
# Aggregation logic for portfolio display
from dataclasses import dataclass

@dataclass(slots=True)
class PortfolioRow:
    symbol: str
    total_amount: float
    avg_buy_price: float
    current_price: float
    total_cost: float
    current_value: float
    pnl_eur: float
    pnl_pct: float
    allocation_pct: float
    change_24h: float

def aggregate_portfolio(holdings: list[Holding], prices: dict[str, CoinData]) -> list[PortfolioRow]:
    """Aggregate holdings by symbol, compute P&L using live prices."""
    from collections import defaultdict

    by_symbol = defaultdict(list)
    for h in holdings:
        by_symbol[h.symbol].append(h)

    rows = []
    total_value = sum(
        sum(h.amount for h in lots) * prices[sym].price
        for sym, lots in by_symbol.items()
        if sym in prices
    )

    for sym, lots in by_symbol.items():
        if sym not in prices:
            continue
        coin = prices[sym]
        total_amount = sum(h.amount for h in lots)
        total_cost = sum(h.amount * h.buy_price for h in lots)
        avg_buy = total_cost / total_amount if total_amount else 0
        current_value = total_amount * coin.price
        pnl_eur = current_value - total_cost
        pnl_pct = (pnl_eur / total_cost * 100) if total_cost else 0
        allocation = (current_value / total_value * 100) if total_value else 0

        rows.append(PortfolioRow(
            symbol=sym,
            total_amount=total_amount,
            avg_buy_price=round(avg_buy, 2),
            current_price=coin.price,
            total_cost=round(total_cost, 2),
            current_value=round(current_value, 2),
            pnl_eur=round(pnl_eur, 2),
            pnl_pct=round(pnl_pct, 2),
            allocation_pct=round(allocation, 2),
            change_24h=coin.change_24h,
        ))

    rows.sort(key=lambda r: r.current_value, reverse=True)
    return rows
```

### CSV Export
```python
import csv
import io

def export_csv(holdings: list[Holding], output: io.TextIOBase | None = None) -> str | None:
    """Export holdings to CSV. Returns string if no output stream given."""
    fieldnames = ["id", "symbol", "amount", "buy_price", "buy_date"]
    buf = output or io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames)
    writer.writeheader()
    for h in holdings:
        writer.writerow({
            "id": h.id,
            "symbol": h.symbol,
            "amount": h.amount,
            "buy_price": h.buy_price,
            "buy_date": h.buy_date,
        })
    if output is None:
        return buf.getvalue()
```

### JSON Export
```python
import json
import dataclasses

def export_json(holdings: list[Holding]) -> str:
    """Export holdings to JSON string."""
    return json.dumps(
        [dataclasses.asdict(h) for h in holdings],
        indent=2,
    )
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `sqlite3.connect()` with DELETE journal | WAL mode (`PRAGMA journal_mode=WAL`) | Always was available, widely adopted | Concurrent CLI + web access without locking |
| Hardcoded `threadsafety=1` | Dynamic `threadsafety` detection | Python 3.11 | Can check actual capability at runtime |
| `appdirs` library | `platformdirs` (successor) | 2021 | platformdirs is the maintained fork; but manual XDG is fine for Linux-only |
| Pydantic v1 | Pydantic v2 (2.12.5 installed) | 2023 | Use `BaseModel` with `Field(gt=0)` validators; model_config instead of Config class |

**Deprecated/outdated:**
- `appdirs`: Replaced by `platformdirs`; but for this project, manual XDG is recommended (zero deps).
- `sqlite3` default datetime adapters: Deprecated in Python 3.12; store dates as TEXT in ISO format.

## Open Questions

1. **Portfolio symbols not in top 100**
   - What we know: `get_top_coins(top_n=100)` returns a limited set; user may hold coins outside this set.
   - What's unclear: Should the portfolio show "price unavailable" or try to fetch specifically?
   - Recommendation: Show "N/A" for price/P&L when a held coin is not in the top 100. This is the simplest approach and consistent with the existing API design. The user can still track the holding; they just won't see a live price.

2. **Lot IDs for editing/removal**
   - What we know: Users need to reference specific lots for edit/remove operations.
   - What's unclear: How does the user discover the lot ID?
   - Recommendation: The `crypto portfolio list` command and the web UI both show lot IDs. The ID is the SQLite `ROWID`/autoincrement primary key.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 |
| Config file | none (no pytest.ini or pyproject.toml `[tool.pytest]` section) |
| Quick run command | `uv run pytest tests/ -x -q` |
| Full suite command | `uv run pytest tests/ -v` |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| PORT-01 | Holding dataclass + SQLite schema creation | unit | `uv run pytest tests/test_portfolio_db.py::test_schema_creation -x` | No - Wave 0 |
| PORT-02 | Add/remove/edit CRUD operations | unit | `uv run pytest tests/test_portfolio_db.py::test_crud_operations -x` | No - Wave 0 |
| PORT-03 | Portfolio aggregation (avg price, P&L, allocation) | unit | `uv run pytest tests/test_portfolio.py::test_aggregation -x` | No - Wave 0 |
| PORT-04 | CLI portfolio subcommands (add/remove/edit/list/export) | unit | `uv run pytest tests/test_cli.py::test_portfolio_commands -x` | No - Wave 0 |
| PORT-05 | Web API endpoints (GET/POST/PUT/DELETE /api/portfolio) | unit | `uv run pytest tests/test_web.py::test_portfolio_endpoints -x` | No - Wave 0 |
| PORT-06 | CSV and JSON export | unit | `uv run pytest tests/test_portfolio.py::test_export -x` | No - Wave 0 |
| PORT-07 | XDG data path resolution | unit | `uv run pytest tests/test_portfolio_db.py::test_xdg_path -x` | No - Wave 0 |
| PORT-08 | Web UI portfolio tab loads and displays data | smoke | Manual browser test | N/A |

### Sampling Rate
- **Per task commit:** `uv run pytest tests/ -x -q`
- **Per wave merge:** `uv run pytest tests/ -v`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_portfolio_db.py` -- covers PORT-01, PORT-02, PORT-07 (SQLite storage layer)
- [ ] `tests/test_portfolio.py` -- covers PORT-03, PORT-06 (aggregation service, export)
- [ ] Extend `tests/test_cli.py` -- covers PORT-04 (portfolio CLI subcommands)
- [ ] Extend `tests/test_web.py` -- covers PORT-05 (portfolio API endpoints)
- [ ] `tests/conftest.py` -- shared fixtures (in-memory SQLite, mock holdings, mock CoinData)

## Sources

### Primary (HIGH confidence)
- [Python sqlite3 docs](https://docs.python.org/3/library/sqlite3.html) - row_factory, thread safety, context manager, parameter binding, Python 3.12 changes
- [SQLite WAL documentation](https://sqlite.org/wal.html) - concurrent read/write behavior
- [Python argparse docs](https://docs.python.org/3/library/argparse.html) - nested subparsers pattern
- [FastAPI request body docs](https://fastapi.tiangolo.com/tutorial/body/) - Pydantic model for POST/PUT

### Secondary (MEDIUM confidence)
- [platformdirs API docs](https://platformdirs.readthedocs.io/en/latest/api.html) - `user_data_path()` signature and Linux behavior
- [Python sqlite3 thread safety analysis](https://ricardoanderegg.com/posts/python-sqlite-thread-safety/) - `threadsafety=3` means serialized mode is safe
- [FastAPI SQLite discussions](https://github.com/fastapi/fastapi/discussions/5199) - `check_same_thread=False` is safe when `threadsafety=3`
- [Nested argparse gist](https://gist.github.com/jirihnidek/3f5d36636198e852280f619847d22d9e) - sub-subcommand working example

### Tertiary (LOW confidence)
- None. All findings verified with primary or secondary sources.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - all stdlib or already installed; verified versions on the system
- Architecture: HIGH - patterns verified against official Python/FastAPI docs and confirmed with runtime checks (`threadsafety=3`, SQLite 3.45.1)
- Pitfalls: HIGH - WAL locking, directory creation, schema idempotency are well-documented issues with known solutions

**Research date:** 2026-03-05
**Valid until:** 2026-04-05 (stable domain; stdlib + SQLite rarely changes)
