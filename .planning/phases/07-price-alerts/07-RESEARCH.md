# Phase 7: Price Alerts - Research

**Researched:** 2026-03-06
**Domain:** SQLite CRUD, CLI subcommands, FastAPI endpoints, Rich terminal display, vanilla JS toast notifications
**Confidence:** HIGH

## Summary

Phase 7 adds price alert functionality across CLI and web surfaces. Users set target prices for coins (above/below), and when prices cross those thresholds, they get notified: Rich Panel banners in the CLI, toast notifications on the web. Alerts are persisted in the same SQLite database as portfolio holdings (`portfolio.db`), following the identical WAL/connection-per-call pattern established in Phase 6.

The implementation is straightforward: a new `alerts_db.py` module mirrors `portfolio_db.py` patterns exactly, an `alerts.py` service handles checking logic, and integration points hook into existing `get_top_coins()` call sites. No new dependencies are required -- everything uses the existing stack (stdlib sqlite3, Rich 13.7.1, FastAPI, vanilla JS/CSS).

**Primary recommendation:** Follow the portfolio_db.py pattern exactly for the storage layer, use Rich Panel with `border_style="yellow"` for CLI alert banners, and implement toast notifications as a self-contained CSS/JS block in index.html (no external library needed for such a simple use case).

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
1. **Alert Checking Model** -- Passive only; alerts checked every time prices are fetched (during `crypto prices`, `crypto watch`, web dashboard auto-refresh). No background daemon. CLI banner above price table plus inline marker on affected row. Flash once in watch mode (mark as triggered in DB). `crypto alert check` command with exit code 1 if triggered, exit 0 if none.
2. **Alert Conditions & Types** -- Above/below only, simple absolute price targets. One-shot (triggers once, marked as triggered). CLI syntax: `crypto alert add BTC 100000 --above` (default `--above`). `crypto alert list` shows active first, then triggered. `crypto alert remove <ID>`.
3. **Notification Experience** -- CLI: colored banner + inline marker using Rich. Web: toast auto-dismiss ~10s, no sound, no browser Notification API. Exit codes: `crypto alert check` uses exit 1 on trigger.
4. **Alerts Panel Layout (Web)** -- New "Alerts" tab. Two entry points: form on alerts tab + "Set Alert" button in coin detail modal. Two sections: Active Alerts (with remove buttons), Triggered Alerts (with timestamps). Individual delete + "Clear All Triggered" bulk button.

### Claude's Discretion
- SQLite schema design for alerts table (columns, constraints, indexes)
- Alert checking logic integration point (where in the price-fetch flow to inject the check)
- Toast notification CSS/JS implementation details
- Rich formatting specifics for CLI banner and inline markers
- API endpoint design (routes, request/response shapes)
- How the coin dropdown in the web form is populated

### Deferred Ideas (OUT OF SCOPE)
None captured during discussion.
</user_constraints>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| sqlite3 | stdlib | Alert persistence | Already used for portfolio; same DB file, same patterns |
| Rich | 13.7.1 | CLI alert banners and inline markers | Already a project dependency; Panel class for banners |
| FastAPI | >=0.115 | Alert CRUD API endpoints | Already used for web server; Pydantic models for validation |
| argparse | stdlib | CLI `alert` subcommand group | Already used for all CLI parsing |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Pydantic | (via FastAPI) | Request body validation for alert creation | Web API endpoint |
| dataclasses | stdlib | `PriceAlert` model | Data transfer object |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Custom toast CSS/JS | Toastify library | Not worth adding a dependency for 30 lines of CSS/JS |
| Separate alerts.db | Same portfolio.db | One DB file is simpler; `_ensure_schema` handles both tables |

**Installation:**
```bash
# No new dependencies required -- all libraries already in pyproject.toml
```

## Architecture Patterns

### Recommended Project Structure
```
src/crypto_price_tracker/
  models.py           # Add PriceAlert dataclass
  alerts_db.py         # NEW: SQLite CRUD (mirrors portfolio_db.py)
  alerts.py            # NEW: Alert checking service
  cli.py               # Add alert subcommand group
  display.py           # Add render_alert_banner(), render_alert_list()
  web.py               # Add /api/alerts endpoints
  static/index.html    # Add alerts tab, toast system, modal button
```

