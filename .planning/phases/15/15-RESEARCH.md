# Phase 15: UI Component Library - Research

**Researched:** 2026-03-09
**Domain:** React shared component extraction, Tailwind CSS utility consolidation, accessibility
**Confidence:** HIGH

## Summary

The existing frontend has 14 components and 4 pages, all using inline Tailwind CSS class strings with significant duplication. There is no `src/components/ui/` directory, no shared primitives, no `<label>` elements on any form field, and no focus-trap or Escape-to-close logic on the single modal (CoinModal). All forms except DownloadReport lack loading/disabled state during submission.

The codebase uses Tailwind CSS v4.2 with `@theme` CSS variables (not the legacy `tailwind.config.js` approach) and React 19 with react-router v7. These are current versions; no migration is needed. The component extraction is purely mechanical: identify duplicated class patterns, extract into reusable components, and replace inline usage site by site.

**Primary recommendation:** Create `frontend/src/components/ui/` with Button.jsx, Input.jsx, Table.jsx, Modal.jsx, Badge.jsx, and NavTab.jsx. Refactor all existing components to consume these primitives. Add visible labels and form loading states as part of the refactor.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| COMP-01 | Shared `<Button>` with variant props (primary, secondary, danger, ghost) | 22 inline `<button>` elements found across 10 files with 6 distinct style patterns (see Button Audit below) |
| COMP-02 | Shared `<Input>` with label, error, disabled states | 8 `<input>` elements and 2 `<select>` elements found with identical `inputClass` pattern repeated in 3 files |
| COMP-03 | Shared `<Table>`, `<Th>`, `<Td>` replacing duplicated styles | 3 tables (PriceTable, WatchlistPage, PortfolioTable) with identical `<th>` pattern repeated 22 times |
| COMP-04 | Shared `<Modal>` with Escape, click-outside, focus trap, animation | 1 existing modal (CoinModal) with click-outside but NO Escape handler, NO focus trap, NO animation |
| COMP-05 | Shared `<Badge>` for tags, status indicators, exchange labels | TAG_COLORS map in WatchlistPage and alert direction badges in AlertList are badge-like elements |
| COMP-06 | Shared `<NavTab>` replacing NavLink className logic | 4 identical NavLink className functions in App.jsx lines 25-28 |
| COMP-07 | All form fields have visible `<label>` elements | 0 `<label>` elements exist anywhere in the codebase; 0 `aria-label` attributes found |
| COMP-08 | Forms show loading/disabled during submission | Only DownloadReport has disabled+loading state; AddHoldingForm, AddAlertForm, WatchlistPage form have none |
</phase_requirements>

## Standard Stack

### Core (already installed, no new dependencies)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| React | 19.2.0 | UI framework | Already in use |
| Tailwind CSS | 4.2.1 | Utility styling | Already in use via `@tailwindcss/vite` plugin |
| react-router | 7.13.1 | Routing + NavLink | Already in use for NavTab base |

### Supporting (zero new npm installs)
No new libraries needed. All component primitives should be built with plain React + Tailwind. The project explicitly has "No Storybook" and "No component library package" in out-of-scope.

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Hand-built focus trap | focus-trap-react npm | Overkill for 1 modal; 20 lines of custom code suffices for this use case |
| Hand-built Modal animation | framer-motion npm | Overkill; CSS transitions with Tailwind `transition-*` classes handle enter/exit |
| Headless UI (Radix, etc.) | @radix-ui/react-dialog | Adds dependency for one modal; project scope says keep components in-app |

**Installation:** None required. Zero new dependencies.

## Architecture Patterns

