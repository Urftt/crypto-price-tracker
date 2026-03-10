# Phase 18: Visual Polish & Animations - Research

**Researched:** 2026-03-10
**Domain:** CSS animations, Tailwind CSS v4 transitions, React component styling, typography/spacing systems
**Confidence:** HIGH

## Summary

Phase 18 adds visual polish to the Crypto Price Tracker app through CSS-only animations (page transitions, modal enter/exit, toast slide-in/out, button hover states, price flash), standardized typography hierarchy, consistent spacing scale, and replacing hardcoded hex colors in PriceChart with CSS custom properties.

The project uses Tailwind CSS v4.2 with the `@theme` directive in `index.css` for custom properties. All animations can be achieved with pure CSS (Tailwind utility classes + custom `@keyframes` in `index.css`). No additional libraries are needed. The existing custom property system (`--color-*`) already defines the full color palette, and PriceChart's hardcoded hex values map 1:1 to these properties.

**Primary recommendation:** Use CSS-only animations via Tailwind utilities and custom `@keyframes` in `index.css`. No animation libraries needed. Add a `@utility` layer in the CSS for the flash animation class. For page transitions, wrap the `<Routes>` outlet in a CSS transition container keyed by location.

<phase_requirements>

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| VIS-01 | Page transition animations when switching tabs (subtle fade or slide) | App.jsx uses React Router v7 `<Routes>`. Add a wrapper component around route content that applies a CSS fade-in animation on key change using `location.pathname` as the key. |
| VIS-02 | Modal open/close animations (fade + scale) | Modal.jsx currently renders/unmounts instantly. Add CSS transition classes for backdrop fade and card scale. Use state-driven classes rather than conditional rendering for exit animation. |
| VIS-03 | Toast enter/exit animations (slide in from top-right, fade out) | Toast.jsx is positioned `fixed right-4` with stacked `top` via inline style. Add CSS `@keyframes` for slide-in (translateX) and a dismissing state for fade-out. |
| VIS-04 | Button hover and active state transitions (smooth color shifts) | Button.jsx already has `transition-colors`. Add `transition-all duration-150` and `active:scale-[0.97]` for press feedback. Already largely in place. |
| VIS-05 | Improved typography hierarchy | Current: h1=text-2xl, h2=text-lg, h3=text-sm, body=text-sm/text-xs. Define a clear scale and standardize across all pages. |
| VIS-06 | Consistent spacing scale | Current spacing is mostly consistent via Tailwind but some ad-hoc values exist (p-5, p-3, p-4, gap-1, gap-2, gap-3, mb-4, mb-5, mt-4, mt-6). Audit and normalize. |
| VIS-07 | Price change flash animation | PriceTable receives coins from SSE. Need to detect when a coin price changes and briefly flash the row/card with a highlight color. Track previous prices with useRef. |
| VIS-08 | PriceChart CSS custom properties | PriceChart has 6 unique hardcoded hex colors that all map exactly to existing `--color-*` custom properties defined in `index.css`. |

</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Tailwind CSS | 4.2.1 | Utility-first CSS framework | Already in use, provides transition/animation utilities |
| React | 19.2.0 | UI framework | Already in use |
| React Router | 7.13.1 | Client-side routing | Already in use, provides `useLocation` for page transitions |
| Recharts | 3.8.0 | Chart library | Already in use, PriceChart needs CSS custom property values |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| None needed | - | - | All animations achievable with CSS-only |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| CSS-only animations | Framer Motion | Overkill for these requirements -- adds 30KB+ for simple fade/scale effects that CSS handles natively |
| CSS-only page transitions | React Transition Group | Unnecessary complexity -- a CSS animation on key change is simpler and sufficient |
| CSS @keyframes | Tailwind animate plugin | The built-in Tailwind v4 `@keyframes` + `@theme` system is already available |

**Installation:**
```bash
# No new dependencies needed
```

## Architecture Patterns

### CSS Custom Properties + Tailwind @theme

The project already uses Tailwind v4's `@theme` directive in `index.css` to define custom color properties. This is the correct place to add animation-related custom properties and `@keyframes`.

**Current `index.css`:**
```css
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
  --font-mono: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", "Courier New", monospace;
}
```

