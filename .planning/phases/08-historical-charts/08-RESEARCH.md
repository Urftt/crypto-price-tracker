# Phase 8: Historical Charts - Research

**Researched:** 2026-03-06
**Domain:** Bitvavo candles API, Unicode sparklines, Plotly.js charting, CLI/web integration
**Confidence:** HIGH

## Summary

Phase 8 adds historical price charts to both the CLI (`crypto chart` / `crypto chart BTC`) and the web dashboard (Plotly chart in coin detail modal). The Bitvavo candles endpoint has been verified working via live API calls and returns `[timestamp_ms, open, high, low, close, volume]` arrays with all numeric values as strings except timestamp. The sparkline rendering algorithm is well-established (8 Unicode block characters mapped linearly from min to max) and trivial to implement inline without external dependencies. Plotly.js v3.4.0 is loaded from CDN with a single `<script>` tag.

The codebase follows clear, consistent patterns: `BitvavoClient` with httpx and context manager in `api.py`, argparse subcommands dispatched via if/elif in `cli.py`, Rich tables with console injection in `display.py`, FastAPI factory pattern in `web.py`, and `@dataclass(slots=True)` models. All tests mock HTTP calls with `pytest-httpx` or `unittest.mock.patch`. This phase touches all layers but adds no new dependencies beyond the Plotly CDN script tag in the HTML file.

**Primary recommendation:** Split into two plans -- Plan 1 for backend (API candle method + Candle model + sparkline rendering + CLI `chart` subcommand) and Plan 2 for web (candle API endpoint + Plotly chart in modal + 7D/30D toggle).

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
1. CLI Chart Output: Two modes -- `crypto chart` (all top 20 with sparklines) and `crypto chart BTC` (single coin detail with sparkline + stats). Both timeframes always shown (7d + 30d), no --period flag. Sparkline style: Unicode block characters. Stats color-coded green/red. No inline sparklines in `crypto prices` table.
2. Web Chart Placement & Interaction: In the coin detail modal (not a new tab). Line chart (closing prices), no candlestick. 7D/30D toggle above chart, default 7D. Plotly loaded from CDN.
3. Candle Granularity: 7-day uses 4h candles (limit=42, ~42 points), 30-day uses 1d candles (limit=30, 30 points). Bitvavo endpoint: `GET /{market}/candles?interval=X&limit=N`. Response newest-first, must reverse for chronological order.
4. Multi-Coin Performance: Sequential fetching for all top 20, one candle request per coin. Progress indicator while loading. No caching, no parallel requests.

### Claude's Discretion
- Sparkline rendering algorithm (mapping close prices to 8 unicode block levels)
- Exact Rich table layout for the sparkline overview table
- Plotly chart configuration (colors, hover tooltips, axis formatting, responsive sizing)
- New `candles` method on `BitvavoClient` or standalone function
- API endpoint design for candle data (`/api/candles/{symbol}?interval=4h&limit=42`)
- Error handling for coins with insufficient candle data
- Progress indicator implementation (Rich spinner, print, or status)

### Deferred Ideas (OUT OF SCOPE)
None captured during discussion.
</user_constraints>

## Bitvavo Candles API (Verified via Live Calls)

**Confidence: HIGH** -- verified with actual API requests on 2026-03-06.

### Endpoint

```
GET https://api.bitvavo.com/v2/{market}/candles?interval={interval}&limit={limit}
```

- **Public endpoint**, no authentication required
- Uses the same base URL as existing `BitvavoClient`: `https://api.bitvavo.com/v2`
- Market format: `{SYMBOL}-EUR` (e.g., `BTC-EUR`)

### Parameters

| Parameter | Values | Usage in This Phase |
|-----------|--------|---------------------|
| `interval` | `1m`, `5m`, `15m`, `30m`, `1h`, `2h`, `4h`, `6h`, `8h`, `12h`, `1d` | `4h` for 7-day, `1d` for 30-day |
| `limit` | integer (must be > 0) | `42` for 7-day, `30` for 30-day |