### Pattern 1: alerts_db.py -- Mirror portfolio_db.py Exactly
**What:** Same connection-per-call pattern with `_ensure_schema`, WAL mode, row factory
**When to use:** All database operations for alerts
**Example:**
```python
# Source: Existing portfolio_db.py pattern (verified in codebase)
from crypto_price_tracker.models import PriceAlert

def _alert_factory(cursor: sqlite3.Cursor, row: tuple) -> PriceAlert:
    """Row factory that returns PriceAlert instances."""
    names = [description[0] for description in cursor.description]
    return PriceAlert(**dict(zip(names, row)))

def _ensure_alert_schema(conn: sqlite3.Connection) -> None:
    """Create the alerts table if it does not exist."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol        TEXT NOT NULL,
            target_price  REAL NOT NULL CHECK(target_price > 0),
            direction     TEXT NOT NULL CHECK(direction IN ('above', 'below')),
            status        TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'triggered')),
            created_at    TEXT NOT NULL,
            triggered_at  TEXT
        )
    """)

def get_alert_connection(db_path: Path | None = None) -> sqlite3.Connection:
    """Open a connection with WAL mode, create alerts table."""
    path = db_path or _get_default_db_path()
    conn = sqlite3.connect(str(path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = _alert_factory
    _ensure_alert_schema(conn)
    return conn
```

**Critical detail:** Reuse `_get_default_db_path()` from `portfolio_db.py` (import it or extract to a shared helper). Both tables live in the same `portfolio.db` file. Each module's `_ensure_schema` only creates its own table -- `CREATE TABLE IF NOT EXISTS` is idempotent so both can run on every connection.

### Pattern 2: Alert Checking Service (alerts.py)
**What:** Pure function that takes coins list + active alerts, returns list of newly triggered alerts
**When to use:** Called after every `get_top_coins()` invocation
**Example:**
```python
# Source: Project pattern (pure function, no side effects in core logic)
from crypto_price_tracker.models import CoinData, PriceAlert

def check_alerts(
    coins: list[CoinData],
    active_alerts: list[PriceAlert],
) -> list[PriceAlert]:
    """Check active alerts against current prices. Return those that triggered."""
    prices = {c.symbol: c.price for c in coins}
    triggered = []
    for alert in active_alerts:
        current_price = prices.get(alert.symbol)
        if current_price is None:
            continue
        if alert.direction == "above" and current_price >= alert.target_price:
            triggered.append(alert)
        elif alert.direction == "below" and current_price <= alert.target_price:
            triggered.append(alert)
    return triggered
```

**Important:** The function is pure -- it returns which alerts triggered but does NOT update the DB. The caller (CLI command or web endpoint) is responsible for calling `mark_triggered()` on each returned alert. This keeps the checking logic testable without DB fixtures.

### Pattern 3: CLI Integration Hook
**What:** Alert checking injected after `get_top_coins()` in `cmd_prices()` and `cmd_watch()`
**When to use:** Every price fetch in CLI
**Example:**
```python
# Source: Existing cmd_prices pattern in cli.py
def cmd_prices(args: argparse.Namespace) -> None:
    try:
        coins = get_top_coins(top_n=args.top)
    except (httpx.HTTPStatusError, httpx.ConnectError) as e:
        print(f"Error fetching data: {e}", file=sys.stderr)
        sys.exit(1)

    # Alert checking hook
    from crypto_price_tracker.alerts_db import get_active_alerts, mark_triggered
    from crypto_price_tracker.alerts import check_alerts
    active = get_active_alerts()
    triggered = check_alerts(coins, active)
    for alert in triggered:
        mark_triggered(alert.id)

    if triggered:
        render_alert_banner(triggered)

    render_price_table(coins, triggered_symbols={a.symbol for a in triggered})
```

### Pattern 4: Web Toast Notification
**What:** CSS-only animated toast that stacks and auto-dismisses
**When to use:** Web dashboard when alerts trigger during price refresh
**Example:**
```javascript
// Source: Standard toast notification pattern (vanilla JS)
function showToast(message, type = 'alert') {
  const container = document.getElementById('toast-container')
    || (() => { const d = document.createElement('div'); d.id = 'toast-container'; document.body.appendChild(d); return d; })();
  const toast = document.createElement('div');
  toast.className = 'toast toast-' + type;
  toast.textContent = message;
  container.appendChild(toast);
  // Trigger reflow for animation
  toast.offsetHeight;
  toast.classList.add('show');
  setTimeout(() => {
    toast.classList.remove('show');
    toast.addEventListener('transitionend', () => toast.remove());
  }, 10000);
}
```

