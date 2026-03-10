# Phase 17: Mobile-Optimized Data Views - Research

**Researched:** 2026-03-10
**Domain:** Responsive table-to-card layouts, loading skeletons, empty states (React + Tailwind CSS v4)
**Confidence:** HIGH

## Summary

Phase 17 transforms four data-heavy views (PriceTable, PortfolioTable, WatchlistPage table, AlertList) from desktop-optimized tables into scannable card layouts on mobile (< 640px). It also adds loading skeleton placeholders and meaningful empty state messages across all data views.

The codebase is well-positioned for this work. Phase 15 established UI primitives (Table, Th, Td, Badge, Button) and Phase 16 added responsive breakpoints (sm/md), overflow-x-auto wrappers, and mobile touch targets (min-h-11). The app uses Tailwind CSS v4 with @theme variables (dark theme only) and React 19. There is no existing `useMediaQuery` hook or skeleton component -- both need to be created. Current loading states are plain text ("Loading watchlist...") and empty states are minimal single-line messages.

**Primary recommendation:** Use CSS-only `hidden sm:block` / `sm:hidden` to toggle between card and table layouts, with a shared Skeleton primitive for loading placeholders. No JS-based media queries needed for the layout switch itself. Create a `useMediaQuery` hook only if needed for skeleton layout matching (showing card-shaped vs table-row-shaped skeletons).

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| MOB-01 | Price table switches to card-based layout on mobile (< 640px) -- one card per coin with key stats | PriceTable analysis: 7 columns (star, rank, symbol, name, price, 24h%, volume). Card shows symbol, name, price, change. Star + row click preserved. |
| MOB-02 | Portfolio table switches to card layout on mobile with expandable lot details | PortfolioTable analysis: 8 columns + expandable lot rows. Card shows symbol, amount, value, P&L. Lot expansion via accordion pattern within card. |
| MOB-03 | Watchlist table switches to card layout on mobile with tag pills | WatchlistPage table analysis: 7 columns (symbol, name, tags, price, 24h%, volume, actions). Card shows symbol, name, tag Badge pills, price, change. Edit/Remove actions. |
| MOB-04 | Alerts display as stacked cards on mobile (already card-based, ensure proper spacing) | AlertList analysis: already card-based with `bg-card border border-border rounded p-3 mb-2`. Just needs spacing audit and mobile-specific adjustments (gap between cards, padding consistency). |
| MOB-05 | Loading skeleton placeholders shown while data is fetching (matching card/table layout) | Currently all loading states are plain text like "Loading watchlist...". Need Skeleton primitive component with pulse animation. Skeletons should match card layout on mobile, table rows on desktop. |
| MOB-06 | Empty state illustrations/messages for tables with no data (portfolio, watchlist, alerts) | Current empty states: PortfolioTable has "No holdings yet. Add one above.", WatchlistPage has conditional message, AlertList has "No {title}". Need richer messages with visual indicators. |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Tailwind CSS | v4.2.1 | Responsive utility classes for card/table toggle | Already in use, @theme variables defined |
| React | v19.2.0 | Component rendering | Already in use |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| @tailwindcss/vite | v4.2.1 | Build integration | Already configured |
| vitest | v4.0.18 | Unit testing | Already configured with jsdom |
| @testing-library/react | v16.3.2 | Component testing | Already in use for UI primitive tests |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| CSS hidden/block toggle | JS useMediaQuery for layout switch | CSS is simpler, no JS needed for showing/hiding; JS adds complexity but allows conditional rendering to save DOM nodes. CSS approach is preferred since these are lightweight components. |
| Custom Skeleton component | react-loading-skeleton npm package | External dependency is overkill. Tailwind's `animate-pulse` + a simple div-based Skeleton primitive matches the project's pattern of in-app UI components (per REQUIREMENTS.md "Out of Scope" -- no component library packages). |
| SVG empty state illustrations | Text-only empty states with emoji/icon | Text + simple styled div indicators match the minimal dark-theme aesthetic. SVG illustrations would be out of character for this monospace/dark terminal-inspired UI. |

**No new dependencies needed.** Everything can be built with existing Tailwind CSS utilities.

## Architecture Patterns