### Response Format (Verified)

```json
[
    [1772827200000, "58756", "58869", "58453", "58805", "78.41325347"],
    [1772812800000, "59191", "59408", "58448", "58750", "303.32466827"]
]
```

Each candle is an array of 6 elements:

| Index | Field | Type | Description |
|-------|-------|------|-------------|
| 0 | timestamp | `int` (milliseconds) | Unix timestamp in ms |
| 1 | open | `str` | Opening price |
| 2 | high | `str` | Highest price in interval |
| 3 | low | `str` | Lowest price in interval |
| 4 | close | `str` | Closing price |
| 5 | volume | `str` | Volume traded in interval |

**Key observations from live testing:**
- Returns **newest-first** -- must reverse for chronological sparkline rendering
- All numeric values except timestamp are **strings** -- must convert to `float`
- `limit=42` with `interval=4h` returns exactly 42 candles spanning ~7 days
- `limit=30` with `interval=1d` returns exactly 30 candles spanning ~30 days
- Invalid market returns HTTP 400: `{"errorCode": 205, "error": "market parameter is invalid."}`
- Invalid limit (0 or negative) returns HTTP 400: `{"errorCode": 205, "error": "limit parameter is invalid."}`

### Integration with BitvavoClient

Add a `get_candles()` method to `BitvavoClient`:

```python
def get_candles(self, market: str, interval: str = "4h", limit: int = 42) -> list[Candle]:
    """Fetch OHLCV candles for a market, returned in chronological order."""
    response = self._client.get(
        f"{BASE_URL}/{market}/candles",
        params={"interval": interval, "limit": limit},
    )
    response.raise_for_status()
    raw: list[list] = response.json()
    candles = [
        Candle(
            timestamp=entry[0],
            open=float(entry[1]),
            high=float(entry[2]),
            low=float(entry[3]),
            close=float(entry[4]),
            volume=float(entry[5]),
        )
        for entry in raw
    ]
    candles.reverse()  # API returns newest-first; we want chronological
    return candles
```

Also add a module-level convenience function (following existing `get_top_coins` pattern):

```python
def get_candles(market: str, interval: str = "4h", limit: int = 42) -> list[Candle]:
    """Convenience wrapper that opens a client, fetches candles, and closes."""
    with BitvavoClient() as client:
        return client.get_candles(market, interval, limit)
```

## Candle Data Model

Add to `models.py` following the existing `@dataclass(slots=True)` pattern:

```python
@dataclass(slots=True)
class Candle:
    """A single OHLCV candle from the Bitvavo candles endpoint.

    Fields:
        timestamp: Unix timestamp in milliseconds
        open:      Opening price in EUR
        high:      Highest price in interval
        low:       Lowest price in interval
        close:     Closing price in EUR
        volume:    Volume traded in the interval
    """
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float
```

## Sparkline Rendering Algorithm

**Confidence: HIGH** -- well-established algorithm from Rosetta Code and multiple implementations.

### Algorithm

The 8 Unicode block characters are: `\u2581\u2582\u2583\u2584\u2585\u2586\u2587\u2588` (displayed as `........`)

```python
SPARK_CHARS = "\u2581\u2582\u2583\u2584\u2585\u2586\u2587\u2588"

def sparkline(values: list[float]) -> str:
    """Convert a list of numeric values to a Unicode sparkline string."""
    if not values:
        return ""
    mn = min(values)
    mx = max(values)
    if mn == mx:
        # All values identical -- render as mid-height bars
        return SPARK_CHARS[3] * len(values)
    extent = mx - mn
    return "".join(
        SPARK_CHARS[min(7, int((v - mn) / extent * 8))]
        for v in values
    )
```

### Recommendation: Custom Implementation (No External Library)

The `sparklines` PyPI package (v0.7.0) exists but adds an unnecessary dependency for ~10 lines of code. The algorithm is trivial and well-understood. Custom implementation is the correct choice here because:

