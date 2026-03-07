# Phase 9: React Frontend - Research

**Researched:** 2026-03-07
**Domain:** Vite + React + Tailwind CSS frontend, FastAPI SSE integration, Recharts, React Router
**Confidence:** HIGH

## Summary

This phase replaces the monolithic 814-line `index.html` with a proper Vite + React + Tailwind CSS 4 application. The existing FastAPI backend (web.py) stays unchanged except for adding one SSE endpoint (`/api/prices/stream`) and updating the static file serving to support SPA routing. All existing API endpoints remain as-is.

The frontend stack is mature and well-documented: Vite 7.x for build tooling, React 19 for UI, Tailwind CSS 4.x with the `@tailwindcss/vite` plugin for styling (CSS-first config, no `tailwind.config.js`), Recharts 3.x for line charts, and React Router 7.x for client-side routing. FastAPI 0.135.1 (already installed) has native `EventSourceResponse` support, making SSE implementation trivial.

**Primary recommendation:** Create a `frontend/` directory at the project root containing the Vite + React app. Configure Vite to build into `src/crypto_price_tracker/static/` (replacing the current `index.html`). Use `@tailwindcss/vite` plugin with `@theme` CSS-first configuration for the GitHub-dark color palette. Use React Router declarative mode with `BrowserRouter` for simplicity (3 routes, no data loaders needed).

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
1. SSE (Server-Sent Events) for real-time updates -- server pushes via `StreamingResponse`, 10s fixed interval, prices only
2. React Router with URL paths: `/`, `/portfolio`, `/alerts` -- top tabs navigation, coin detail as modal overlay
3. Recharts (~200KB) for line charts replacing Plotly CDN (~3MB) -- line chart with 7D/30D toggle
4. Tailwind utility classes replicating GitHub-dark theme: `#0d1117` bg, `#161b22` cards, `#58a6ff` accent, `#3fb950` up, `#f85149` down
5. Vite dev proxy for `/api/*` to FastAPI
6. Build output to `src/crypto_price_tracker/static/` (replacing current `index.html`)
7. Monospace font, nl-NL locale for EUR formatting

### Claude's Discretion
None specified -- all major decisions were locked in CONTEXT.md.

### Deferred Ideas (OUT OF SCOPE)
None raised during discussion.
</user_constraints>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| vite | ^7.3 | Build tool & dev server | Industry standard, HMR, proxy, fast builds |
| react | ^19.0 | UI framework | Locked decision |
| react-dom | ^19.0 | React DOM renderer | Required by React |
| tailwindcss | ^4.2 | Utility-first CSS | Locked decision, CSS-first config in v4 |
| @tailwindcss/vite | ^4.2 | Tailwind Vite plugin | Official plugin, replaces PostCSS in v4 |
| recharts | ^3.7 | Chart library | Locked decision, ~200KB vs Plotly ~3MB |
| react-router | ^7.13 | Client-side routing | Locked decision. Note: v7 uses `react-router` package, NOT `react-router-dom` |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| @vitejs/plugin-react | ^4.x | React Fast Refresh for Vite | Always -- required for JSX transform and HMR |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Recharts | Plotly.js | Plotly is 3MB+, not React-native, but more chart types |
| Tailwind v4 @theme | tailwind.config.js | Config JS is deprecated in v4, CSS-first is the way |
| react-router | wouter | Wouter is lighter but lacks NavLink active styling |

**Installation (from `frontend/` directory):**
```bash
npm create vite@latest . -- --template react
npm install tailwindcss @tailwindcss/vite recharts react-router
```

## Architecture Patterns