### Recommended Project Structure
```
frontend/src/
  components/
    ui/
      Skeleton.jsx           # NEW: Shared skeleton placeholder primitive
      Card.jsx               # NEW: Shared card container primitive (optional)
      EmptyState.jsx          # NEW: Shared empty state primitive
      __tests__/
        Skeleton.test.jsx     # NEW
        EmptyState.test.jsx   # NEW
    PriceTable.jsx            # MODIFIED: Add mobile card view
    PortfolioTable.jsx        # MODIFIED: Add mobile card view with expandable lots
    AlertList.jsx             # MODIFIED: Spacing adjustments
  pages/
    WatchlistPage.jsx         # MODIFIED: Add mobile card view
    PortfolioPage.jsx         # MODIFIED: Add skeleton loading state
    PricesPage.jsx            # MODIFIED: Add skeleton loading state
    AlertsPage.jsx            # MODIFIED: Add skeleton loading state
  hooks/
    useMediaQuery.js          # NEW: Optional, only if skeleton layout matching needed
```

### Pattern 1: CSS-Only Table/Card Toggle
**What:** Use Tailwind responsive classes to show a card layout on mobile and a table on desktop, both rendered in the same component.
**When to use:** For all three table-to-card conversions (PriceTable, PortfolioTable, WatchlistPage table).
**Example:**
```jsx
function PriceTable({ coins, onSelectCoin }) {
  return (
    <>
      {/* Mobile card layout */}
      <div className="sm:hidden space-y-2">
        {coins.map((coin) => (
          <div
            key={coin.symbol}
            onClick={() => onSelectCoin(coin)}
            className="bg-card border border-border rounded p-3 cursor-pointer active:bg-border/50"
          >
            <div className="flex justify-between items-start mb-1">
              <div>
                <span className="text-accent font-bold">{coin.symbol}</span>
                <span className="text-text-muted text-sm ml-2">{coin.name}</span>
              </div>
              {/* watchlist star button */}
            </div>
            <div className="flex justify-between items-baseline">
              <span className="text-text">{formatEUR(coin.price)}</span>
              <span className={coin.change_24h > 0 ? 'text-up' : 'text-down'}>
                {formatPct(coin.change_24h)}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Desktop table layout */}
      <div className="hidden sm:block overflow-x-auto">
        <Table className="max-w-4xl">
          {/* existing table markup */}
        </Table>
      </div>
    </>
  );
}
```

### Pattern 2: Skeleton Primitive with animate-pulse
**What:** A reusable Skeleton component that renders pulsing placeholder shapes.
**When to use:** For all loading states across the app.
**Example:**
```jsx
// ui/Skeleton.jsx
export function Skeleton({ className = '', ...props }) {
  return (
    <div
      className={`animate-pulse bg-border rounded ${className}`}
      {...props}
    />
  );
}

// Usage: card skeleton on mobile
<div className="sm:hidden space-y-2">
  {[...Array(5)].map((_, i) => (
    <div key={i} className="bg-card border border-border rounded p-3">
      <div className="flex justify-between mb-2">
        <Skeleton className="h-4 w-16" />
        <Skeleton className="h-4 w-20" />
      </div>
      <div className="flex justify-between">
        <Skeleton className="h-5 w-24" />
        <Skeleton className="h-4 w-12" />
      </div>
    </div>
  ))}
</div>

// Usage: table skeleton on desktop
<div className="hidden sm:block">
  <Table className="max-w-4xl">
    <thead><tr><Th>Symbol</Th><Th>Price</Th>...</tr></thead>
    <tbody>
      {[...Array(5)].map((_, i) => (
        <tr key={i} className="border-b border-border/50">
          <Td><Skeleton className="h-4 w-12" /></Td>
          <Td><Skeleton className="h-4 w-20" /></Td>
          ...
        </tr>
      ))}
    </tbody>
  </Table>
</div>
```

### Pattern 3: Empty State Component
**What:** A consistent empty state with an icon/visual and descriptive message.
**When to use:** When data arrays are empty (no portfolio holdings, empty watchlist, no alerts).
**Example:**
```jsx
// ui/EmptyState.jsx
export function EmptyState({ title, description, className = '' }) {
  return (
    <div className={`text-center py-8 ${className}`}>
      <p className="text-text-muted text-lg mb-1">{title}</p>
      {description && (
        <p className="text-text-dim text-sm">{description}</p>
      )}
    </div>
  );
}

// Usage:
<EmptyState
  title="No holdings yet"
  description="Add your first holding using the form above to start tracking your portfolio."
/>
```