### Recommended Project Structure
```
frontend/src/
  components/
    ui/                  # NEW - shared primitives
      Button.jsx
      Input.jsx
      Table.jsx          # exports Table, Th, Td
      Modal.jsx
      Badge.jsx
      NavTab.jsx
    AddAlertForm.jsx     # REFACTORED to use Button, Input
    AddHoldingForm.jsx   # REFACTORED to use Button, Input
    AlertList.jsx        # REFACTORED to use Badge, Button
    CoinModal.jsx        # REFACTORED to use Modal, Button
    CountdownTimer.jsx   # unchanged
    DownloadReport.jsx   # REFACTORED to use Button
    ErrorBoundary.jsx    # unchanged
    ExchangeDropdown.jsx # REFACTORED to use Input (select variant)
    InstallButton.jsx    # REFACTORED to use Button
    OfflineBanner.jsx    # unchanged
    PortfolioTable.jsx   # REFACTORED to use Table, Th, Td, Button, Input
    PriceChart.jsx       # REFACTORED to use Button
    PriceTable.jsx       # REFACTORED to use Table, Th, Td, Button
    Toast.jsx            # REFACTORED to use Button
  pages/
    AlertsPage.jsx       # minor: uses refactored children
    PortfolioPage.jsx    # minor: uses refactored children
    PricesPage.jsx       # minor: uses refactored children
    WatchlistPage.jsx    # REFACTORED to use Table, Th, Td, Button, Input, Badge
  App.jsx                # REFACTORED to use NavTab
```

### Pattern 1: Variant Props via Object Map
**What:** Button variants defined as a `variants` object mapping names to Tailwind classes.
**When to use:** Any component with visual variants (Button, Badge, Input states).
**Example:**
```jsx
const variants = {
  primary: 'bg-accent text-bg font-bold hover:bg-accent/80',
  secondary: 'bg-card border border-border text-text hover:border-border-light',
  danger: 'text-down hover:text-down/80',
  ghost: 'text-text-muted hover:text-text',
};

function Button({ variant = 'primary', size = 'md', className, ...props }) {
  const sizes = {
    sm: 'px-2.5 py-0.5 text-xs',
    md: 'px-4 py-1.5 text-sm',
  };
  return (
    <button
      className={`rounded cursor-pointer transition-colors ${variants[variant]} ${sizes[size]} ${className || ''}`}
      {...props}
    />
  );
}
```

### Pattern 2: Compound Components for Tables
**What:** Table, Th, Td as separate named exports from one file.
**When to use:** Table primitive triplet used together.
**Example:**
```jsx
export function Table({ className, ...props }) {
  return <table className={`w-full ${className || ''}`} {...props} />;
}

export function Th({ align = 'left', className, ...props }) {
  return (
    <th
      className={`text-text-muted text-xs uppercase py-1.5 px-3 border-b border-border text-${align} ${className || ''}`}
      {...props}
    />
  );
}

export function Td({ align = 'left', className, ...props }) {
  return (
    <td
      className={`py-1.5 px-3 text-${align} ${className || ''}`}
      {...props}
    />
  );
}
```

### Pattern 3: Modal with Escape + Click-Outside + Focus Trap
**What:** Modal wrapper that handles backdrop click, Escape key, and focus cycling.
**When to use:** CoinModal and any future modals.
**Example:**
```jsx
function Modal({ open, onClose, children }) {
  const modalRef = useRef(null);

  useEffect(() => {
    if (!open) return;
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [open, onClose]);

  // Focus trap: cycle Tab within modal
  useEffect(() => {
    if (!open || !modalRef.current) return;
    const focusable = modalRef.current.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    if (focusable.length) focusable[0].focus();

    const handleTab = (e) => {
      if (e.key !== 'Tab' || !focusable.length) return;
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    };
    document.addEventListener('keydown', handleTab);
    return () => document.removeEventListener('keydown', handleTab);
  }, [open]);

  if (!open) return null;
  return (
    <div className="fixed inset-0 bg-black/70 z-40 flex items-center justify-center" onClick={onClose}>
      <div ref={modalRef} className="bg-card border border-border-light rounded-lg p-6 max-w-xl w-full mx-4 relative z-50" onClick={(e) => e.stopPropagation()}>
        {children}
      </div>
    </div>
  );
}
```