### Recommended Project Structure
```
crypto-price-tracker-v2/
├── frontend/                    # NEW: Vite + React app
│   ├── index.html               # Vite entry HTML
│   ├── package.json
│   ├── vite.config.js
│   ├── src/
│   │   ├── main.jsx             # React root + Router
│   │   ├── App.jsx              # Layout: header + tabs + Outlet
│   │   ├── index.css            # Tailwind @import + @theme colors
│   │   ├── hooks/
│   │   │   ├── useSSE.js        # EventSource hook with auto-reconnect
│   │   │   └── useApi.js        # fetch wrapper for REST calls
│   │   ├── pages/
│   │   │   ├── PricesPage.jsx   # Price table + SSE subscription
│   │   │   ├── PortfolioPage.jsx # Portfolio CRUD
│   │   │   └── AlertsPage.jsx   # Alerts CRUD
│   │   ├── components/
│   │   │   ├── PriceTable.jsx   # Table with clickable rows
│   │   │   ├── CoinModal.jsx    # Coin detail + Recharts chart
│   │   │   ├── PriceChart.jsx   # Recharts LineChart wrapper
│   │   │   ├── PortfolioTable.jsx
│   │   │   ├── AddHoldingForm.jsx
│   │   │   ├── AlertList.jsx
│   │   │   ├── AddAlertForm.jsx
│   │   │   ├── Toast.jsx        # Toast notification component
│   │   │   └── CountdownTimer.jsx
│   │   └── lib/
│   │       └── format.js        # EUR formatter (nl-NL), percentage, volume
│   └── .gitignore               # node_modules, dist
├── src/
│   └── crypto_price_tracker/
│       ├── web.py               # MODIFIED: add SSE endpoint + SPA catch-all
│       ├── static/              # BUILD TARGET: Vite outputs here
│       │   ├── index.html       # REPLACED by Vite build
│       │   └── assets/          # JS/CSS chunks from Vite
│       └── ...                  # All other Python modules unchanged
├── pyproject.toml               # Unchanged
└── ...
```

### Pattern 1: SSE Endpoint (FastAPI)
**What:** Server pushes price data every 10 seconds via `EventSourceResponse`
**When to use:** The `/api/prices/stream` endpoint
**Example:**
```python
# Source: FastAPI official docs (https://fastapi.tiangolo.com/tutorial/server-sent-events/)
# Available since FastAPI 0.135.0 -- project has 0.135.1 installed
import asyncio
import dataclasses
import json
from collections.abc import AsyncIterable

from fastapi import Query
from fastapi.sse import EventSourceResponse, ServerSentEvent

@app.get("/api/prices/stream", response_class=EventSourceResponse)
async def stream_prices(
    top: int = Query(default=20, ge=1, le=100),
) -> AsyncIterable[ServerSentEvent]:
    """Push price updates every 10 seconds via SSE."""
    event_id = 0
    while True:
        coins = get_top_coins(top_n=top)
        active = db_get_active_alerts()
        triggered_alerts = check_alerts(coins, active)
        for alert in triggered_alerts:
            db_mark_triggered(alert.id)
        data = {
            "coins": [dataclasses.asdict(c) for c in coins],
            "triggered_alerts": [dataclasses.asdict(a) for a in triggered_alerts],
        }
        yield ServerSentEvent(
            data=json.dumps(data),
            event="prices",
            id=str(event_id),
            retry=10000,
        )
        event_id += 1
        await asyncio.sleep(10)
```

### Pattern 2: SSE Consumer Hook (React)
**What:** Custom React hook for EventSource with auto-reconnect and cleanup
**When to use:** PricesPage component subscribes to price stream
**Example:**
```jsx
// Source: Verified pattern from multiple React SSE implementations
import { useEffect, useRef, useState, useCallback } from 'react';

export function useSSE(url) {
  const [data, setData] = useState(null);
  const [connected, setConnected] = useState(false);
  const esRef = useRef(null);

  const connect = useCallback(() => {
    const es = new EventSource(url);
    esRef.current = es;

    es.addEventListener('prices', (event) => {
      setData(JSON.parse(event.data));
    });

    es.onopen = () => setConnected(true);

    es.onerror = () => {
      setConnected(false);
      es.close();
      // EventSource auto-reconnects, but we handle manual reconnect
      // if readyState is CLOSED (2)
      if (es.readyState === EventSource.CLOSED) {
        setTimeout(connect, 3000);
      }
    };

    return es;
  }, [url]);

  useEffect(() => {
    const es = connect();
    return () => {
      es.close();
      esRef.current = null;
    };
  }, [connect]);

  return { data, connected };
}
```

