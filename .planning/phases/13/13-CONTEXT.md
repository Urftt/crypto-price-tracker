# Phase 13 Context: Mobile PWA

## Goal
Make the web dashboard a Progressive Web App with manifest, service worker, offline support, and install-to-home-screen.

## Requirements

- PWA-01: Web app manifest with name, icons, theme color, standalone display mode
- PWA-02: Service worker that precaches app shell (HTML/JS/CSS) for offline access
- PWA-03: Runtime caching — NetworkFirst for API data, CacheFirst for images
- PWA-04: SSE endpoint excluded from service worker interception
- PWA-05: Offline banner shown when network unavailable, displaying last-known cached data
- PWA-06: Install-to-home-screen button in header (Chrome/Edge beforeinstallprompt)
- PWA-07: PWA icons (192x192, 512x512, 180x180 apple-touch-icon, favicon)
- PWA-08: Meta tags for theme-color, description, apple-touch-icon
- PWA-09: Build output includes manifest and service worker alongside existing assets
- PWA-10: Passes Chrome Lighthouse PWA installability check

## Success Criteria

1. `npm run build` generates manifest.webmanifest and sw.js in the static output directory
2. Chrome DevTools > Application > Manifest shows "Installable" with no errors
3. Clicking "Install" button in header triggers the browser install prompt (Chrome/Edge)
4. With network offline, app shell loads and shows last-known prices/portfolio from cache
5. An offline banner appears when disconnected; disappears when reconnected
6. SSE price streaming continues to work normally (not intercepted by service worker)
7. All existing 265+ tests continue to pass

## Technical Approach

- **vite-plugin-pwa** with `registerType: 'autoUpdate'` and `generateSW` mode
- Workbox runtime caching for `/api/*` endpoints (NetworkFirst)
- `navigateFallbackDenylist: [/^\/api\/prices\/stream/]` to protect SSE
- `useInstallPrompt` React hook for install button
- `useOffline` React hook (navigator.onLine + online/offline events) for banner
- SVG-to-PNG icons generated as static files in `frontend/public/`

## Plans

- 13-01: PWA infrastructure — plugin, manifest, service worker, icons, meta tags
- 13-02: Offline UX + install button — React hooks, offline banner, install button, tests