```css
/* Source: Standard toast CSS pattern */
#toast-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 200;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.toast {
  background: #161b22;
  color: #c9d1d9;
  border: 1px solid #f0883e;
  border-left: 4px solid #f0883e;
  border-radius: 4px;
  padding: 12px 16px;
  font-family: monospace;
  font-size: 0.85em;
  max-width: 350px;
  opacity: 0;
  transform: translateX(100%);
  transition: opacity 0.3s, transform 0.3s;
}
.toast.show {
  opacity: 1;
  transform: translateX(0);
}
```

### Pattern 5: Argparse Nested Subparser (Existing Pattern)
**What:** `crypto alert` subcommand group with `add`, `list`, `remove`, `check` sub-subcommands
**When to use:** CLI command registration
**Example:**
```python
# Source: Existing portfolio subcommand pattern in cli.py
alert_parser = subparsers.add_parser("alert", help="Manage price alerts")
alert_sub = alert_parser.add_subparsers(dest="alert_command")

# alert add
alert_add_parser = alert_sub.add_parser("add", help="Add a price alert")
alert_add_parser.add_argument("symbol", type=str, help="Coin symbol (e.g. BTC)")
alert_add_parser.add_argument("target_price", type=float, help="Target price in EUR")
alert_add_parser.add_argument("--above", dest="direction", action="store_const",
                               const="above", default="above", help="Alert when price goes above target (default)")
alert_add_parser.add_argument("--below", dest="direction", action="store_const",
                               const="below", help="Alert when price goes below target")

# alert list
alert_sub.add_parser("list", help="List all alerts")

# alert remove
alert_remove_parser = alert_sub.add_parser("remove", help="Remove an alert by ID")
alert_remove_parser.add_argument("id", type=int, help="Alert ID to remove")

# alert check
alert_sub.add_parser("check", help="Check alerts against current prices")
```

**Critical argparse detail:** The `--above`/`--below` flags both write to `dest="direction"`. Using `action="store_const"` with `const="above"` and `default="above"` means `--above` is the default when neither flag is given. This matches the CONTEXT.md requirement.

### Anti-Patterns to Avoid
- **Separate price fetch for alerts:** Never call `get_top_coins()` again just for alert checking. Always piggyback on the existing fetch.
- **Repeating triggered alerts in watch mode:** Mark alert as triggered in DB on first detection. On subsequent refreshes, `get_active_alerts()` will not return it.
- **Custom notification daemon:** No background processes. Alerts are purely passive, checked during existing price fetches.
- **Row factory collision:** `alerts_db.py` must use its own `_alert_factory`, not the `_holding_factory` from `portfolio_db.py`. Each module manages its own row factory.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Terminal alert box | Custom print statements | Rich Panel with border_style | Consistent styling, handles terminal width |
| Toast stacking | Manual DOM positioning | CSS flexbox column with gap | Stacking is automatic with flex-direction: column |
| Date/time formatting | Manual string building | `datetime.now().isoformat()` | ISO 8601 consistency with existing buy_date pattern |
| Direction validation | Custom if/else | SQLite CHECK constraint | DB enforces valid values even if code has bugs |

**Key insight:** This phase introduces no fundamentally new patterns. Every component mirrors an established Phase 6 pattern (DB layer, CLI subcommands, web endpoints, HTML tab). The only truly new element is toast notifications, which are ~40 lines of CSS/JS.

## Common Pitfalls

### Pitfall 1: Row Factory Collision Between Tables
**What goes wrong:** Using `portfolio_db.get_connection()` for alert queries returns `Holding` objects instead of `PriceAlert` objects because the row factory is set to `_holding_factory`.
**Why it happens:** Both tables live in the same DB file, but the connection's row factory is per-connection, not per-query.
**How to avoid:** `alerts_db.py` creates its own `get_alert_connection()` function with `_alert_factory` as the row factory. Never share connection objects between modules.
**Warning signs:** `TypeError` when accessing `.target_price` on what's actually a `Holding` object.