### Pattern 4: Portfolio Card with Expandable Lots
**What:** On mobile, each portfolio row becomes a card. Tapping it toggles an expandable section showing individual lot details.
**When to use:** PortfolioTable on mobile.
**Example:**
```jsx
<div className="sm:hidden space-y-2">
  {rows.map((row) => (
    <div key={row.symbol} className="bg-card border border-border rounded overflow-hidden">
      <div
        onClick={() => toggleLots(row.symbol)}
        className="p-3 cursor-pointer active:bg-border/50"
      >
        <div className="flex justify-between items-start mb-1">
          <div>
            <span className="text-accent font-bold">{row.symbol}</span>
            <span className="text-text-dim text-xs ml-1">({row.num_lots} lots)</span>
          </div>
          <span className={pnlColor(row.pnl_pct)}>{formatPct(row.pnl_pct)}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-text-muted">Value: {formatEUR(row.current_value)}</span>
          <span className={pnlColor(row.pnl_eur)}>{formatEUR(row.pnl_eur)}</span>
        </div>
      </div>
      {expandedSymbol === row.symbol && (
        <div className="border-t border-border/50 bg-bg/50 px-3 py-2">
          {/* lot details here */}
        </div>
      )}
    </div>
  ))}
</div>
```

### Anti-Patterns to Avoid
- **Conditional rendering via JS media queries for layout switch:** Using `useMediaQuery` to conditionally render card vs table adds JS complexity and causes layout flashes on page load. Use CSS `hidden sm:block` / `sm:hidden` instead.
- **Duplicating data transformation logic:** The card and table views share the same data. Extract shared rendering logic (like P&L color, format functions) and reuse between both views. Do NOT create separate components that each fetch their own data.
- **Over-engineering Card component:** Do not create a generic Card primitive with many props. Each data view's card has unique layout needs. Use direct Tailwind classes on divs. A Card primitive would add abstraction without value.
- **Complex skeleton count matching:** Do not try to match skeleton count to actual data length. Use a fixed count (e.g., 5 skeletons) for simplicity.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Pulse animation | Custom CSS keyframes | Tailwind's built-in `animate-pulse` | Already works, tested, zero config |
| Responsive breakpoints | Custom media query JS | Tailwind `sm:` / `md:` prefix classes | Consistent with Phase 16 patterns |
| Card container styling | Reusable Card wrapper | Direct `bg-card border border-border rounded` classes | Same pattern used in AlertList, PortfolioPage summary -- consistency trumps DRY here |

**Key insight:** The project already has a card styling pattern (`bg-card border border-border rounded p-3`) used in AlertList and PortfolioPage summary. Reuse this exact pattern for consistency rather than abstracting it.

## Common Pitfalls

### Pitfall 1: Forgetting Interactive States on Cards
**What goes wrong:** Cards lack tap feedback, making them feel unresponsive on mobile.
**Why it happens:** Desktop hover styles don't translate to touch.
**How to avoid:** Add `active:bg-border/50` or `active:bg-card/80` to clickable cards for touch feedback. Add `cursor-pointer` as well.
**Warning signs:** Cards feel "dead" when tapped.

### Pitfall 2: Watchlist Star Button Propagation on Cards
**What goes wrong:** Clicking the watchlist star on a PriceTable card also triggers the card's onClick (opening CoinModal).
**Why it happens:** The existing table uses `e.stopPropagation()` on the star button, which works. But the card layout may structure DOM differently.
**How to avoid:** Ensure the star button still calls `e.stopPropagation()` in the card layout, same as the table layout.
**Warning signs:** Clicking star both toggles watchlist AND opens the modal.

### Pitfall 3: Portfolio Lot Expansion State Shared Between Layouts
**What goes wrong:** The card and table views share the same `expandedSymbol` state, so expanding in one layout auto-expands in the other.
**Why it happens:** Both layouts render simultaneously (CSS hidden/shown), and both reference the same state.
**How to avoid:** This is actually fine -- the user only sees one layout at a time, and shared state means the expanded coin persists if they resize. No action needed.

### Pitfall 4: Skeleton Layout Mismatch
**What goes wrong:** Skeletons are shown as card-shaped on desktop (or table-shaped on mobile) because the CSS toggle was not applied to the skeleton section.
**Why it happens:** Loading state rendering was added without the `sm:hidden` / `hidden sm:block` wrapper.
**How to avoid:** Apply the same `sm:hidden` / `hidden sm:block` pattern to skeleton sections as to the data sections. On mobile, show card-shaped skeletons; on desktop, show table-row-shaped skeletons.
**Warning signs:** Skeletons look out of place when resizing browser.

