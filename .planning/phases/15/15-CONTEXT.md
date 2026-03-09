# Phase 15: UI Component Library — Context

**Phase:** 15
**Goal:** Extract shared, accessible UI primitives that eliminate style duplication and improve form UX
**Requirements:** COMP-01 through COMP-08

## Requirements Summary

| ID | Description |
|----|-------------|
| COMP-01 | Shared `<Button>` with variant props (primary, secondary, danger, ghost) replacing all inline button styles |
| COMP-02 | Shared `<Input>` with label, error state, disabled state replacing all inline input styles |
| COMP-03 | Shared `<Table>`, `<Th>`, `<Td>` replacing duplicated table cell styles across 3 tables |
| COMP-04 | Shared `<Modal>` with Escape-to-close, click-outside, focus trap, enter/exit animation |
| COMP-05 | Shared `<Badge>` for tags, status indicators, exchange labels |
| COMP-06 | Shared `<NavTab>` replacing duplicated NavLink className logic in App.jsx |
| COMP-07 | All form fields have visible `<label>` elements (not just placeholder text) |
| COMP-08 | Forms show loading/disabled state during submission (prevent double-submit) |

## Success Criteria

1. Button, Input, Table/Th/Td, Modal, Badge, NavTab components exist in `src/components/ui/`
2. All forms use `<Input>` with visible labels (not just placeholders)
3. All buttons use `<Button>` with consistent variants
4. Modal supports Escape key, click-outside, and focus trap
5. No duplicate `inputClass` or button style strings remain anywhere in the codebase
6. All 271+ existing tests still pass

## Constraints

- Zero new npm dependencies for components (vitest/testing-library for tests only)
- Visual output must be pixel-identical after refactor (no color/spacing changes)
- Tailwind v4 with `@theme` CSS variables — no tailwind.config.js
- React 19 + react-router v7 — use existing patterns
- Frontend-only changes (no backend modifications)

## Key Decisions

1. **Input vs Select:** Keep Input for text/number/date inputs. Selects keep their existing patterns (only 2 exist).
2. **TAG_COLORS:** Badge accepts a `colorScheme` prop; tag-to-color mapping stays in WatchlistPage.
3. **Inline edit input:** Use Input with `size="xs"` and `aria-label` instead of visible label.
4. **Focus trap:** Hand-built 20-line useEffect (no library needed for 1 modal).
5. **Modal animation:** Structural support only (always-rendered with `open` prop); actual animation in Phase 18.

## Research Reference

Full audit: `.planning/phases/15/15-RESEARCH.md`