### Anti-Patterns to Avoid
- **Passing full className strings to primitives:** Components should accept `variant`/`size` props, not raw Tailwind classes. Use `className` prop only for truly one-off overrides (like width constraints).
- **Building a "kitchen sink" component:** Each primitive does ONE thing. Don't add form validation logic to Input; don't add table sorting to Table.
- **Breaking existing behavior during refactor:** Each component swap must be visually pixel-identical. Do not change colors, spacing, or layout during this phase.

## Detailed Component Audit

### BUTTON AUDIT (COMP-01)

**22 total `<button>` elements found across 10 files. 6 distinct style patterns:**

#### Pattern A: Primary Action (submit buttons)
Used in: AddHoldingForm:72, AddAlertForm:67, WatchlistPage:155
```
bg-accent text-bg font-bold rounded px-4 py-1.5 text-sm hover:bg-accent/80 cursor-pointer
```
Maps to: `variant="primary" size="md"`

#### Pattern B: Secondary/Outline
Used in: DownloadReport:28, InstallButton:11
```
px-3 py-1.5 bg-card border border-border rounded text-sm text-text hover:border-border-light disabled:opacity-50 cursor-pointer  (DownloadReport)
px-3 py-1.5 bg-accent/20 border border-accent/40 rounded text-sm text-accent hover:bg-accent/30 cursor-pointer  (InstallButton)
```
Maps to: `variant="secondary"` and `variant="ghost"` (or a custom "accent-ghost")

#### Pattern C: Danger/Destructive (text-only)
Used in: PortfolioTable:158, WatchlistPage:281, AlertList:40, AlertsPage:76
```
text-down hover:text-down/80 text-xs cursor-pointer  (Delete, Remove, Clear All)
```
Maps to: `variant="danger" size="sm"`

#### Pattern D: Link-style action (text-only colored)
Used in: PortfolioTable:137 (Save), PortfolioTable:151 (Edit), WatchlistPage:275 (Edit Tags), WatchlistPage:232 (Save)
```
text-up hover:text-up/80 text-xs cursor-pointer  (Save)
text-accent hover:text-accent/80 text-xs cursor-pointer  (Edit, Edit Tags)
text-text-muted hover:text-text text-xs cursor-pointer  (Cancel, Clear)
```
Maps to: `variant="ghost" size="sm"` with color override, or dedicated ghost variants

#### Pattern E: Toggle/Period selector
Used in: PriceChart:39-56 (7D/30D buttons)
```
px-2.5 py-0.5 rounded text-xs cursor-pointer ${active ? 'bg-accent text-bg' : 'bg-border text-text-muted hover:text-text'}
```
Maps to: `variant="primary" size="sm"` when active, `variant="ghost" size="sm"` when inactive; or a dedicated toggle pattern

#### Pattern F: Small utility button
Used in: PricesPage:65 (Refresh)
```
bg-border border border-border-light rounded px-2.5 py-0.5 text-text hover:border-accent hover:text-accent text-xs cursor-pointer
```
Maps to: `variant="secondary" size="sm"`

#### Pattern G: Star toggle (icon button)
Used in: PriceTable:66
```
cursor-pointer text-sm transition-colors ${isWatched ? 'text-yellow-400' : 'text-text-dim hover:text-yellow-400/60'}
```
Special case: icon-only button, may need `variant="icon"` or just pass className

#### Pattern H: Modal close button
Used in: CoinModal:23, Toast:21
```
text-text-muted hover:text-text text-xl cursor-pointer  (CoinModal close)
text-text-muted hover:text-text cursor-pointer  (Toast close)
```
Maps to: `variant="ghost"` (icon-style close)

#### Pattern I: Modal CTA
Used in: CoinModal:60
```
bg-accent/20 text-accent border border-accent/30 rounded px-3 py-1 text-sm hover:bg-accent/30 cursor-pointer
```
Maps to: `variant="secondary"` with accent coloring -- or a new "outline" variant

### INPUT AUDIT (COMP-02)

**Shared `inputClass` pattern repeated in 3 files:**
```
bg-bg border border-border rounded px-3 py-1.5 text-text text-sm focus:border-accent focus:outline-none
```