### Pitfall 5: PriceTable Has No Loading State Currently
**What goes wrong:** PriceTable receives `coins` as a prop from PricesPage, which receives data from SSE. There is no explicit loading state -- the table simply doesn't render until `prices` is truthy.
**Why it happens:** SSE data arrives continuously, so there's a brief flash of nothing before the first event.
**How to avoid:** Add skeleton loading to PricesPage for the initial load (when `prices` is null). After first SSE event, data is always present.
**Warning signs:** Empty/flash on initial page load.

### Pitfall 6: Empty States Need Different Messages Per Context
**What goes wrong:** Generic "No data" messages don't guide the user toward action.
**Why it happens:** Using a single message for all empty states.
**How to avoid:** Tailor each empty state: Portfolio -> "Add your first holding above", Watchlist -> "Star coins on the Prices tab or add them above", Alerts -> "Set up a price alert to get notified".
**Warning signs:** User confusion about what to do next.

## Code Examples

### Current Data Shapes (from component analysis)

**PriceTable coin object** (from SSE via PricesPage):
```javascript
{
  symbol: "BTC",       // string
  name: "Bitcoin",     // string
  price: 45000.50,     // number (EUR)
  change_24h: 2.5,     // number (percentage, not decimal)
  volume: 12345,       // number (raw volume)
  volume_eur: 5000000  // number (EUR volume)
}
```

**PortfolioTable row object** (from /api/portfolio):
```javascript
{
  symbol: "BTC",           // string
  total_amount: 1.5,       // number
  avg_buy_price: 40000,    // number (EUR)
  current_price: 45000,    // number | null (EUR)
  current_value: 67500,    // number | null (EUR)
  pnl_eur: 7500,           // number | null (EUR)
  pnl_pct: 12.5,           // number | null (percentage)
  allocation_pct: 65.2,    // number | null (percentage)
  num_lots: 3              // number
}
```

**WatchlistPage entry object** (from /api/watchlist):
```javascript
{
  symbol: "BTC",           // string
  name: "Bitcoin",         // string | null
  tags: "Layer1,DeFi",     // string (comma-separated) | null
  price: 45000,            // number | null (EUR)
  change_24h: 2.5,         // number | null (percentage)
  volume_eur: 5000000      // number | null (EUR)
}
```

**AlertList alert object** (from /api/alerts):
```javascript
{
  id: 1,                             // number
  symbol: "BTC",                     // string
  target_price: 50000,               // number (EUR)
  direction: "above",                // "above" | "below"
  status: "active",                  // "active" | "triggered"
  created_at: "2026-03-09T...",      // ISO string | null
  triggered_at: "2026-03-10T...",    // ISO string | null
}
```

### Current Card Pattern in Codebase
AlertList already uses a card pattern that serves as the reference:
```jsx
// From AlertList.jsx -- THE card styling convention
<div className="bg-card border border-border rounded p-3 mb-2 flex flex-col gap-2 sm:flex-row sm:justify-between sm:items-center">
```

### Current Loading State Pattern
All pages use the same text-only pattern:
```jsx
if (loading) {
  return <p className="text-text-muted text-sm">Loading portfolio...</p>;
}
```
This is replaced with skeleton components.

### Current Empty State Pattern
```jsx
// PortfolioTable
if (!rows || rows.length === 0) {
  return <p className="text-text-muted text-sm max-w-4xl">No holdings yet. Add one above.</p>;
}

// WatchlistPage
<p className="text-text-muted text-sm">
  {activeTags.length > 0
    ? 'No entries match the selected tags.'
    : 'Watchlist is empty. Add coins using the form above or star them on the Prices tab.'}
</p>

// AlertList
<p className="text-text-muted text-sm">No {title.toLowerCase()}</p>
```