### Pattern 3: Vite Config with Proxy and Build Output
**What:** Dev proxy to FastAPI + build output to Python static dir
**When to use:** `frontend/vite.config.js`
**Example:**
```javascript
// Source: Vite official docs (https://vite.dev/config/server-options)
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        // No rewrite needed -- FastAPI routes already start with /api
      },
    },
  },
  build: {
    outDir: '../src/crypto_price_tracker/static',
    emptyOutDir: true,
  },
});
```

### Pattern 4: Tailwind CSS v4 Theme (CSS-first)
**What:** Custom GitHub-dark color palette defined via `@theme` directive
**When to use:** `frontend/src/index.css`
**Example:**
```css
/* Source: Tailwind CSS v4 docs (https://tailwindcss.com/docs/theme) */
@import "tailwindcss";

@theme {
  --color-bg: #0d1117;
  --color-card: #161b22;
  --color-border: #21262d;
  --color-border-light: #30363d;
  --color-accent: #58a6ff;
  --color-text: #c9d1d9;
  --color-text-muted: #8b949e;
  --color-text-dim: #6e7681;
  --color-up: #3fb950;
  --color-down: #f85149;

  --font-mono: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas,
    "Liberation Mono", "Courier New", monospace;
}
```
This generates utility classes like `bg-bg`, `text-accent`, `text-up`, `text-down`, `border-border`, `font-mono`, etc.

### Pattern 5: React Router Layout with Tabs
**What:** BrowserRouter with NavLink tabs and Outlet for page content
**When to use:** `App.jsx` layout component
**Example:**
```jsx
// Source: React Router v7 docs (https://reactrouter.com/home)
import { BrowserRouter, Routes, Route, NavLink, Outlet } from 'react-router';

function Layout() {
  return (
    <div className="min-h-screen bg-bg font-mono text-text">
      <header className="p-5">
        <h1 className="text-accent text-2xl font-bold">Crypto Prices -- EUR</h1>
      </header>
      <nav className="flex gap-1 px-5 mb-4">
        <NavLink
          to="/"
          end
          className={({ isActive }) =>
            `px-4 py-1.5 rounded-t border text-sm ${
              isActive
                ? 'bg-card border-border-light text-text'
                : 'bg-border border-border text-text-muted hover:text-text'
            }`
          }
        >
          Prices
        </NavLink>
        <NavLink
          to="/portfolio"
          className={({ isActive }) =>
            `px-4 py-1.5 rounded-t border text-sm ${
              isActive
                ? 'bg-card border-border-light text-text'
                : 'bg-border border-border text-text-muted hover:text-text'
            }`
          }
        >
          Portfolio
        </NavLink>
        <NavLink
          to="/alerts"
          className={({ isActive }) =>
            `px-4 py-1.5 rounded-t border text-sm ${
              isActive
                ? 'bg-card border-border-light text-text'
                : 'bg-border border-border text-text-muted hover:text-text'
            }`
          }
        >
          Alerts
        </NavLink>
      </nav>
      <main className="px-5">
        <Outlet />
      </main>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<PricesPage />} />
          <Route path="portfolio" element={<PortfolioPage />} />
          <Route path="alerts" element={<AlertsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
```