| File | Line | Type | Placeholder | Extra Classes | Has Label? |
|------|------|------|-------------|---------------|------------|
| AddHoldingForm.jsx | 37-42 | text | "Symbol" | `w-24 uppercase` | NO |
| AddHoldingForm.jsx | 45-50 | number | "Amount" | `w-28` | NO |
| AddHoldingForm.jsx | 55-60 | number | "Buy Price EUR" | `w-32` | NO |
| AddHoldingForm.jsx | 65-69 | date | (none) | `w-36` | NO |
| AddAlertForm.jsx | 41-46 | text | "Symbol" | `w-24 uppercase` | NO |
| AddAlertForm.jsx | 48-55 | number | "Target Price EUR" | `w-36` | NO |
| AddAlertForm.jsx | 58-63 | select | (n/a) | (none) | NO |
| WatchlistPage.jsx | 132-138 | text | "Symbol" | `w-24 uppercase` | NO |
| PortfolioTable.jsx | 117-124 | number (inline edit) | (none) | `w-20 text-xs` -- different size pattern | NO |
| ExchangeDropdown.jsx | 3-7 | select | (n/a) | custom bg-border style | NO |

**Zero `<label>` elements in the entire codebase.** All form fields use placeholder text only.
**Zero `aria-label` attributes anywhere.**

### TABLE AUDIT (COMP-03)

**3 tables with identical `<th>` pattern:**

**TH pattern (repeated 22 times):**
```
text-text-muted text-left text-xs uppercase py-1.5 px-3 border-b border-border
```
Variations: `text-right` (for numeric columns), `text-center` (for action columns), `w-8` (for star column)

| Component | Headers | Alignment Pattern |
|-----------|---------|-------------------|
| PriceTable.jsx (lines 44-52) | [star], #, Symbol, Name, Price, 24h%, Volume | center, left, left, left, right, right, right |
| WatchlistPage.jsx (lines 200-208) | Symbol, Name, Tags, Price, 24h%, Volume, [actions] | left, left, left, right, right, right, center |
| PortfolioTable.jsx (lines 74-83) | Symbol, Amount, Avg Buy, Current, Value, P&L EUR, P&L %, Alloc % | left, right, right, right, right, right, right, right |

**TD pattern (repeated ~30 times):**
```
py-1.5 px-3 [alignment] [color classes]
```

**TR pattern:**
```
cursor-pointer hover:bg-card border-b border-border/50  (clickable rows in PriceTable, PortfolioTable)
border-b border-border/50  (non-clickable rows in WatchlistPage)
```

### MODAL AUDIT (COMP-04)

**1 existing modal: CoinModal.jsx**

Current features:
- Click-outside-to-close: YES (line 15, onClick={onClose} on backdrop)
- Escape-to-close: NO
- Focus trap: NO
- Enter animation: NO
- Exit animation: NO
- Backdrop: `fixed inset-0 bg-black/70 z-40`
- Content: `bg-card border border-border-light rounded-lg p-6 max-w-xl w-full mx-4 relative z-50`
- Close button: `absolute top-3 right-4` with "x" text

The modal is rendered conditionally: `{selectedCoin && <CoinModal ... />}` in PricesPage.jsx:74.
For animation support, the Modal wrapper should always be rendered and use an `open` prop to control visibility with CSS transitions.

### BADGE AUDIT (COMP-05)

**Badge-like elements found in 2 files:**

#### WatchlistPage TAG_COLORS map (line 6-12):
```jsx
const TAG_COLORS = {
  Layer1: 'bg-blue-900/50 text-blue-300 border-blue-700',
  Layer2: 'bg-purple-900/50 text-purple-300 border-purple-700',
  DeFi: 'bg-green-900/50 text-green-300 border-green-700',
  Meme: 'bg-yellow-900/50 text-yellow-300 border-yellow-700',
  Exchange: 'bg-orange-900/50 text-orange-300 border-orange-700',
  Privacy: 'bg-red-900/50 text-red-300 border-red-700',
};
```

