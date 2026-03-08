# Phase 13 Research: Progressive Web App (PWA)

**Researched:** 2026-03-08  |  **Confidence:** HIGH

## 1. vite-plugin-pwa Setup

**Package:** `vite-plugin-pwa` v1.2.0 (supports Vite 7). Uses Workbox under the hood.

```bash
npm install -D vite-plugin-pwa
```

Add to existing `vite.config.js`:
```js
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    VitePWA({
      registerType: 'autoUpdate',
      manifest: { /* section 2 */ },
      workbox: { /* section 3 */ },
    }),
  ],
  // ...existing config
})
```

**What the plugin generates automatically:**
- Service worker (`sw.js`) that precaches all Vite build output (JS, CSS, HTML)
- `manifest.webmanifest` injected into `index.html`
- Registration script that loads the SW on page load

`registerType: 'autoUpdate'` silently updates the SW when new content deploys -- no user prompt needed.

## 2. Web App Manifest -- Required Fields

Configure in the `manifest` key of VitePWA options:

```js
manifest: {
  name: 'Crypto Price Tracker',
  short_name: 'CryptoTracker',
  description: 'Real-time crypto prices, portfolio tracking, and alerts',
  start_url: '/',
  display: 'standalone',
  theme_color: '#0f172a',
  background_color: '#0f172a',
  icons: [
    { src: 'pwa-192x192.png', sizes: '192x192', type: 'image/png' },
    { src: 'pwa-512x512.png', sizes: '512x512', type: 'image/png' },
    { src: 'pwa-512x512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
  ],
}
```

Add to `index.html` `<head>`:
```html
<meta name="description" content="Real-time crypto prices and portfolio tracker">
<meta name="theme-color" content="#0f172a">
<link rel="icon" href="/favicon.ico">
<link rel="apple-touch-icon" href="/apple-touch-icon-180x180.png" sizes="180x180">
```

## 3. Service Worker Caching Strategies

Static assets are **precached automatically**. Runtime caching handles API calls:

```js
workbox: {
  globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],
  runtimeCaching: [
    {
      urlPattern: /^\/api\/(coins|portfolio|alerts)/,
      handler: 'NetworkFirst',
      options: {
        cacheName: 'api-cache',
        expiration: { maxEntries: 50, maxAgeSeconds: 60 * 60 },
        cacheableResponse: { statuses: [0, 200] },
      },
    },
    {
      urlPattern: /^https:\/\/assets\.coingecko\.com\//,
      handler: 'CacheFirst',
      options: {
        cacheName: 'coin-images',
        expiration: { maxEntries: 100, maxAgeSeconds: 60 * 60 * 24 * 30 },
        cacheableResponse: { statuses: [0, 200] },
      },
    },
  ],
  navigateFallbackDenylist: [/^\/api\/prices\/stream/],
}
```

| Resource | Strategy | Why |
|----------|----------|-----|
| Static assets (JS/CSS) | Precache (auto) | Versioned by Vite hashes |
| `/api/coins`, `/api/portfolio` | NetworkFirst | Fresh when online, cached when offline |
| CoinGecko images | CacheFirst | Coin icons rarely change |
| `/api/prices/stream` (SSE) | **Excluded** | Persistent connection, not cacheable |

## 4. Offline Support

**Works offline (from cache):**
- Full app shell (HTML/JS/CSS) -- precached
- Last-fetched portfolio, coin list, alerts -- NetworkFirst cache
- Coin icon images -- CacheFirst cache
- Previously viewed chart data -- if cached

**Requires network:**
- Live prices via SSE -- inherently real-time
- Portfolio/alert CRUD mutations -- need backend + SQLite
- Fresh chart data for new time ranges

**UX approach:** Show a banner "You're offline -- showing last known data" when `navigator.onLine` is false or SSE disconnects. Do NOT queue offline writes -- the sync complexity is not worth it for this app.

## 5. Install Prompt

The `beforeinstallprompt` event fires when Chrome/Edge detect installability. Hook pattern:

```jsx
function useInstallPrompt() {
  const [deferredPrompt, setDeferredPrompt] = useState(null)
  const [isInstallable, setIsInstallable] = useState(false)

  useEffect(() => {
    const handler = (e) => {
      e.preventDefault()
      setDeferredPrompt(e)
      setIsInstallable(true)
    }
    window.addEventListener('beforeinstallprompt', handler)
    return () => window.removeEventListener('beforeinstallprompt', handler)
  }, [])

  const install = async () => {
    if (!deferredPrompt) return
    deferredPrompt.prompt()
    await deferredPrompt.userChoice
    setDeferredPrompt(null)
    setIsInstallable(false)
  }

  return { isInstallable, install }
}
```

Show install button in header/settings -- only renders when `isInstallable` is true. Safari does not support `beforeinstallprompt` (uses its own share menu flow).

## 6. Icon Requirements

| File | Size | Purpose |
|------|------|---------|
| `pwa-192x192.png` | 192x192 | Android home screen, splash |
| `pwa-512x512.png` | 512x512 | Android splash, install dialog |
| `apple-touch-icon-180x180.png` | 180x180 | iOS home screen |
| `favicon.ico` | 48x48 | Browser tab |

**Maskable icon:** 512x512 with `purpose: 'maskable'`. Safe zone is the inner 80% circle -- keep logo within it. Preview at https://maskable.app/editor. Use a separate file if the standard icon has edge content.

All icon files go in `frontend/public/`.

## 7. Testing PWA

**Chrome DevTools > Application tab:**
- Manifest panel: verify fields, icons, installability status
- Service Workers panel: confirm registration, inspect caches, test offline

**Manual testing checklist:**
1. Build production (`npm run build`) and serve with FastAPI
2. Application > Manifest -- confirm "Installable" with no warnings
3. Install via Chrome address bar -- app opens standalone
4. DevTools > Network > Offline -- app shell loads, cached data shows
5. Reconnect -- SSE resumes, fresh data flows

**Dev mode:** Set `devOptions: { enabled: true }` for quick iteration (SW only precaches in prod builds).

## Key Pitfalls

1. **SSE + Service Worker conflict:** SW must NOT intercept `/api/prices/stream`. Use `navigateFallbackDenylist` or SSE connections break.

2. **Maskable vs any icons:** Do not use `purpose: 'any maskable'` on one icon. Use separate entries -- one default, one maskable.

3. **Build output path:** Project builds to `../src/crypto_price_tracker/static`. FastAPI must serve `manifest.webmanifest` with `application/manifest+json` MIME type from the same origin.

4. **HTTPS requirement:** PWAs require HTTPS in production. Localhost is exempt for dev.

## Sources

- [vite-plugin-pwa Guide](https://vite-pwa-org.netlify.app/guide/)
- [vite-plugin-pwa Minimal Requirements](https://vite-pwa-org.netlify.app/guide/pwa-minimal-requirements.html)
- [vite-plugin-pwa generateSW Config](https://vite-pwa-org.netlify.app/workbox/generate-sw)
- [Chrome Installable Manifest](https://developer.chrome.com/docs/lighthouse/pwa/installable-manifest)
- [web.dev Install Prompt](https://web.dev/learn/pwa/installation-prompt)
- [MDN: Making PWAs Installable](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Guides/Making_PWAs_installable)
- [vite-plugin-pwa GitHub](https://github.com/vite-pwa/vite-plugin-pwa)