### Pattern 6: Recharts Price Chart
**What:** LineChart showing closing prices with period toggle
**When to use:** CoinModal / PriceChart component
**Example:**
```jsx
// Source: Recharts API docs (https://recharts.github.io/en-US/api/LineChart/)
import {
  LineChart, Line, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid,
} from 'recharts';

function PriceChart({ candles, color = '#58a6ff' }) {
  // candles = [{ timestamp, open, high, low, close, volume }, ...]
  const data = candles.map((c) => ({
    time: new Date(c.timestamp).toLocaleDateString('nl-NL', {
      day: 'numeric', month: 'short',
    }),
    price: c.close,
  }));

  return (
    <ResponsiveContainer width="100%" height={250}>
      <LineChart data={data} margin={{ top: 5, right: 10, left: 10, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
        <XAxis
          dataKey="time"
          tick={{ fill: '#8b949e', fontSize: 11 }}
          stroke="#21262d"
        />
        <YAxis
          tick={{ fill: '#8b949e', fontSize: 11 }}
          stroke="#21262d"
          domain={['auto', 'auto']}
        />
        <Tooltip
          contentStyle={{
            background: '#161b22',
            border: '1px solid #30363d',
            color: '#c9d1d9',
            fontFamily: 'monospace',
          }}
          formatter={(value) =>
            new Intl.NumberFormat('nl-NL', {
              style: 'currency', currency: 'EUR',
            }).format(value)
          }
        />
        <Line
          type="monotone"
          dataKey="price"
          stroke={color}
          strokeWidth={2}
          dot={false}
          activeDot={{ r: 4, fill: color }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
```

### Pattern 7: EUR Formatting Utility
**What:** Consistent EUR formatting with nl-NL locale
**When to use:** All price/value display throughout the app
**Example:**
```javascript
// lib/format.js
const eurFormatter = new Intl.NumberFormat('nl-NL', {
  style: 'currency',
  currency: 'EUR',
});

const eurCompactFormatter = new Intl.NumberFormat('nl-NL', {
  style: 'currency',
  currency: 'EUR',
  notation: 'compact',
  maximumFractionDigits: 1,
});

const pctFormatter = new Intl.NumberFormat('nl-NL', {
  style: 'percent',
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
  signDisplay: 'always',
});

export function formatEUR(value) {
  return eurFormatter.format(value);
}

export function formatEURCompact(value) {
  return eurCompactFormatter.format(value);
}

export function formatPct(value) {
  // value is already a percentage number (e.g., 2.5 for 2.5%)
  return pctFormatter.format(value / 100);
}
```

### Pattern 8: SPA Catch-All Route (FastAPI)
**What:** Serve `index.html` for all non-API, non-static routes to support React Router
**When to use:** Modified `web.py` -- must be the LAST route defined
**Example:**
```python
# Source: Verified pattern from FastAPI + React SPA guides
from fastapi.responses import FileResponse
from pathlib import Path

STATIC_DIR = Path(__file__).parent / "static"

# In create_app(), AFTER all /api/* routes, BEFORE app.mount("/static", ...):

@app.get("/{path:path}")
def spa_catch_all(path: str):
    """Serve index.html for all non-API paths (SPA routing)."""
    # Try to serve actual static files first (JS, CSS, images)
    file_path = STATIC_DIR / path
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    # Fall back to index.html for client-side routing
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "Crypto Price Tracker API", "docs": "/docs"}
```

**Important:** The current `web.py` has a `@app.get("/")` route and a `app.mount("/static", ...)` at the end. For SPA support, replace both with the catch-all pattern above. The catch-all MUST be registered after all `/api/*` routes so they take priority.