### Pattern 1: CSS Keyframe Animations in index.css

**What:** Define `@keyframes` in `index.css` and reference them via Tailwind's `@theme` for animation utilities or via plain CSS classes.
**When to use:** For all enter/exit animations (page fade, modal scale, toast slide, price flash).

**Example (adding to index.css):**
```css
@import "tailwindcss";

@theme {
  /* existing colors... */

  /* Animation durations */
  --animate-fade-in: fade-in 200ms ease-out;
  --animate-scale-in: scale-in 200ms ease-out;
  --animate-slide-in-right: slide-in-right 300ms ease-out;
  --animate-flash: flash 600ms ease-out;
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes scale-in {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

@keyframes slide-in-right {
  from { opacity: 0; transform: translateX(100%); }
  to { opacity: 1; transform: translateX(0); }
}

@keyframes flash {
  0% { background-color: var(--color-accent); }
  100% { background-color: transparent; }
}
```

This makes `animate-fade-in`, `animate-scale-in`, `animate-slide-in-right`, and `animate-flash` available as Tailwind utility classes.

### Pattern 2: Page Transition via Key-based Remount

**What:** Wrap the `<Routes>` content in a div keyed by `location.pathname` with an `animate-fade-in` class. When the key changes, React remounts the div, replaying the CSS animation.
**When to use:** VIS-01 page transitions.

**Example:**
```jsx
import { Routes, Route, useLocation } from 'react-router';

function App() {
  const location = useLocation();
  // ...
  return (
    <div className="min-h-screen bg-bg font-mono text-text">
      {/* header, nav... */}
      <main className="px-5 pb-20 md:pb-0">
        <div key={location.pathname} className="animate-fade-in">
          <Routes location={location}>
            <Route index element={<PricesPage exchange={exchange} />} />
            {/* ... */}
          </Routes>
        </div>
      </main>
    </div>
  );
}
```

**Important:** Pass `location` to `<Routes location={location}>` to ensure route matching uses the same location as the key.

### Pattern 3: Modal Enter/Exit with State-driven Classes

**What:** Instead of `if (!open) return null`, always render the modal DOM but toggle visibility and animation classes based on an internal animation state. Use `onAnimationEnd` to truly unmount after exit animation completes.
**When to use:** VIS-02 modal animations.

**Example:**
```jsx
export function Modal({ open, onClose, children }) {
  const [visible, setVisible] = useState(false);
  const [animating, setAnimating] = useState(false);

  useEffect(() => {
    if (open) {
      setVisible(true);
      setAnimating(true);
    } else if (visible) {
      setAnimating(true); // triggers exit animation
    }
  }, [open]);

  const handleAnimationEnd = () => {
    setAnimating(false);
    if (!open) setVisible(false);
  };

  if (!visible) return null;

  return (
    <div
      className={`fixed inset-0 z-40 flex items-center justify-center transition-opacity duration-200 ${
        open ? 'bg-black/70 opacity-100' : 'bg-black/70 opacity-0'
      }`}
      onClick={onClose}
      onTransitionEnd={!open ? handleAnimationEnd : undefined}
    >
      <div
        className={`... transition-all duration-200 ${
          open ? 'scale-100 opacity-100' : 'scale-95 opacity-0'
        }`}
        onClick={(e) => e.stopPropagation()}
      >
        {children}
      </div>
    </div>
  );
}
```

### Pattern 4: Price Flash via useRef Previous Values

**What:** Track previous coin prices in a `useRef` map. When SSE delivers new data, compare current prices to previous. Apply a temporary CSS class to changed rows.
**When to use:** VIS-07 price change flash.

**Example:**
```jsx
function PriceTable({ coins }) {
  const prevPrices = useRef({});
  const [flashSymbols, setFlashSymbols] = useState(new Set());

  useEffect(() => {
    const flashing = new Set();
    for (const coin of coins) {
      const prev = prevPrices.current[coin.symbol];
      if (prev !== undefined && prev !== coin.price) {
        flashing.add(coin.symbol);
      }
      prevPrices.current[coin.symbol] = coin.price;
    }
    if (flashing.size > 0) {
      setFlashSymbols(flashing);
      const timer = setTimeout(() => setFlashSymbols(new Set()), 600);
      return () => clearTimeout(timer);
    }
  }, [coins]);

  // Then on each row/card:
  // className={`... ${flashSymbols.has(coin.symbol) ? 'animate-flash' : ''}`}
}
```

