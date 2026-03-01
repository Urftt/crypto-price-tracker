# Phase 6: Add Portfolio Tracking to the Crypto Tracker - Context

**Gathered:** 2026-03-01
**Status:** Ready for planning

<domain>
## Phase Boundary

Add portfolio tracking to the crypto price tracker. Users can record their crypto holdings (trades with full history), view portfolio value with profit/loss and allocation breakdown, and manage holdings from both CLI and web interfaces. This phase delivers the portfolio data layer, CLI subcommands, web page with CRUD form, and API endpoints to support it.

</domain>

<decisions>
## Implementation Decisions

### Holdings Management
- Both CLI and web interfaces for adding/editing/removing holdings
- Full trade history per holding: coin symbol, quantity, buy price, purchase date, and fees
- Single portfolio per installation (no multi-portfolio support)
- Validate coin symbols against the Bitvavo API when adding — reject unknown symbols to prevent typos

### Portfolio Display
- Show both value/P&L metrics AND allocation percentages — comprehensive view
- CLI: color-coded rich table matching existing `crypto prices` style (green profit, red loss)
- Columns: coin, quantity, avg buy price, current price, current value, P/L (EUR), P/L%, allocation%
- Total portfolio summary row at bottom
- Web: separate dedicated portfolio page (not integrated into price dashboard)
- Web portfolio page includes summary cards (total value, total P/L) and holdings table

### Web Interface
- Navigation bar with "Prices" and "Portfolio" tabs for switching between views
- Full CRUD form on web portfolio page — add, edit, and remove holdings directly from browser
- Portfolio values auto-refresh on the same 30-second cycle as the price table

### Data Storage
- JSON file for persistence — no database dependency
- No import/export functionality for now (users can manually copy the JSON file)

### CLI Commands
- Grouped under `crypto portfolio` subcommand:
  - `crypto portfolio` — show portfolio overview
  - `crypto portfolio add` — add a new trade/holding
  - `crypto portfolio remove` — remove a trade/holding

### Claude's Discretion
- Edit/remove approach for holdings (IDs, interactive selection, etc.)
- JSON file location (follow Python/platform conventions)
- REST API endpoint design for web CRUD operations
- Loading states and error handling for portfolio operations
- Exact web form layout and interaction patterns

</decisions>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 06-add-portfolio-tracking-to-the-crypto-tracker*
*Context gathered: 2026-03-01*