Used as:
- Tag display (line 249): `px-1.5 py-0.5 rounded text-xs border ${TAG_COLORS[tag]}`
- Tag toggle button (line 146): `px-2 py-0.5 rounded text-xs border cursor-pointer transition-opacity ${TAG_COLORS[tag]} ${selected ? 'opacity-100 ring-1 ring-accent' : 'opacity-50'}`
- Tag filter pill (line 172): `px-2.5 py-1 rounded-full text-xs border cursor-pointer transition-all ${TAG_COLORS[tag]} ${active ? 'opacity-100 ring-1 ring-accent' : 'opacity-40 hover:opacity-70'}`

#### AlertList direction badge (line 19-24):
```jsx
<span className={`rounded px-2 py-0.5 text-xs ${
  alert.direction === 'above' ? 'text-up bg-up/10' : 'text-down bg-down/10'
}`}>
```

Badge variants needed:
1. **Tag badge** (static display): colored background, border, small text
2. **Status badge** (alert direction): semantic color (up/down)
3. TAG_COLORS should move into Badge component or a shared constants file

### NAVTAB AUDIT (COMP-06)

**App.jsx lines 25-28 -- 4 identical NavLink className functions:**

```jsx
<NavLink to="/" end className={({isActive}) =>
  `px-4 py-1.5 rounded-t border text-sm ${
    isActive
      ? 'bg-card border-border-light text-text'
      : 'bg-border border-border text-text-muted hover:text-text'
  }`
}>Prices</NavLink>
```

This exact pattern is repeated 4 times (Prices, Watchlist, Portfolio, Alerts).

NavTab component should:
- Accept `to`, `end` (boolean), and `children` props
- Wrap `<NavLink>` with the shared className function
- Eliminate the 4x duplication in App.jsx

### LABEL AUDIT (COMP-07)

**Zero `<label>` elements. Zero `aria-label` attributes.**

Forms that need labels:
| Form | Fields Needing Labels |
|------|----------------------|
| AddHoldingForm | Symbol, Amount, Buy Price EUR, Buy Date |
| AddAlertForm | Symbol, Target Price EUR, Direction |
| WatchlistPage (add form) | Symbol |
| PortfolioTable (inline edit) | Amount (inline -- could use aria-label instead) |
| ExchangeDropdown | Exchange (standalone select) |

Strategy: The shared `<Input>` component should ALWAYS render a `<label>`. The `placeholder` prop is kept for UX but the label is the primary accessible name. Labels should be visually styled as small text above the input (e.g., `text-text-muted text-xs mb-0.5 block`).

### FORM LOADING STATE AUDIT (COMP-08)

| Form | Submit Handler | Has Loading State? | Has Disabled on Submit? |
|------|----------------|--------------------|------------------------|
| AddHoldingForm | handleSubmit (line 12) | NO | NO |
| AddAlertForm | handleSubmit (line 17) | NO | NO |
| WatchlistPage (add form) | handleAdd (line 52) | NO | NO |
| DownloadReport | handleDownload (line 6) | YES (`loading` state) | YES (`disabled={loading}`) |
| PortfolioTable (inline edit) | handleEditLot (line 47) | NO | NO |

Strategy: Add `loading`/`submitting` state to each form. The submit `<Button>` should accept a `loading` prop that disables it and shows "Submitting..." or a spinner.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Class merging | String concatenation everywhere | Simple template literal helper or just careful ordering | Keep it simple; no `clsx`/`cn` dependency needed since patterns are predictable |
| Focus trap | Full accessibility trap library | 20-line useEffect cycling through focusable elements | Only 1 modal; no complex nested focus scenarios |
| CSS transitions for modal | JS animation library | Tailwind `transition-*` + `opacity-*` + `scale-*` classes with conditional rendering | Phase 18 (VIS-02) handles proper animation later; phase 15 just needs structural support |

**Key insight:** This is a small codebase (14 components). Every "don't hand-roll" item is simple enough to build inline. The complexity risk is in breaking existing visual behavior during refactor, not in the primitives themselves.

## Common Pitfalls