1. The algorithm is 5 lines of logic
2. No edge cases beyond flat data (handled by `mn == mx` check)
3. No dependency management overhead
4. Full control over the output format

### Edge Cases to Handle

| Case | Handling |
|------|----------|
| Empty candle list | Return empty string |
| All prices identical | Return mid-height bars (index 3) |
| Single candle | Return single mid-height bar |
| Very small price range | Algorithm handles naturally (linear scaling) |

### Usage in Display

Extract closing prices from candles, then render:

```python
def render_sparkline(candles: list[Candle]) -> str:
    """Generate a sparkline string from candle closing prices."""
    closes = [c.close for c in candles]
    return sparkline(closes)
```

## CLI Chart Command Design

### `crypto chart` (All Coins Overview)

Rich table with columns: #, Symbol, 7d Sparkline, 30d Sparkline

```python
def render_chart_table(
    coins: list[CoinData],
    sparklines_7d: dict[str, str],
    sparklines_30d: dict[str, str],
    console: Console | None = None,
) -> None:
    table = Table(title="Price Charts (EUR)", show_lines=False)
    table.add_column("#", justify="right", style="dim")
    table.add_column("Symbol", justify="left", style="bold")
    table.add_column("7d", justify="left")
    table.add_column("30d", justify="left")
    for rank, coin in enumerate(coins, start=1):
        table.add_row(
            str(rank),
            coin.symbol,
            sparklines_7d.get(coin.symbol, ""),
            sparklines_30d.get(coin.symbol, ""),
        )
    console.print(table)
```

### `crypto chart BTC` (Single Coin Detail)

Show sparklines for both timeframes plus stats (open, close, high, low, change %):

```python
def render_chart_detail(
    coin: CoinData,
    candles_7d: list[Candle],
    candles_30d: list[Candle],
    console: Console | None = None,
) -> None:
    # Header
    console.print(f"\n[bold]{coin.symbol}[/bold] -- {coin.name}\n")

    for label, candles in [("7-Day", candles_7d), ("30-Day", candles_30d)]:
        if not candles:
            console.print(f"  {label}: No data available")
            continue
        spark = sparkline([c.close for c in candles])
        o, c = candles[0].open, candles[-1].close
        hi = max(c_.high for c_ in candles)
        lo = min(c_.low for c_ in candles)
        change = ((c - o) / o) * 100 if o else 0

        console.print(f"  [bold]{label}[/bold]  {spark}")
        change_str = f"{change:+.2f}%"
        color = "green" if change >= 0 else "red"
        console.print(f"    Open: EUR {o:,.2f}  Close: EUR {c:,.2f}  High: EUR {hi:,.2f}  Low: EUR {lo:,.2f}  Change: [{color}]{change_str}[/{color}]")
```

### Progress Indicator

Use `rich.console.Console.status()` for the loading spinner during multi-coin fetch:

```python
with console.status("Fetching chart data..."):
    for coin in coins:
        market = f"{coin.symbol}-EUR"
        try:
            candles_7d = get_candles(market, interval="4h", limit=42)
            candles_30d = get_candles(market, interval="1d", limit=30)
        except httpx.HTTPStatusError:
            candles_7d, candles_30d = [], []
        sparklines_7d[coin.symbol] = sparkline([c.close for c in candles_7d])
        sparklines_30d[coin.symbol] = sparkline([c.close for c in candles_30d])
```

## Plotly CDN Integration

**Confidence: HIGH** -- verified via official Plotly documentation.

### CDN URL

```html
<script src="https://cdn.plot.ly/plotly-3.4.0.min.js" charset="utf-8"></script>
```

**Important:** Do NOT use `plotly-latest.min.js` -- it is frozen at v1.58.5 and will never be updated. Always use an explicit version number.

### Minimal Line Chart Configuration