### Anti-Patterns to Avoid
- **JavaScript-driven animation loops:** Don't use `requestAnimationFrame` or JS timers for visual transitions. CSS handles these more performantly.
- **Installing Framer Motion for simple effects:** Adding a 30KB+ library for fade and scale transitions that CSS handles natively is unnecessary.
- **Conditional rendering for animated exit:** `if (!open) return null` prevents exit animations from being seen. Must keep DOM mounted during exit transition.
- **Inline keyframes:** Don't put `@keyframes` in component files. Centralize in `index.css` for reuse.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Fade/scale/slide animations | Custom JS animation system | CSS `@keyframes` + Tailwind `animate-*` utilities | CSS animations are GPU-accelerated and simpler |
| Duration/easing tokens | Hardcoded `200ms ease-out` everywhere | `@theme` variables for animation durations | Single source of truth, easy to tune globally |
| Color values in Recharts | Hardcoded hex strings | `getComputedStyle()` to read CSS custom properties | Theme changes propagate to charts automatically |

**Key insight:** Every animation in VIS-01 through VIS-07 is a basic CSS transition or keyframe animation. The Tailwind v4 `@theme` + `@keyframes` system provides exactly the right abstraction.

## Common Pitfalls

### Pitfall 1: Modal Exit Animation Never Visible
**What goes wrong:** Using `if (!open) return null` removes the DOM instantly, so the exit animation (fade-out, scale-down) is never seen.
**Why it happens:** Conditional rendering is the natural React pattern, but it defeats CSS transitions.
**How to avoid:** Use a two-state approach: `open` (desired state) and `visible` (DOM presence). Keep DOM mounted while exit animation plays, then set `visible=false` on `transitionend`.
**Warning signs:** Modal disappears instantly with no animation.

### Pitfall 2: Page Transition Flicker
**What goes wrong:** The new page content flashes unstyled or loads with a visible jump.
**Why it happens:** The key-based remount destroys and recreates the entire subtree, causing layout reflow.
**How to avoid:** Keep the animation short (150-200ms) and use `opacity` only (not `transform: translateY`) to avoid layout shifts. The `ease-out` curve makes the fade feel smooth.
**Warning signs:** Visible white flash or content jumping during tab switch.

### Pitfall 3: Recharts Ignoring CSS Custom Properties
**What goes wrong:** Passing `stroke="var(--color-accent)"` to Recharts SVG elements may not work because Recharts renders inline SVG attributes, not CSS.
**Why it happens:** SVG `stroke` and `fill` attributes accept CSS custom property references in modern browsers, but some Recharts internal components may stringify values.
**How to avoid:** Read the computed value at render time: `getComputedStyle(document.documentElement).getPropertyValue('--color-accent').trim()`. Store in a `useMemo` or a constants object.
**Warning signs:** Chart renders with literal string "var(--color-accent)" or no color.

### Pitfall 4: Flash Animation Firing on Initial Load
**What goes wrong:** Every row flashes when the page first loads because there are no previous prices.
**Why it happens:** The `prevPrices` ref starts empty, so every coin appears "changed."
**How to avoid:** Only flash when `prevPrices` already has an entry for that symbol (skip the first render).
**Warning signs:** All rows flash on page load.

### Pitfall 5: Toast Exit Animation Blocking Removal
**What goes wrong:** Toast starts exit animation but is removed from state before animation completes, causing it to disappear instantly.
**Why it happens:** `onClose` removes the toast from the array, unmounting it mid-animation.
**How to avoid:** Add a "dismissing" state to each toast. When `onClose` fires, set `dismissing: true`, play exit animation, then remove from array on `animationend`.
**Warning signs:** Toast disappears instantly instead of fading out.

### Pitfall 6: Inconsistent Spacing After Standardization
**What goes wrong:** Changing spacing values breaks existing visual layouts that relied on specific padding/margin combinations.
**Why it happens:** Ad-hoc values were often chosen to look right in context; a global scale may not fit everywhere.
**How to avoid:** Audit every changed value visually. The current spacing is mostly consistent (p-3 for cards, p-5 for page, gap-2/gap-3 for layouts). Only standardize genuinely inconsistent values.
**Warning signs:** Components look cramped or too spread out after changes.