### Pitfall 1: Breaking Visual Parity During Refactor
**What goes wrong:** Replacing inline classes with a shared component subtly changes spacing, colors, or hover states.
**Why it happens:** Missing a class in the variant map, or adding default classes that conflict with existing layout.
**How to avoid:** Side-by-side screenshot comparison before/after each component swap. Each file change should be independently verifiable.
**Warning signs:** Any visual diff in the browser dev tools.

### Pitfall 2: Tailwind v4 Class String Construction
**What goes wrong:** Dynamic class construction like `` `text-${align}` `` does not work with Tailwind's JIT compiler -- it needs to see full class names to include them in the build.
**Why it happens:** Tailwind scans source files for class strings at build time.
**How to avoid:** Use explicit mapping objects: `{ left: 'text-left', right: 'text-right', center: 'text-center' }` instead of template literals for Tailwind classes.
**Warning signs:** Classes present in source but styles missing in production build.

### Pitfall 3: Modal Focus Trap Breaking on Rerender
**What goes wrong:** `querySelectorAll` captures focusable elements once, but React rerenders may add/remove elements.
**Why it happens:** Focus trap initialized in useEffect with stale closure.
**How to avoid:** Re-query focusable elements on each Tab keypress, not just on mount.
**Warning signs:** Tab cycling skips dynamically added buttons or inputs.

### Pitfall 4: Button `type` Default
**What goes wrong:** `<Button>` inside a `<form>` submits the form unexpectedly because HTML `<button>` defaults to `type="submit"`.
**Why it happens:** Forgot to set `type="button"` on non-submit buttons.
**How to avoid:** Button component should NOT default `type` -- pass through props. Document that tag toggle buttons, period buttons, etc. need `type="button"`.
**Warning signs:** Clicking "Cancel" or "Edit Tags" submits the form.

### Pitfall 5: NavLink `end` Prop
**What goes wrong:** The "/" route stays active when navigating to "/watchlist" etc.
**Why it happens:** Missing `end` prop on the root NavLink.
**How to avoid:** NavTab component must pass through the `end` prop to NavLink. The Prices tab currently uses `end` on line 25 of App.jsx.
**Warning signs:** "Prices" tab highlighted on all pages.

### Pitfall 6: Inline Edit Input in PortfolioTable
**What goes wrong:** The inline edit input in PortfolioTable (line 117-124) has a completely different style from the form inputs.
**Why it happens:** It's a tiny inline editor inside a table cell, not a form field.
**How to avoid:** Either use a `size="xs"` variant of Input, or keep it as a special case with a className override. Don't force full label+error treatment on an inline edit cell.
**Warning signs:** Inline edit input looks oversized or gains an unwanted label.

## Code Examples

### Button Component (verified pattern from codebase analysis)
```jsx
// frontend/src/components/ui/Button.jsx
const variants = {
  primary: 'bg-accent text-bg font-bold hover:bg-accent/80',
  secondary: 'bg-card border border-border text-text hover:border-border-light',
  danger: 'text-down hover:text-down/80',
  ghost: 'text-text-muted hover:text-text',
};

const sizes = {
  xs: 'px-1 py-0.5 text-xs',
  sm: 'px-2.5 py-0.5 text-xs',
  md: 'px-4 py-1.5 text-sm',
};

export function Button({
  variant = 'primary',
  size = 'md',
  loading = false,
  className = '',
  children,
  disabled,
  ...props
}) {
  return (
    <button
      className={`rounded cursor-pointer transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${variants[variant]} ${sizes[size]} ${className}`}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? 'Submitting...' : children}
    </button>
  );
}
```

### Input Component (verified pattern from codebase analysis)
```jsx
// frontend/src/components/ui/Input.jsx
export function Input({
  label,
  error,
  className = '',
  id,
  ...props
}) {
  const inputId = id || label?.toLowerCase().replace(/\s+/g, '-');
  return (
    <div className={className}>
      {label && (
        <label htmlFor={inputId} className="text-text-muted text-xs mb-0.5 block">
          {label}
        </label>
      )}
      <input
        id={inputId}
        className={`bg-bg border rounded px-3 py-1.5 text-text text-sm focus:border-accent focus:outline-none w-full ${
          error ? 'border-down' : 'border-border'
        }`}
        {...props}
      />
      {error && <p className="text-down text-xs mt-0.5">{error}</p>}
    </div>
  );
}
```