```javascript
async function loadChart(symbol, interval, limit) {
    const resp = await fetch(`/api/candles/${symbol}?interval=${interval}&limit=${limit}`);
    if (!resp.ok) return;
    const candles = await resp.json();

    const trace = {
        x: candles.map(c => new Date(c.timestamp)),
        y: candles.map(c => c.close),
        type: 'scatter',
        mode: 'lines',
        line: { color: '#58a6ff', width: 2 },
        hovertemplate: '%{x|%b %d, %H:%M}<br>EUR %{y:,.2f}<extra></extra>'
    };

    const layout = {
        paper_bgcolor: '#161b22',
        plot_bgcolor: '#161b22',
        font: { color: '#c9d1d9', family: 'monospace' },
        xaxis: {
            gridcolor: '#21262d',
            tickformat: interval === '1d' ? '%b %d' : '%b %d %H:%M'
        },
        yaxis: {
            gridcolor: '#21262d',
            tickprefix: '\u20ac ',
            tickformat: ',.2f'
        },
        margin: { t: 10, r: 20, b: 40, l: 70 },
        height: 250
    };

    const config = { responsive: true, displayModeBar: false };
    Plotly.newPlot('chart-container', [trace], layout, config);
}
```

### Dark Theme Colors (Matching Existing Dashboard)

| Element | Color | Source |
|---------|-------|--------|
| Background | `#161b22` | Modal card background |
| Grid lines | `#21262d` | Border color from existing CSS |
| Line color | `#58a6ff` | Accent color (links, symbol highlights) |
| Text color | `#c9d1d9` | Main body text |
| Positive change | `#3fb950` | Existing `.up` class |
| Negative change | `#f85149` | Existing `.down` class |

### 7D / 30D Toggle Buttons

Follow existing `.tab-btn` styling from the dashboard:

```html
<div id="chart-section" style="margin-top:16px; display:none;">
    <div style="display:flex; gap:4px; margin-bottom:8px;">
        <button class="chart-period-btn active" onclick="switchPeriod('7d')">7D</button>
        <button class="chart-period-btn" onclick="switchPeriod('30d')">30D</button>
    </div>
    <div id="chart-container" style="width:100%; height:250px;"></div>
</div>
```

### Modal Card Width Adjustment

The existing modal card has `max-width: 400px`. With Plotly charts, this should expand to `max-width: 600px` to give the chart adequate width.

## Web API Endpoint Design

### Recommended Endpoint

```
GET /api/candles/{symbol}?interval=4h&limit=42
```

Default values: `interval=4h`, `limit=42` (matching 7-day default).

### FastAPI Implementation

```python
@app.get("/api/candles/{symbol}")
def api_candles(
    symbol: str,
    interval: str = Query(default="4h", pattern="^(1m|5m|15m|30m|1h|2h|4h|6h|8h|12h|1d)$"),
    limit: int = Query(default=42, ge=1, le=1440),
):
    """Return OHLCV candle data for a market."""
    symbol = symbol.upper()
    market = f"{symbol}-EUR"
    try:
        candles = get_candles(market, interval=interval, limit=limit)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 400:
            raise HTTPException(status_code=404, detail=f"No candle data for {symbol}")
        raise
    return [dataclasses.asdict(c) for c in candles]
```

## Architecture Patterns

### Project Structure (Files to Modify/Create)

```
src/crypto_price_tracker/
    api.py          # ADD: get_candles() method on BitvavoClient + convenience function
    models.py       # ADD: Candle dataclass
    display.py      # ADD: sparkline(), render_chart_table(), render_chart_detail()
    cli.py          # ADD: cmd_chart() + chart subparser
    web.py          # ADD: /api/candles/{symbol} endpoint
    static/
        index.html  # ADD: Plotly CDN script, chart section in modal, toggle buttons
tests/
    test_api.py     # ADD: test_get_candles_* tests
    test_display.py # ADD: test_sparkline_*, test_render_chart_* tests
    test_cli.py     # ADD: test_chart_command_* tests
    test_web.py     # ADD: test_api_candles_* tests
```

### Pattern: Existing Codebase Conventions