### Pitfall 2: Alert Repeating in Watch Mode
**What goes wrong:** The same alert fires on every refresh cycle in `crypto watch`, flooding the user with banners.
**Why it happens:** Forgetting to call `mark_triggered()` before the next loop iteration, or checking triggered status in the wrong order.
**How to avoid:** Call `mark_triggered(alert.id)` immediately after detection, before displaying. On next loop iteration, `get_active_alerts()` excludes it.
**Warning signs:** Duplicate alert banners on consecutive refreshes.

### Pitfall 3: Race Condition in Web Alert Checking
**What goes wrong:** Two concurrent `/api/prices` requests both detect the same alert, both try to mark it as triggered.
**Why it happens:** SQLite connection-per-call means no transaction spans the check-and-mark operation.
**How to avoid:** Use `UPDATE alerts SET status='triggered', triggered_at=? WHERE id=? AND status='active'` -- the `AND status='active'` guard ensures only one concurrent caller succeeds. Check `cursor.rowcount > 0` to confirm.
**Warning signs:** Duplicate toast notifications for the same alert.

### Pitfall 4: Missing Coin in Price Data
**What goes wrong:** User sets alert for a coin that drops out of top 100, alert never fires.
**Why it happens:** `get_top_coins(top_n=20)` might not include the alerted coin.
**How to avoid:** For alert checking, use the full coin list from the current fetch. In `cmd_prices`, coins are top 20, but alert checking should work within whatever was fetched. Document that alerts only fire when the coin is in the fetched set. In `cmd_watch` and `crypto alert check`, consider fetching top 100 for better coverage.
**Warning signs:** Alert stays active forever despite price crossing threshold.

### Pitfall 5: `--above`/`--below` Flag Conflict in argparse
**What goes wrong:** Both flags specified, argparse silently uses the last one.
**Why it happens:** `action="store_const"` with same `dest` -- last flag wins.
**How to avoid:** This is actually acceptable behavior. Document that last flag wins if both specified. Alternatively, use a mutually exclusive group.
**Warning signs:** User confusion when `--above --below` does not error.

## Code Examples

### PriceAlert Dataclass (models.py)
```python
# Source: Existing CoinData/Holding pattern in models.py
@dataclass(slots=True)
class PriceAlert:
    """A price alert for a cryptocurrency.

    Fields:
        id:            SQLite row ID (autoincrement primary key)
        symbol:        Coin ticker symbol (e.g. "BTC"), stored uppercase
        target_price:  Target price in EUR
        direction:     "above" or "below"
        status:        "active" or "triggered"
        created_at:    Creation timestamp as ISO 8601 string
        triggered_at:  Trigger timestamp as ISO 8601 string, or None
    """
    id: int
    symbol: str
    target_price: float
    direction: str
    status: str
    created_at: str
    triggered_at: str | None
```

### Rich Panel for Alert Banner (display.py)
```python
# Source: Rich Panel docs (https://rich.readthedocs.io/en/stable/panel.html)
from rich.panel import Panel

def render_alert_banner(
    triggered: list[PriceAlert],
    console: Console | None = None,
) -> None:
    """Render a warning banner for triggered alerts."""
    if console is None:
        console = Console()
    lines = []
    for a in triggered:
        arrow = "above" if a.direction == "above" else "below"
        lines.append(f"[bold yellow]\\u26a0[/bold yellow] {a.symbol} hit EUR {a.target_price:,.2f} ({arrow} target)")
    text = "\\n".join(lines)
    console.print(Panel(text, title="[bold yellow]ALERTS TRIGGERED[/bold yellow]",
                        border_style="yellow", expand=True))
```

### Inline Marker on Price Table Row (display.py modification)
```python
# Source: Existing render_price_table pattern
def render_price_table(
    coins: list[CoinData],
    console: Console | None = None,
    triggered_symbols: set[str] | None = None,
) -> None:
    """Render price table with optional alert markers."""
    if console is None:
        console = Console()
    if triggered_symbols is None:
        triggered_symbols = set()

    # ... existing table setup ...
    for rank, coin in enumerate(coins, start=1):
        symbol_str = coin.symbol
        if coin.symbol in triggered_symbols:
            symbol_str = f"[bold yellow]\\u26a0 {coin.symbol}[/bold yellow]"
        # ... rest of row rendering with symbol_str ...
```