### Usage: Replacing AddHoldingForm
```jsx
// Before:
<input type="text" placeholder="Symbol" value={symbol}
  onChange={(e) => setSymbol(e.target.value)}
  className={`${inputClass} w-24 uppercase`} required />

// After:
<Input label="Symbol" type="text" placeholder="BTC" value={symbol}
  onChange={(e) => setSymbol(e.target.value)}
  className="w-24" style={{ textTransform: 'uppercase' }} required />
```

### Usage: Replacing NavLink in App.jsx
```jsx
// Before (repeated 4x):
<NavLink to="/" end className={({isActive}) => `px-4 py-1.5 rounded-t border text-sm ${isActive ? 'bg-card border-border-light text-text' : 'bg-border border-border text-text-muted hover:text-text'}`}>Prices</NavLink>

// After:
<NavTab to="/" end>Prices</NavTab>
<NavTab to="/watchlist">Watchlist</NavTab>
<NavTab to="/portfolio">Portfolio</NavTab>
<NavTab to="/alerts">Alerts</NavTab>
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `tailwind.config.js` theme | `@theme` CSS custom properties in `index.css` | Tailwind v4 (early 2025) | Theme vars defined in CSS, not JS; no config file needed |
| React Router v6 `<Routes>` | react-router v7 (same API) | 2025 | NavLink API unchanged; `className` function prop still works |
| `clsx` / `classnames` for merging | Template literals | Always | For predictable variants, template literals are sufficient |

**Deprecated/outdated:**
- `tailwind.config.js`: This project uses Tailwind v4's `@theme` block in CSS. Do NOT create a tailwind.config.js.
- `className` prop on NavLink as a string: In react-router v7, it accepts a function `({isActive}) => string`. This is what the codebase already uses.

## Design Token Reference

The theme is defined in `frontend/src/index.css` using Tailwind v4 `@theme`:

| Token | Value | Tailwind Class | Usage |
|-------|-------|----------------|-------|
| `--color-bg` | `#0d1117` | `bg-bg`, `text-bg` | Page background, button text on primary |
| `--color-card` | `#161b22` | `bg-card` | Card/panel backgrounds, active tab |
| `--color-border` | `#21262d` | `border-border` | Default borders |
| `--color-border-light` | `#30363d` | `border-border-light` | Hover/active borders |
| `--color-accent` | `#58a6ff` | `text-accent`, `bg-accent` | Links, primary actions, active states |
| `--color-text` | `#c9d1d9` | `text-text` | Primary text |
| `--color-text-muted` | `#8b949e` | `text-text-muted` | Secondary text, labels, headers |
| `--color-text-dim` | `#6e7681` | `text-text-dim` | Tertiary text, subtle info |
| `--color-up` | `#3fb950` | `text-up`, `bg-up` | Positive values, success |
| `--color-down` | `#f85149` | `text-down`, `bg-down` | Negative values, danger, errors |

**Font:** `--font-mono` (monospace stack) -- used globally via `font-mono` on body.

## Open Questions

1. **Should `<Input>` handle `<select>` as well, or have a separate `<Select>` component?**
   - What we know: There are 2 select elements (ExchangeDropdown, AddAlertForm direction). Both use the same base inputClass pattern.
   - What's unclear: Whether a single `Input` component with an `as="select"` prop is cleaner than a separate Select.
   - Recommendation: Create a single `Input` component for text/number/date inputs, and keep selects as their own thing or add a thin `Select` wrapper with the same styling. The simplest approach is to just extract the shared base classes and let ExchangeDropdown and AddAlertForm use them directly.