| Convention | How It Works | Apply To Phase 8 |
|------------|-------------|-------------------|
| **HTTP mocking** | `pytest-httpx` with `httpx_mock.add_response(url=..., json=...)` | Mock candle endpoint responses |
| **CLI testing** | `patch("crypto_price_tracker.cli.func_name")` + `sys.argv` setting | Mock `get_candles`, verify render calls |
| **Display testing** | `Console(file=buf, force_terminal=True, color_system="truecolor")` | Capture sparkline/chart table output |
| **Web testing** | `TestClient(create_app())` + `patch("crypto_price_tracker.web.func")` | Test `/api/candles/{symbol}` endpoint |
| **Error handling** | `httpx.HTTPStatusError`, `httpx.ConnectError` caught in CLI | Catch same errors for candle fetching |
| **DB isolation** | `portfolio_db` fixture redirects DB path | Not needed for candles (no DB) |

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Interactive web charts | Custom SVG/Canvas rendering | Plotly.js from CDN | Handles hover, zoom, responsive sizing, date formatting |
| Unicode sparklines | Custom character encoding | Standard algorithm (8 block chars, linear mapping) | 5-line algorithm, well-established, no library needed |
| HTTP client | `requests` or `urllib` | `httpx` (already in use) | Consistent with existing `BitvavoClient` |
| CLI argument parsing | Click or Typer | `argparse` (already in use) | Consistent with existing CLI structure |

## Common Pitfalls

### Pitfall 1: Candle Data Ordering
**What goes wrong:** Rendering sparklines with newest-first data produces reversed charts (price goes from present to past).
**Why it happens:** Bitvavo returns candles newest-first by default.
**How to avoid:** Always `reverse()` the candle list immediately after fetching, before any rendering.
**Warning signs:** Charts that look like mirror images of actual price movement.

### Pitfall 2: String-to-Float Conversion
**What goes wrong:** Treating candle OHLCV values as numbers directly causes TypeError.
**Why it happens:** Bitvavo returns all values as strings except the timestamp.
**How to avoid:** Convert to `float()` during `Candle` dataclass construction in the API layer.
**Warning signs:** `TypeError: '<' not supported between instances of 'str' and 'str'` when computing min/max.

### Pitfall 3: Division by Zero in Sparkline
**What goes wrong:** `ZeroDivisionError` when all candle close prices are identical.
**Why it happens:** `extent = max - min = 0`, then dividing by zero.
**How to avoid:** Check `mn == mx` and return uniform bars.
**Warning signs:** Crash on stablecoins (USDT, USDC) or very low-volatility periods.

### Pitfall 4: Plotly CDN Version
**What goes wrong:** Using `plotly-latest.min.js` loads v1.58.5, which is 5+ years old and missing modern features.
**Why it happens:** Plotly froze the "latest" CDN URL at v1 and never updated it.
**How to avoid:** Always use explicit version: `plotly-3.4.0.min.js`.
**Warning signs:** Missing features, different API, visual inconsistencies.

### Pitfall 5: Modal Width Too Narrow for Charts
**What goes wrong:** Plotly chart is squished and unreadable at 400px width.
**Why it happens:** Existing modal `max-width: 400px` was designed for text-only coin detail.
**How to avoid:** Increase modal `max-width` to `600px` when chart is present.
**Warning signs:** Overlapping axis labels, truncated chart.

### Pitfall 6: Sequential API Calls Timeout
**What goes wrong:** Fetching 40 candle requests (20 coins x 2 timeframes) may timeout the httpx client.
**Why it happens:** Each request takes ~100-300ms, total ~4-12 seconds, but individual request timeout is 10s.
**How to avoid:** The 10s per-request timeout is fine since each call is independent. Total wall time is just sequential sum. Show a progress indicator so the user knows it is working.
**Warning signs:** Occasional `httpx.TimeoutException` on slow connections.

### Pitfall 7: Non-EUR Coins in Candle Fetch
**What goes wrong:** A coin in the top 20 might not have a `-EUR` market on Bitvavo for candles.
**Why it happens:** Some coins only have BTC or USDT pairs.
**How to avoid:** Already handled by existing `get_top_coins()` which filters to EUR pairs only. Candle fetch uses `{symbol}-EUR`, so this should always work. Add a try/except for safety.
**Warning signs:** 400 errors from Bitvavo for invalid market.