### Breakpoint Reference (from Phase 16)
```
sm: 640px   -- Card/table breakpoint for MOB-01/02/03 (matches RESP-06 modal breakpoint)
md: 768px   -- Mobile nav breakpoint (BottomNav hidden at md+)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| CSS-only responsive tables (hide columns) | Card layouts on mobile | ~2020-present | Better information density and scannability on small screens |
| Plain "Loading..." text | Skeleton placeholders | ~2019-present | Perceived performance improvement, reduced layout shift |
| Blank empty states | Actionable empty state messages | ~2018-present | Better UX, guides users to take action |
| JS window.matchMedia for layout | CSS hidden/block toggle | Always available | Simpler, no hydration mismatch, no flash of wrong layout |

**Current state in this codebase:**
- Tables use `overflow-x-auto` (Phase 16) but still show full table on mobile -- scroll required
- Loading states are plain text -- no skeletons
- Empty states exist but are minimal single-line messages
- AlertList already uses card-based layout, which is the target pattern for other views

## Open Questions

1. **Card layout for PriceTable: which columns to show?**
   - What we know: 7 columns in table (star, rank, symbol, name, price, 24h%, volume)
   - Recommendation: Card shows symbol, name, price, 24h% change. Omit rank and volume from card (less important on mobile). Keep star button. This is the most information-dense yet scannable approach.

2. **Skeleton count per view**
   - What we know: No way to know actual data count before fetch completes
   - Recommendation: Use 5 skeleton cards/rows as a reasonable default. Matches typical "above the fold" content.

3. **Should we create a useMediaQuery hook?**
   - What we know: CSS toggle handles layout switching without JS. Only skeleton layout matching might benefit from JS media query.
   - Recommendation: Do NOT create useMediaQuery. Use the same `sm:hidden` / `hidden sm:block` CSS pattern for skeletons too. Both card-shaped and table-row-shaped skeletons render in DOM but only the appropriate one is visible. This keeps the approach consistent and simple.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | vitest v4.0.18 + @testing-library/react v16.3.2 |
| Config file | `frontend/vitest.config.js` |
| Quick run command | `cd frontend && npx vitest run --reporter=verbose` |
| Full suite command | `cd frontend && npx vitest run --reporter=verbose` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| MOB-01 | PriceTable renders card layout with sm:hidden class | unit | `cd frontend && npx vitest run src/components/ui/__tests__/Skeleton.test.jsx -x` | No -- Wave 0 |
| MOB-02 | PortfolioTable renders card layout with expandable lots | unit | Manual verification via responsive testing | No -- Wave 0 |
| MOB-03 | WatchlistPage renders card layout with tag badges | unit | Manual verification via responsive testing | No -- Wave 0 |
| MOB-04 | AlertList cards have proper spacing on mobile | unit | `cd frontend && npx vitest run` (existing AlertList behavior) | No -- needs visual check |
| MOB-05 | Skeleton component renders with animate-pulse | unit | `cd frontend && npx vitest run src/components/ui/__tests__/Skeleton.test.jsx -x` | No -- Wave 0 |
| MOB-06 | EmptyState component renders title and description | unit | `cd frontend && npx vitest run src/components/ui/__tests__/EmptyState.test.jsx -x` | No -- Wave 0 |

### Sampling Rate
- **Per task commit:** `cd frontend && npx vitest run --reporter=verbose`
- **Per wave merge:** `cd frontend && npx vitest run --reporter=verbose`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `frontend/src/components/ui/Skeleton.jsx` -- new Skeleton primitive
- [ ] `frontend/src/components/ui/__tests__/Skeleton.test.jsx` -- covers MOB-05
- [ ] `frontend/src/components/ui/EmptyState.jsx` -- new EmptyState primitive
- [ ] `frontend/src/components/ui/__tests__/EmptyState.test.jsx` -- covers MOB-06

## Sources

### Primary (HIGH confidence)
- Direct codebase analysis of all 13 frontend component files
- Phase 16 CONTEXT.md and SUMMARY files for responsive patterns and breakpoints
- `frontend/package.json` for exact dependency versions
- `frontend/src/index.css` for Tailwind v4 @theme configuration

### Secondary (MEDIUM confidence)
- Tailwind CSS v4 documentation for `animate-pulse`, responsive prefix behavior (verified via existing codebase usage of sm: and md: prefixes)

### Tertiary (LOW confidence)
- None -- all findings are from direct codebase analysis

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Direct analysis of package.json and existing code
- Architecture: HIGH - Patterns derived from existing codebase conventions (AlertList card pattern, Table primitive usage, loading state patterns)
- Pitfalls: HIGH - Identified from actual code (e.stopPropagation in PriceTable, shared expandedSymbol state in PortfolioTable, null checks on prices data)

**Research date:** 2026-03-10
**Valid until:** 2026-04-10 (stable -- no fast-moving dependencies involved)