2. **Should TAG_COLORS live inside Badge or in a shared constants file?**
   - What we know: TAG_COLORS is currently in WatchlistPage and used in 3 places within that file.
   - What's unclear: Whether other pages will need these colors.
   - Recommendation: Move TAG_COLORS into Badge.jsx as a `colorScheme` prop mapping. The Badge component can accept `colorScheme="blue"` etc., with the tag-to-color mapping staying in WatchlistPage.

3. **How to handle the inline edit input in PortfolioTable?**
   - What we know: It's a tiny number input inside a table cell (line 117-124), with different sizing (`text-xs w-20 px-1 py-0.5`).
   - Recommendation: Use the shared Input component with a `size="xs"` prop and no label (use `aria-label` instead). Or keep it as a special case with direct className usage since it is fundamentally different from the form inputs.

## Validation Architecture

> Note: `workflow.nyquist_validation` is not present in config.json. Treating as enabled.

### Test Framework
| Property | Value |
|----------|-------|
| Framework | None detected for frontend (no jest/vitest config, no test files) |
| Config file | none -- see Wave 0 |
| Quick run command | `cd frontend && npx vitest run --reporter=verbose` |
| Full suite command | `cd frontend && npx vitest run` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| COMP-01 | Button renders variants correctly | unit | `cd frontend && npx vitest run src/components/ui/__tests__/Button.test.jsx` | Wave 0 |
| COMP-02 | Input renders label, error, disabled states | unit | `cd frontend && npx vitest run src/components/ui/__tests__/Input.test.jsx` | Wave 0 |
| COMP-03 | Table/Th/Td render with correct classes | unit | `cd frontend && npx vitest run src/components/ui/__tests__/Table.test.jsx` | Wave 0 |
| COMP-04 | Modal handles Escape, click-outside, focus trap | unit | `cd frontend && npx vitest run src/components/ui/__tests__/Modal.test.jsx` | Wave 0 |
| COMP-05 | Badge renders color schemes | unit | `cd frontend && npx vitest run src/components/ui/__tests__/Badge.test.jsx` | Wave 0 |
| COMP-06 | NavTab renders active/inactive states | unit | `cd frontend && npx vitest run src/components/ui/__tests__/NavTab.test.jsx` | Wave 0 |
| COMP-07 | Form fields have visible labels | unit | `cd frontend && npx vitest run src/components/__tests__/AddHoldingForm.test.jsx` | Wave 0 |
| COMP-08 | Submit buttons disabled during loading | unit | `cd frontend && npx vitest run src/components/__tests__/AddAlertForm.test.jsx` | Wave 0 |

### Sampling Rate
- **Per task commit:** `cd frontend && npx vitest run --reporter=verbose`
- **Per wave merge:** `cd frontend && npx vitest run`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] Install vitest + @testing-library/react + @testing-library/jest-dom + jsdom: `cd frontend && npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom`
- [ ] Create `frontend/vitest.config.js` with jsdom environment
- [ ] Create `frontend/src/components/ui/__tests__/` directory
- [ ] Create test files for each UI primitive

## Sources

### Primary (HIGH confidence)
- Direct codebase analysis of all 14 components + 4 pages + 3 hooks + 1 lib file
- `frontend/src/index.css` -- Tailwind v4 `@theme` configuration with all design tokens
- `frontend/package.json` -- exact dependency versions (React 19.2, Tailwind 4.2, react-router 7.13)
- `frontend/vite.config.js` -- build configuration and plugin setup

### Secondary (MEDIUM confidence)
- Tailwind v4 `@theme` documentation pattern (verified in codebase)
- react-router v7 NavLink API (verified in codebase usage)

### Tertiary (LOW confidence)
- None. All findings are from direct codebase inspection.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - all versions read directly from package.json
- Architecture: HIGH - component audit is complete and exhaustive (every JSX file read)
- Pitfalls: HIGH - based on actual code patterns found in the codebase (e.g., dynamic Tailwind class construction, button type defaults)
- Validation: MEDIUM - vitest recommended based on Vite ecosystem standard, but no existing test infrastructure to build on

**Research date:** 2026-03-09
**Valid until:** 2026-04-09 (stable -- no fast-moving dependencies)