## Code Examples

### Example 1: Complete index.css with Animations

```css
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

  --animate-fade-in: fade-in 150ms ease-out;
  --animate-scale-in: scale-in 200ms ease-out;
  --animate-slide-in-right: slide-in-right 300ms ease-out;
  --animate-fade-out: fade-out 200ms ease-in forwards;
  --animate-flash: flash 600ms ease-out;
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes scale-in {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

@keyframes slide-in-right {
  from { opacity: 0; transform: translateX(100%); }
  to { opacity: 1; transform: translateX(0); }
}

@keyframes fade-out {
  from { opacity: 1; }
  to { opacity: 0; }
}

@keyframes flash {
  0%, 100% { background-color: transparent; }
  15% { background-color: color-mix(in srgb, var(--color-accent) 25%, transparent); }
}
```

### Example 2: PriceChart with CSS Custom Properties

```jsx
// Helper to read CSS custom properties
function getCSSColor(prop) {
  return getComputedStyle(document.documentElement).getPropertyValue(prop).trim();
}

function PriceChart({ symbol }) {
  // Read theme colors once
  const colors = useMemo(() => ({
    border: getCSSColor('--color-border'),
    textMuted: getCSSColor('--color-text-muted'),
    card: getCSSColor('--color-card'),
    borderLight: getCSSColor('--color-border-light'),
    text: getCSSColor('--color-text'),
    accent: getCSSColor('--color-accent'),
  }), []);

  // ... then use colors.border instead of '#21262d' etc.
  return (
    <ResponsiveContainer width="100%" height={250}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke={colors.border} />
        <XAxis dataKey="time" tick={{ fill: colors.textMuted, fontSize: 11 }} stroke={colors.border} />
        <YAxis tick={{ fill: colors.textMuted, fontSize: 11 }} stroke={colors.border} domain={['auto', 'auto']} />
        <Tooltip contentStyle={{
          background: colors.card,
          border: `1px solid ${colors.borderLight}`,
          color: colors.text,
          fontFamily: 'monospace',
        }} />
        <Line type="monotone" dataKey="price" stroke={colors.accent} strokeWidth={2} dot={false}
          activeDot={{ r: 4, fill: colors.accent }} />
      </LineChart>
    </ResponsiveContainer>
  );
}
```

### Example 3: Toast with Enter/Exit Animation

```jsx
function Toast({ message, type = 'info', duration = 10000, onClose, style }) {
  const [dismissing, setDismissing] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setDismissing(true), duration);
    return () => clearTimeout(timer);
  }, [duration]);

  const handleAnimationEnd = () => {
    if (dismissing) onClose();
  };

  return (
    <div
      className={`fixed right-4 z-50 bg-card border ${colors[type]} rounded px-4 py-3 font-mono text-sm shadow-lg ${
        dismissing ? 'animate-fade-out' : 'animate-slide-in-right'
      }`}
      style={style}
      onAnimationEnd={handleAnimationEnd}
    >
      {message}
      <Button variant="ghost" size="xs" onClick={() => setDismissing(true)} type="button" className="ml-3">
        x
      </Button>
    </div>
  );
}
```

## Detailed Component Audit

### Files That Need Changes

#### UI Primitives (frontend/src/components/ui/)
| File | Changes | Requirement |
|------|---------|-------------|
| `Modal.jsx` | Add enter/exit animation (fade backdrop + scale card) | VIS-02 |
| `Button.jsx` | Add `active:scale-[0.97]` and ensure `transition-all duration-150` | VIS-04 |

#### Components (frontend/src/components/)
| File | Changes | Requirement |
|------|---------|-------------|
| `Toast.jsx` | Add slide-in enter, fade-out exit animation with dismissing state | VIS-03 |
| `PriceChart.jsx` | Replace 6 hardcoded hex colors with CSS custom property reads | VIS-08 |
| `PriceTable.jsx` | Add flash animation when coin prices change via SSE | VIS-07 |