### Anti-Patterns to Avoid
- **Inline styles in React components:** Use Tailwind utility classes exclusively. Do not port the 200+ lines of inline CSS from the current `index.html` as `style={{...}}` props.
- **Polling instead of SSE:** Do not use `setInterval` + `fetch` for price updates. The SSE connection handles push updates.
- **Giant monolith component:** Do not put all 10 features into a single `App.jsx`. Split into pages and small components.
- **`react-router-dom` package:** In React Router v7, import from `react-router`, not `react-router-dom`. The `-dom` package is a legacy compatibility shim.
- **`tailwind.config.js`:** Tailwind v4 uses CSS-first `@theme` directive. Do not create a JS config file.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Chart rendering | Custom SVG/Canvas | Recharts `<LineChart>` | Axes, tooltips, responsive sizing, animation all handled |
| CSS utility system | Custom CSS classes | Tailwind CSS 4 | Consistent design tokens, purging, responsive variants |
| Client-side routing | Hash-based nav + show/hide divs | React Router `<BrowserRouter>` | URL support, back/forward, NavLink active state |
| SSE auto-reconnect | Manual WebSocket reconnect | `EventSource` built-in | Browser auto-reconnects SSE by default |
| EUR number formatting | Custom `toFixed()` logic | `Intl.NumberFormat('nl-NL', ...)` | Handles thousands separators, decimals, currency symbol correctly |
| Build tooling | Webpack config | Vite `npm create vite` | Zero-config React + Tailwind + proxy setup |
| SSE server endpoint | Raw `StreamingResponse` | FastAPI `EventSourceResponse` | Handles keep-alive pings, cache headers, proper formatting |

**Key insight:** The current `index.html` hand-rolls everything (tabs, modals, formatting, polling). React + its ecosystem replaces all custom logic with composable, tested components.

## Common Pitfalls

### Pitfall 1: Vite Build Output Overwrites .gitignore
**What goes wrong:** `emptyOutDir: true` in Vite config deletes everything in `static/` before build, including any `.gitkeep` or other files.
**Why it happens:** Vite's build step cleans the output directory by default.
**How to avoid:** This is actually desired behavior. The `static/` directory should only contain build output. Add `frontend/dist` and `src/crypto_price_tracker/static/assets/` to `.gitignore`. Keep the old `index.html` in git history but accept it will be replaced.
**Warning signs:** Build artifacts (JS/CSS chunks) appearing in git status.

### Pitfall 2: SPA Route Order in FastAPI
**What goes wrong:** The catch-all `/{path:path}` route swallows `/api/*` requests, returning `index.html` instead of JSON.
**Why it happens:** FastAPI processes routes in registration order. If catch-all is registered before API routes, it matches first.
**How to avoid:** Register ALL `/api/*` routes BEFORE the SPA catch-all. Remove the old `app.mount("/static", ...)` and old `@app.get("/")` route. The catch-all handles both.
**Warning signs:** API calls returning HTML content-type, 200 responses with HTML body.

### Pitfall 3: SSE Connection Stacking
**What goes wrong:** Multiple EventSource connections open simultaneously, causing duplicate price updates and server load.
**Why it happens:** React strict mode (dev only) double-invokes effects. Or: navigating away from PricesPage and back creates a new connection without closing the old one.
**How to avoid:** Always close EventSource in useEffect cleanup. Use a ref to track the connection. Consider only subscribing when PricesPage is mounted.
**Warning signs:** Network tab showing multiple open SSE connections, prices flickering rapidly.

### Pitfall 4: Tailwind v4 @theme vs :root Confusion
**What goes wrong:** Custom colors defined in `:root` don't generate utility classes. Writing `bg-[var(--my-color)]` everywhere.
**Why it happens:** Tailwind v4 only generates utilities for variables defined inside `@theme { }`, not `:root`.
**How to avoid:** Define ALL design token colors inside `@theme { --color-*: ...; }`. Use the generated utilities like `bg-accent`, `text-up`.
**Warning signs:** Lots of arbitrary value classes like `bg-[#0d1117]` or `text-[var(--color-accent)]`.

### Pitfall 5: Vite Proxy Not Matching SSE Content-Type
**What goes wrong:** SSE connections through Vite proxy get buffered or timeout.
**Why it happens:** Some proxy configurations buffer streaming responses.
**How to avoid:** Vite's proxy (based on http-proxy) handles SSE correctly out of the box. Do NOT add `rewrite` rules for the `/api` prefix since FastAPI routes already use `/api/*`. FastAPI's `EventSourceResponse` sets `X-Accel-Buffering: no` automatically.
**Warning signs:** SSE events arriving in batches instead of individually, or connection timing out.