### Web API Endpoints (web.py)
```python
# Source: Existing portfolio endpoint patterns in web.py
class AlertCreate(BaseModel):
    """Request body for creating a new alert."""
    symbol: str
    target_price: float = Field(gt=0)
    direction: str = Field(default="above", pattern="^(above|below)$")

@app.get("/api/alerts")
def api_alerts():
    """Return all alerts grouped by status."""
    alerts = get_all_alerts()
    return [dataclasses.asdict(a) for a in alerts]

@app.post("/api/alerts", status_code=201)
def api_alerts_add(body: AlertCreate):
    """Create a new price alert."""
    alert_id = add_alert(body.symbol, body.target_price, body.direction)
    return {"id": alert_id, "status": "created"}

@app.delete("/api/alerts/{alert_id}")
def api_alerts_delete(alert_id: int):
    """Remove an alert by ID."""
    if not remove_alert(alert_id):
        raise HTTPException(status_code=404, detail=f"Alert #{alert_id} not found")
    return {"status": "deleted"}

@app.delete("/api/alerts/triggered")
def api_alerts_clear_triggered():
    """Remove all triggered alerts."""
    count = clear_triggered_alerts()
    return {"status": "cleared", "count": count}
```

### Web Alert Checking (integrated into /api/prices)
```python
# Source: Existing /api/prices pattern
@app.get("/api/prices")
def api_prices(top: int = Query(default=20, ge=1, le=100)):
    """Return top N coins with triggered alerts flagged."""
    coins = get_top_coins(top_n=top)
    # Check alerts passively
    active = get_active_alerts()
    triggered_alerts = check_alerts(coins, active)
    for alert in triggered_alerts:
        mark_triggered(alert.id)
    result = [dataclasses.asdict(c) for c in coins]
    if triggered_alerts:
        # Append triggered alerts to response for toast display
        result = {
            "coins": result,
            "triggered_alerts": [dataclasses.asdict(a) for a in triggered_alerts],
        }
    else:
        result = {"coins": result, "triggered_alerts": []}
    return result
```

**Important API change:** The `/api/prices` response shape changes from a bare array to `{"coins": [...], "triggered_alerts": [...]}`. The frontend `load()` function must be updated to read `data.coins` instead of `data` directly.

### Alerts Tab HTML Structure
```html
<!-- Source: Existing tab pattern in index.html -->
<div id="tab-alerts" class="tab-content" style="display:none;">
  <form class="portfolio-form" onsubmit="addAlert(event)">
    <label>Coin
      <select id="alert-symbol" required>
        <option value="">Select...</option>
      </select>
    </label>
    <label>Target Price
      <input type="number" id="alert-price" required step="any" min="0.01" placeholder="100000">
    </label>
    <label>Direction
      <select id="alert-direction">
        <option value="above">Above</option>
        <option value="below">Below</option>
      </select>
    </label>
    <button type="submit">+ Add Alert</button>
  </form>
  <div class="form-msg" id="alert-msg"></div>

  <h3 style="color:#58a6ff;margin:16px 0 8px;">Active Alerts</h3>
  <table id="alerts-active-table">
    <thead>
      <tr><th>ID</th><th>Symbol</th><th>Target</th><th>Direction</th><th>Created</th><th></th></tr>
    </thead>
    <tbody id="alerts-active-tbody"></tbody>
  </table>

  <h3 style="color:#8b949e;margin:16px 0 8px;">Triggered Alerts</h3>
  <table id="alerts-triggered-table">
    <thead>
      <tr><th>ID</th><th>Symbol</th><th>Target</th><th>Direction</th><th>Triggered</th><th></th></tr>
    </thead>
    <tbody id="alerts-triggered-tbody"></tbody>
  </table>
  <button id="clear-triggered-btn" onclick="clearTriggered()" style="display:none;">Clear All Triggered</button>
</div>
```