#### Pages (frontend/src/pages/)
| File | Changes | Requirement |
|------|---------|-------------|
| `PricesPage.jsx` | Typography/spacing standardization | VIS-05, VIS-06 |
| `PortfolioPage.jsx` | Typography/spacing standardization | VIS-05, VIS-06 |
| `WatchlistPage.jsx` | Typography/spacing standardization | VIS-05, VIS-06 |
| `AlertsPage.jsx` | Typography/spacing standardization | VIS-05, VIS-06 |

#### App Shell
| File | Changes | Requirement |
|------|---------|-------------|
| `App.jsx` | Add page transition wrapper using `useLocation` + key | VIS-01 |
| `index.css` | Add `@keyframes` and `--animate-*` theme variables | VIS-01-VIS-07 |

### Current Typography Audit

| Element | Current Classes | Location |
|---------|----------------|----------|
| App title (h1) | `text-2xl font-bold` | App.jsx |
| Page headings (h2) | `text-lg font-bold` | PortfolioPage, WatchlistPage, AlertsPage |
| Section headings (h3) | `text-sm font-bold uppercase` | AlertsPage |
| Body text / table data | `text-sm` | Throughout |
| Meta / labels | `text-xs` | Labels, timestamps, badges |
| Modal coin name | `text-2xl font-bold` | CoinModal |
| EmptyState title | `text-lg` | EmptyState |
| EmptyState description | `text-sm` | EmptyState |
| Bottom nav | `text-xs font-medium` | BottomNav |
| Top nav tabs | `text-sm` | NavTab |

**Assessment:** Typography is already reasonably consistent. The scale in use is: `text-xs` (labels/meta), `text-sm` (body/nav), `text-lg` (page headings/empty state), `text-2xl` (app title/modal title). This is a sensible 4-level hierarchy. The main inconsistency is that AlertsPage h3 uses `text-sm uppercase` while it could use a dedicated subheading size.

**Recommended typography scale:**
- **Display/title:** `text-2xl font-bold` (app title, modal coin name)
- **Page heading:** `text-lg font-bold` (h2 on each page)
- **Section heading:** `text-sm font-bold uppercase tracking-wide text-text-muted` (h3 section dividers)
- **Body:** `text-sm` (default body, table cells, nav)
- **Caption/meta:** `text-xs` (labels, timestamps, badges, bottom nav)

### Current Spacing Audit

| Context | Current Values | Assessment |
|---------|----------------|------------|
| Page padding | `px-5 pb-20 md:pb-0` (App.jsx) | Consistent |
| Header padding | `p-5` | Matches page padding |
| Card padding | `p-3` | Consistent across all cards |
| Form bottom margin | `mb-4` | Consistent |
| Section gaps | `mt-6` (AlertsPage sections), `mt-4` (Portfolio summary) | Slightly inconsistent -- recommend `mt-6` for sections |
| Page heading margin | `mb-4` | Consistent |
| Card list spacing | `space-y-2` (cards), `space-y-3` (AlertList) | Slightly inconsistent -- AlertList uses `space-y-3` |
| Inline element gap | `gap-1`, `gap-2`, `gap-3` | Used appropriately at different scales |
| Nav gap | `gap-1` (top nav) | Fine for tabs |

**Assessment:** Spacing is mostly consistent. The few inconsistencies are:
1. `space-y-2` vs `space-y-3` for card lists (AlertList uses 3, others use 2)
2. `mt-6` vs `mt-4` for section separators

**Recommendation:** Standardize card list spacing to `space-y-2` and section margins to `mt-6`. These are minor adjustments.

### PriceChart Hex Color Mapping

| Hardcoded Hex | CSS Custom Property | Used For |
|---------------|-------------------|----------|
| `#21262d` | `--color-border` | CartesianGrid stroke, XAxis stroke, YAxis stroke |
| `#8b949e` | `--color-text-muted` | XAxis tick fill, YAxis tick fill |
| `#161b22` | `--color-card` | Tooltip background |
| `#30363d` | `--color-border-light` | Tooltip border |
| `#c9d1d9` | `--color-text` | Tooltip text color |
| `#58a6ff` | `--color-accent` | Line stroke, activeDot fill |

All 6 hex values map exactly to existing custom properties. No new properties needed.

### SSE Data Flow for Price Flash (VIS-07)