### Pitfall 6: React Router v7 Import Path
**What goes wrong:** `import { BrowserRouter } from 'react-router-dom'` fails or installs an extra package.
**Why it happens:** React Router v7 consolidated all exports into the `react-router` package. The `react-router-dom` package is a legacy compatibility layer.
**How to avoid:** Install `react-router` (not `react-router-dom`). Import everything from `'react-router'`.
**Warning signs:** Package.json has both `react-router` and `react-router-dom`, or import errors.

### Pitfall 7: Production Static File MIME Types
**What goes wrong:** Vite build output JS/CSS files served with wrong MIME type by FastAPI.
**Why it happens:** The catch-all `FileResponse` may not detect MIME type correctly for all file extensions.
**How to avoid:** `FileResponse` auto-detects MIME type from file extension. Alternatively, mount static assets explicitly: `app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"))` for Vite chunk files, then catch-all for everything else.
**Warning signs:** Browser console showing MIME type errors, scripts not executing.

## Code Examples

### Complete main.jsx (Entry Point)
```jsx
// Source: Verified Vite + React + Router setup pattern
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router';
import App from './App';
import './index.css';

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </StrictMode>
);
```

### Toast Notification Pattern
```jsx
// Source: Standard React portal + timer pattern
import { useEffect, useState } from 'react';

export function Toast({ message, type = 'info', duration = 10000, onClose }) {
  useEffect(() => {
    const timer = setTimeout(onClose, duration);
    return () => clearTimeout(timer);
  }, [duration, onClose]);

  const colors = {
    info: 'border-accent text-accent',
    success: 'border-up text-up',
    error: 'border-down text-down',
  };

  return (
    <div className={`fixed top-4 right-4 z-50 bg-card border ${colors[type]}
      rounded px-4 py-3 font-mono text-sm shadow-lg`}>
      {message}
      <button onClick={onClose} className="ml-3 text-text-muted hover:text-text">
        x
      </button>
    </div>
  );
}
```