### Coin Dropdown Population Strategy
```javascript
// Source: Project pattern -- populate from /api/prices data already fetched
function populateAlertDropdown(coins) {
  const select = document.getElementById('alert-symbol');
  // Keep first "Select..." option, remove rest
  while (select.options.length > 1) select.remove(1);
  coins.forEach(c => {
    const opt = document.createElement('option');
    opt.value = c.symbol;
    opt.textContent = c.symbol + ' - ' + c.name;
    select.appendChild(opt);
  });
}
// Called inside load() after prices are fetched
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| External toast libraries | Inline CSS/JS toast | Always viable for simple cases | Zero dependency cost |
| Separate alert DB file | Same DB, separate table | N/A (design choice) | One fewer file to manage |
| Browser Notification API | Visual-only toast | User decision | No permission prompts, simpler UX |

**Deprecated/outdated:**
- None applicable -- all patterns in this phase use stable, mature APIs.

## Open Questions

1. **Should `crypto alert check` fetch top 100 for better coverage?**
   - What we know: `cmd_prices` fetches top 20, some alerted coins may not be in top 20
   - What's unclear: Whether users expect alerts on coins outside their normal view
   - Recommendation: `crypto alert check` should fetch top 100 (same as `cmd_info`). `cmd_prices` and `cmd_watch` check within whatever was fetched (top_n from `--top` flag). Document this behavior.

2. **Should the `/api/prices` response format change be backwards-compatible?**
   - What we know: Changing from array to `{"coins": [...], "triggered_alerts": [...]}` breaks existing frontend code
   - What's unclear: Whether any external consumers depend on the current format
   - Recommendation: Just change it. This is an internal API, and the frontend is updated in the same plan. No external consumers exist.

3. **Mutually exclusive `--above`/`--below` flags?**
   - What we know: argparse `add_mutually_exclusive_group` would enforce at most one
   - What's unclear: Whether the complexity is worth it
   - Recommendation: Use mutually exclusive group for correctness. It is two lines of code.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8.0+ |
| Config file | pyproject.toml (implicit discovery) |
| Quick run command | `uv run pytest tests/ -x -q` |
| Full suite command | `uv run pytest tests/ -v` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| ALERT-01 | SQLite CRUD: add, get, remove, mark_triggered, clear_triggered | unit | `uv run pytest tests/test_alerts_db.py -x` | No -- Wave 0 |
| ALERT-02 | Alert checking logic: above/below triggers | unit | `uv run pytest tests/test_alerts.py -x` | No -- Wave 0 |
| ALERT-03 | CLI subcommands: add, list, remove, check | unit | `uv run pytest tests/test_cli.py -x -k alert` | No -- Wave 0 |
| ALERT-04 | Web API endpoints: GET/POST/DELETE /api/alerts | unit | `uv run pytest tests/test_web.py -x -k alert` | No -- Wave 0 |
| ALERT-05 | Rich banner and inline markers render correctly | unit | `uv run pytest tests/test_display.py -x -k alert` | No -- Wave 0 |
| ALERT-06 | Web HTML has alerts tab, toast container, form | smoke | `uv run pytest tests/test_web.py -x -k "alert and html"` | No -- Wave 0 |
| ALERT-07 | `crypto alert check` exit code semantics | unit | `uv run pytest tests/test_cli.py -x -k "alert_check_exit"` | No -- Wave 0 |

### Sampling Rate
- **Per task commit:** `uv run pytest tests/ -x -q`
- **Per wave merge:** `uv run pytest tests/ -v`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_alerts_db.py` -- SQLite CRUD for alerts table
- [ ] `tests/test_alerts.py` -- Alert checking logic (pure function tests)
- [ ] Additional tests in `tests/test_cli.py` -- alert subcommand tests
- [ ] Additional tests in `tests/test_web.py` -- alert API endpoint tests
- [ ] Additional tests in `tests/test_display.py` -- alert banner rendering tests

## Sources

### Primary (HIGH confidence)
- Project codebase: `portfolio_db.py`, `cli.py`, `web.py`, `display.py`, `models.py`, `static/index.html` -- all patterns verified by direct code reading
- Rich Panel docs: https://rich.readthedocs.io/en/stable/panel.html -- Panel constructor params verified
- Rich 13.7.1 installed locally -- `Panel.__init__` signature verified via `help()`

### Secondary (MEDIUM confidence)
- Toast notification patterns from CSS Script and DEV Community articles -- standard vanilla JS/CSS approach, no library needed

### Tertiary (LOW confidence)
- None -- all findings verified against primary sources

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- no new dependencies, all libraries already in use
- Architecture: HIGH -- every pattern mirrors existing Phase 6 implementation
- Pitfalls: HIGH -- identified from direct code analysis of existing patterns
- Toast notifications: MEDIUM -- standard web pattern, but implementation details are discretionary

**Research date:** 2026-03-06
**Valid until:** 2026-04-06 (stable -- no fast-moving dependencies)