## Code Examples

### Full Sparkline Module (Recommended Implementation)

```python
# In display.py

SPARK_CHARS = "\u2581\u2582\u2583\u2584\u2585\u2586\u2587\u2588"


def sparkline(values: list[float]) -> str:
    """Convert numeric values to a Unicode sparkline string.

    Maps values linearly across 8 Unicode block characters (U+2581..U+2588).
    Returns empty string for empty input, uniform bars for constant values.
    """
    if not values:
        return ""
    mn, mx = min(values), max(values)
    if mn == mx:
        return SPARK_CHARS[3] * len(values)
    extent = mx - mn
    return "".join(
        SPARK_CHARS[min(7, int((v - mn) / extent * 8))]
        for v in values
    )
```

### CLI Subcommand Registration Pattern

```python
# In cli.py, within main():

# chart subcommand
chart_parser = subparsers.add_parser("chart", help="Show price history charts")
chart_parser.add_argument(
    "symbol",
    type=str,
    nargs="?",
    default=None,
    help="Coin symbol (e.g. BTC). Omit for all top 20.",
)
```

### Candle Mock for Tests

```python
# In test_api.py

BITVAVO_CANDLES_URL = "https://api.bitvavo.com/v2/BTC-EUR/candles"

def make_candle(ts: int, open_: str, high: str, low: str, close: str, vol: str) -> list:
    return [ts, open_, high, low, close, vol]

def test_get_candles_returns_chronological(httpx_mock: HTTPXMock) -> None:
    """Candles should be returned in chronological order (oldest first)."""
    raw = [
        make_candle(3000, "103", "105", "101", "104", "10"),
        make_candle(2000, "101", "103", "100", "102", "20"),
        make_candle(1000, "100", "102", "99", "101", "30"),
    ]
    httpx_mock.add_response(url=BITVAVO_CANDLES_URL, json=raw)

    with BitvavoClient() as client:
        candles = client.get_candles("BTC-EUR", interval="4h", limit=3)

    assert len(candles) == 3
    assert candles[0].timestamp == 1000  # oldest first
    assert candles[-1].timestamp == 3000  # newest last
    assert candles[0].close == 101.0
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `plotly-latest.min.js` | Explicit version `plotly-3.4.0.min.js` | Plotly v2+ (2021) | Must pin version in CDN URL |
| Plotly v2.x | Plotly v3.4.0 | 2025 | New default export format, same `newPlot` API |
| `sparklines` PyPI package | Custom 5-line function | N/A | Avoids dependency for trivial logic |

## Recommended Plan Breakdown

### Plan 08-01: Backend + CLI (Chart Data & Terminal Rendering)
- Add `Candle` dataclass to `models.py`
- Add `get_candles()` to `BitvavoClient` in `api.py` + convenience function
- Add `sparkline()`, `render_chart_table()`, `render_chart_detail()` to `display.py`
- Add `cmd_chart()` and `chart` subparser to `cli.py`
- Add tests: `test_api.py` (candle fetching), `test_display.py` (sparkline rendering), `test_cli.py` (chart subcommand)

### Plan 08-02: Web Dashboard (Plotly Charts in Modal)
- Add `/api/candles/{symbol}` endpoint to `web.py`
- Add Plotly CDN `<script>` tag to `index.html`
- Add chart section with 7D/30D toggle to coin detail modal
- Add `loadChart()` and `switchPeriod()` JavaScript functions
- Widen modal card to accommodate chart
- Add CSS for chart period buttons
- Add tests: `test_web.py` (candle endpoint), HTML content tests

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8.0+ with pytest-httpx 0.35+ |
| Config file | `pyproject.toml` [tool.hatch] / default pytest discovery |
| Quick run command | `uv run pytest tests/ -x -q` |
| Full suite command | `uv run pytest tests/ -v` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| CHART-01 | Candle data fetched from Bitvavo API | unit | `uv run pytest tests/test_api.py::test_get_candles_returns_chronological -x` | No -- Wave 0 |
| CHART-02 | Sparkline renders correctly from price values | unit | `uv run pytest tests/test_display.py::test_sparkline_basic -x` | No -- Wave 0 |
| CHART-03 | `crypto chart` renders overview table for all coins | unit | `uv run pytest tests/test_cli.py::test_chart_command_all_coins -x` | No -- Wave 0 |
| CHART-04 | `crypto chart BTC` renders single coin detail | unit | `uv run pytest tests/test_cli.py::test_chart_command_single_coin -x` | No -- Wave 0 |
| CHART-05 | `/api/candles/{symbol}` returns candle JSON | unit | `uv run pytest tests/test_web.py::test_api_candles_returns_json -x` | No -- Wave 0 |
| CHART-06 | Web modal shows Plotly chart with toggle | smoke | `uv run pytest tests/test_web.py::test_index_has_chart_elements -x` | No -- Wave 0 |

### Sampling Rate
- **Per task commit:** `uv run pytest tests/ -x -q`
- **Per wave merge:** `uv run pytest tests/ -v`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_api.py` -- add `test_get_candles_*` tests (candle fetching, chronological order, error handling)
- [ ] `tests/test_display.py` -- add `test_sparkline_*` tests (basic, edge cases, empty, constant values)
- [ ] `tests/test_cli.py` -- add `test_chart_command_*` tests (all coins, single coin, not found)
- [ ] `tests/test_web.py` -- add `test_api_candles_*` tests (endpoint, params, 404) and `test_index_has_chart_elements`