### Manual Refresh Alongside SSE
```jsx
// Pattern: Manual refresh triggers an immediate fetch while SSE handles periodic updates
function PricesPage() {
  const { data: sseData } = useSSE('/api/prices/stream');
  const [prices, setPrices] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  // SSE updates
  useEffect(() => {
    if (sseData) {
      setPrices(sseData);
      setLastUpdate(new Date());
    }
  }, [sseData]);

  // Manual refresh
  const handleRefresh = async () => {
    const res = await fetch('/api/prices');
    const data = await res.json();
    setPrices(data);
    setLastUpdate(new Date());
  };

  // Countdown timer (10s SSE interval)
  const [countdown, setCountdown] = useState(10);
  useEffect(() => {
    setCountdown(10); // Reset on each SSE update
  }, [sseData]);
  useEffect(() => {
    const id = setInterval(() => setCountdown((c) => Math.max(0, c - 1)), 1000);
    return () => clearInterval(id);
  }, []);

  return (
    <div>
      <div className="flex items-center gap-2 text-text-dim text-xs mb-4">
        <span>Next update in <span className="text-accent font-bold">{countdown}s</span></span>
        <button onClick={handleRefresh} className="bg-border border border-border-light
          rounded px-2.5 py-0.5 text-text hover:border-accent hover:text-accent">
          Refresh
        </button>
      </div>
      {prices && <PriceTable coins={prices.coins} />}
    </div>
  );
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Tailwind `tailwind.config.js` | Tailwind v4 `@theme` CSS directive | Jan 2025 (v4.0) | No JS config file, CSS-first |
| `react-router-dom` package | `react-router` package | Nov 2024 (v7.0) | Single package, simplified imports |
| FastAPI `StreamingResponse` for SSE | FastAPI `EventSourceResponse` | Jan 2025 (v0.135.0) | Built-in keep-alive, auto JSON encoding |
| Vite PostCSS + `@tailwind` directives | Vite `@tailwindcss/vite` plugin | Jan 2025 (Tailwind v4) | Faster, no PostCSS config needed |
| Plotly CDN (~3MB) | Recharts (~200KB) | N/A (library choice) | 15x smaller, React-native components |

**Deprecated/outdated:**
- `tailwind.config.js`: Replaced by `@theme` in Tailwind v4. Still works via compat but not recommended.
- `react-router-dom`: Replaced by unified `react-router` in v7. Legacy shim only.
- `@tailwind base/components/utilities` directives: Replaced by `@import "tailwindcss"` in v4.
- Manual `StreamingResponse(media_type="text/event-stream")`: Use `EventSourceResponse` instead for proper SSE formatting.

## Open Questions

1. **Hatchling static file inclusion**
   - What we know: The current `pyproject.toml` has `packages = ["src/crypto_price_tracker"]` which includes everything under that directory tree, including `static/`. Vite build output to `static/` will be automatically included in the wheel.
   - What's unclear: Whether the `node_modules/` or `frontend/` directory could accidentally be picked up by hatchling.
   - Recommendation: Add `frontend/` to `.gitignore` is NOT needed (we want it versioned), but DO add `frontend/node_modules/` and `frontend/dist/` to `.gitignore`. The hatchling config only packages `src/crypto_price_tracker/`, so `frontend/` at the project root is safe.

2. **SSE connection limit per browser**
   - What we know: Browsers limit concurrent connections per domain (6 for HTTP/1.1). Each SSE connection is a persistent HTTP connection.
   - What's unclear: If a user opens multiple tabs, they each open an SSE connection.
   - Recommendation: Not a concern for a local dev tool. If needed later, a `BroadcastChannel` API could share one SSE connection across tabs.

## Sources

### Primary (HIGH confidence)
- [FastAPI SSE official docs](https://fastapi.tiangolo.com/tutorial/server-sent-events/) - EventSourceResponse API, ServerSentEvent fields, keep-alive behavior
- [Tailwind CSS v4 @theme docs](https://tailwindcss.com/docs/theme) - CSS-first configuration, --color-* namespaces, @import syntax
- [Vite server proxy docs](https://vite.dev/config/server-options) - Proxy configuration syntax, target/changeOrigin/rewrite options
- [Recharts LineChart API](https://recharts.github.io/en-US/api/LineChart/) - Props, child components, data format
- [Recharts Line API](https://recharts.github.io/en-US/api/Line) - type, stroke, dot, activeDot props
- [React Router v7 docs](https://reactrouter.com/home) - BrowserRouter, NavLink, Route, Outlet patterns
- [Tailwind CSS Vite installation guide](https://tailwindcss.com/docs) - Official step-by-step setup

### Secondary (MEDIUM confidence)
- [FastAPI + React (2025)](https://www.joshfinnie.com/blog/fastapi-and-react-in-2025/) - Project structure, proxy setup, dual dev server pattern
- [FastAPI SPA catch-all gist](https://gist.github.com/ultrafunkamsterdam/b1655b3f04893447c3802453e05ecb5e) - FileResponse catch-all pattern for react-router

### Tertiary (LOW confidence)
- None -- all findings verified with primary or secondary sources.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All versions verified on npm, all APIs verified in official docs
- Architecture: HIGH - Patterns verified against official documentation for each library
- Pitfalls: HIGH - Based on verified API behaviors (FastAPI route ordering, Tailwind v4 @theme requirements, React Router v7 import changes)
- SSE integration: HIGH - FastAPI 0.135.1 installed, `EventSourceResponse` verified in official docs with code examples

**Research date:** 2026-03-07
**Valid until:** 2026-04-07 (stable ecosystem, 30-day validity)

**Environment verified:**
- Node.js: v22.22.0 (meets Vite requirement of 20.19+)
- npm: 10.9.4
- FastAPI: 0.135.1 (has EventSourceResponse support, added in 0.135.0)
- Python: 3.12+