1. `PricesPage` creates SSE connection via `useSSE('/api/prices/stream?exchange=...')`
2. `useSSE` hook returns `{ data, connected }` -- `data` updates on each `prices` event
3. `PricesPage` stores `data` in `prices` state via `useEffect` on `sseData`
4. `PricesPage` passes `prices.coins` to `<PriceTable coins={prices.coins} />`
5. `PriceTable` receives new `coins` array prop each time SSE delivers data

**For flash:** PriceTable needs to compare `coins` prop against previous values using a `useRef`. The flash should apply to both mobile cards and desktop table rows.

### Current Modal Behavior

- Always rendered (`<CoinModal coin={selectedCoin} open={!!selectedCoin} onClose={...} />`)
- `Modal` returns `null` when `!open` (line 58)
- No animation classes at all
- Backdrop: `fixed inset-0 bg-black/70 z-40`
- Card: `bg-card border-border-light w-full h-full sm:border sm:rounded-lg sm:p-6 sm:max-w-xl sm:h-auto sm:mx-4 p-4`
- Focus trap and escape-to-close already implemented

### Current Button Behavior

- Already has `transition-colors` in base class
- Hover states defined per variant: `hover:bg-accent/80`, `hover:border-border-light`, `hover:text-down/80`, `hover:text-text`
- No active state feedback (no scale or press effect)
- No explicit `duration-*` -- uses Tailwind default (150ms)

### Current Toast Behavior

- Positioned `fixed right-4 z-50` with stacked `top` via inline `style={{ top: ... }}`
- No enter/exit animation
- Auto-dismisses via `setTimeout(onClose, duration)`
- Close button calls `onClose` directly
- Multiple toasts stack vertically with `top` offset

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Tailwind v3 `tailwind.config.js` keyframes | Tailwind v4 `@theme` directive in CSS + `@keyframes` | Tailwind v4 (2024) | Define animations directly in CSS, auto-generates `animate-*` utilities |
| React Transition Group for enter/exit | CSS-only animations + state management | Always viable, simpler | No library needed for basic transitions |
| Hardcoded `duration-200` etc. | Tailwind v4 theme-level animation variables | Tailwind v4 | `--animate-*` in `@theme` block |

## Open Questions

1. **Page transition exit animation**
   - What we know: Enter animation (fade-in on mount) is straightforward with key-based remount. Exit animation (fade-out of old page) requires keeping old content mounted during transition.
   - What's unclear: Whether exit animation is worth the complexity for this app.
   - Recommendation: Implement enter-only fade (much simpler). The enter fade alone feels polished. Exit animation adds significant complexity (AnimatePresence pattern) for minimal UX benefit.

2. **Toast stacking with animations**
   - What we know: Currently toasts stack using inline `top` style offsets. With enter/exit animations, a dismissing toast in the middle of the stack could leave a gap.
   - What's unclear: Whether to reflow remaining toasts when one exits.
   - Recommendation: Keep current stacking approach. Toasts are rare (only triggered alerts). A brief gap during exit is acceptable.

## Sources

### Primary (HIGH confidence)
- Direct codebase audit of all 24 source files in `frontend/src/`
- `index.css` -- Tailwind v4 `@theme` directive with existing custom properties
- `package.json` -- Tailwind v4.2.1, React 19.2.0, React Router 7.13.1, Recharts 3.8.0
- Tailwind CSS v4 documentation -- `@theme` supports `--animate-*` for custom animation utilities

### Secondary (MEDIUM confidence)
- Tailwind v4 `@keyframes` + `--animate-*` pattern -- verified against Tailwind v4 docs, this is the standard way to define custom animations in v4

### Tertiary (LOW confidence)
- None

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- no new dependencies, CSS-only approach well understood
- Architecture: HIGH -- all patterns use standard CSS + React patterns, no exotic techniques
- Pitfalls: HIGH -- identified from direct code analysis and known React/CSS interaction patterns
- Typography/spacing: HIGH -- derived from complete audit of every source file
- PriceChart colors: HIGH -- exact 1:1 hex-to-custom-property mapping verified

**Research date:** 2026-03-10
**Valid until:** 2026-04-10 (stable -- CSS animations and Tailwind v4 are well-established)