## Open Questions

1. **Plotly chart height in modal**
   - What we know: 250px is a reasonable default for the modal width
   - What's unclear: Whether 250px is enough vertical space alongside existing coin detail fields
   - Recommendation: Start with 250px, easy to adjust in CSS

2. **Rate limiting on Bitvavo candle endpoint**
   - What we know: Public endpoint, no auth required, sequential calls at ~100-300ms each
   - What's unclear: Whether 40 rapid sequential requests (20 coins x 2 timeframes) will trigger rate limiting
   - Recommendation: Accept the risk for now. If rate-limited, add a small `time.sleep(0.1)` between requests. The progress indicator makes the delay user-friendly.

## Sources

### Primary (HIGH confidence)
- **Bitvavo candles endpoint** -- verified via live `curl` requests to `https://api.bitvavo.com/v2/BTC-EUR/candles` on 2026-03-06, confirmed response format, ordering, data types, and error responses
- **Plotly.js official docs** -- https://plotly.com/javascript/getting-started/ confirmed CDN URL `https://cdn.plot.ly/plotly-3.4.0.min.js` and line chart API
- **Plotly.js line charts** -- https://plotly.com/javascript/line-charts/ verified `Plotly.newPlot()` trace and layout configuration
- **Rosetta Code sparkline** -- https://rosettacode.org/wiki/Sparkline_in_unicode verified algorithm for 8 Unicode block characters
- **Existing codebase** -- all source files in `src/crypto_price_tracker/` and `tests/` read and analyzed

### Secondary (MEDIUM confidence)
- **sparklines PyPI** -- https://pypi.org/project/sparklines/ reviewed as alternative, decided against adding dependency
- **Plotly.js GitHub** -- https://github.com/plotly/plotly.js/ confirmed v3.4.0 as latest

### Tertiary (LOW confidence)
- None -- all findings verified with primary sources

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all libraries already in use (httpx, Rich, FastAPI), Plotly CDN verified
- Architecture: HIGH -- follows exact patterns from existing codebase
- Pitfalls: HIGH -- verified via live API testing and code analysis
- Sparkline algorithm: HIGH -- verified via Rosetta Code and multiple implementations

**Research date:** 2026-03-06
**Valid until:** 2026-04-05 (stable domain, pinned Plotly version)
