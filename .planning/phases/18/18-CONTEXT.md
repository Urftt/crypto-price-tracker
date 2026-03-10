# Phase 18: Visual Polish & Animations — Context

**Phase Goal:** Smooth transitions and consistent visual hierarchy make the app feel polished and professional.

**Scope:** Frontend-only. CSS animations, transitions, typography/spacing standardization, PriceChart theming.

## Requirements

| ID | Description | Notes |
|----|-------------|-------|
| VIS-01 | Page transition animations when switching tabs (subtle fade or slide) | Key-based remount with animate-fade-in on Routes wrapper; enter-only (no exit animation) |
| VIS-02 | Modal open/close animations (fade + scale) | Two-state approach: open vs visible to allow exit animation before unmount |
| VIS-03 | Toast enter/exit animations (slide in from top-right, fade out) | Add dismissing state for exit animation; onAnimationEnd triggers removal |
| VIS-04 | Button hover and active state transitions (smooth color shifts) | Already has transition-colors; add active:scale-[0.97] press feedback |
| VIS-05 | Improved typography hierarchy | Already mostly consistent 4-level scale; standardize AlertsPage h3 and sections |
| VIS-06 | Consistent spacing scale | Standardize card list spacing to space-y-2, section margins to mt-6 |
| VIS-07 | Price change flash animation on SSE update | useRef to track previous prices, animate-flash class, skip first render |
| VIS-08 | PriceChart CSS custom properties instead of hardcoded hex | 6 hex values map 1:1 to existing --color-* properties; use getComputedStyle() |

## Success Criteria

1. Tab switching has a subtle fade-in transition animation
2. Modal opens with fade+scale, closes with reverse
3. Toasts slide in and fade out
4. Buttons have smooth hover/active transitions
5. Typography uses a consistent size scale (not ad-hoc)
6. PriceChart reads theme colors from CSS custom properties
7. Price changes flash briefly when updated via SSE

## Key Decisions

- CSS-only animations — no Framer Motion or React Transition Group needed
- Tailwind v4 @theme directive for --animate-* custom animation utilities
- Enter-only page transitions (exit animation adds complexity for minimal benefit)
- getComputedStyle() for reading CSS custom properties into Recharts SVG attributes

## Research Reference

See: 18-RESEARCH.md for full codebase audit, architecture patterns, and pitfall analysis.
