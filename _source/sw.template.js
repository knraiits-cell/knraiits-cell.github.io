// ─────────────────────────────────────────────────────────────────────
// netineti charaiveti charaiveti — service worker
// ─────────────────────────────────────────────────────────────────────
// Goals:
//   1. Make the site work fully offline after first visit.
//   2. Make every repeat visit near-instant (cache-first for static assets).
//   3. Survive flaky / low-bandwidth networks (slow phones, rural ISPs).
//   4. Update silently in the background when new content is pushed.
//
// Strategy:
//   - Precache the app shell (HTML, CSS, JS, manifest, icons, portrait).
//   - HTML: network-first with 3s timeout, fall back to cache, then offline.html
//   - CSS / JS / assets: stale-while-revalidate (instant + refresh in background)
//   - Cross-origin fonts: cache-first with long TTL
//
// Versioning: bumping CACHE_VERSION evicts old caches on activation.
// ─────────────────────────────────────────────────────────────────────

const CACHE_VERSION = "{{CACHE_VERSION}}";
const PRECACHE   = `nncc-pre-${CACHE_VERSION}`;
const RUNTIME    = `nncc-rt-${CACHE_VERSION}`;
const FONTS      = `nncc-fonts-${CACHE_VERSION}`;

const APP_SHELL = [
  "./",
  "./index.html",
  "./css/style.css",
  "./js/main.js",
  "./offline.html",
  "./manifest.webmanifest",
  "./assets/knrai.jpg",
  "./assets/knrai.webp",
  "./assets/knrai-400.webp",
  "./assets/knrai-200.webp",
  "./assets/favicon-32.png",
  "./assets/favicon-180.png",
  "./assets/icon-192.png",
  "./assets/icon-512.png"
];

// ── install: precache the app shell ────────────────────────────────────
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(PRECACHE)
      .then((cache) => cache.addAll(APP_SHELL).catch((e) => {
        // partial-success: cache what we can; the rest will be lazy-cached
        console.warn("[sw] partial precache:", e);
      }))
      .then(() => self.skipWaiting())
  );
});

// ── activate: evict old caches ─────────────────────────────────────────
self.addEventListener("activate", (event) => {
  const keep = new Set([PRECACHE, RUNTIME, FONTS]);
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => !keep.has(k)).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

// ── helpers ────────────────────────────────────────────────────────────
const TIMEOUT_MS = 3000;

function timeout(promise, ms) {
  return new Promise((resolve, reject) => {
    const t = setTimeout(() => reject(new Error("timeout")), ms);
    promise.then((v) => { clearTimeout(t); resolve(v); },
                 (e) => { clearTimeout(t); reject(e); });
  });
}

async function networkFirstHTML(req) {
  const cache = await caches.open(RUNTIME);
  try {
    const fresh = await timeout(fetch(req), TIMEOUT_MS);
    if (fresh && fresh.ok) cache.put(req, fresh.clone());
    return fresh;
  } catch (e) {
    const cached = await caches.match(req) || await caches.match("./");
    if (cached) return cached;
    return caches.match("./offline.html");
  }
}

async function staleWhileRevalidate(req, cacheName) {
  const cache = await caches.open(cacheName);
  const cached = await cache.match(req);
  const network = fetch(req).then((res) => {
    if (res && res.ok) cache.put(req, res.clone());
    return res;
  }).catch(() => cached);          // network died — return cached
  return cached || network;
}

async function cacheFirst(req, cacheName) {
  const cache = await caches.open(cacheName);
  const cached = await cache.match(req);
  if (cached) return cached;
  try {
    const fresh = await fetch(req);
    if (fresh && fresh.ok) cache.put(req, fresh.clone());
    return fresh;
  } catch (e) {
    return new Response("", { status: 504, statusText: "Offline" });
  }
}

// ── fetch router ───────────────────────────────────────────────────────
self.addEventListener("fetch", (event) => {
  const req = event.request;
  if (req.method !== "GET") return;

  const url = new URL(req.url);

  // 1. Google Fonts CSS / WOFF2 → cache-first (rare update, big perf win)
  if (url.hostname === "fonts.googleapis.com" || url.hostname === "fonts.gstatic.com") {
    event.respondWith(cacheFirst(req, FONTS));
    return;
  }

  // 2. Same-origin navigation requests (HTML pages) → network-first w/ timeout
  if (req.mode === "navigate" || (req.destination === "document")) {
    event.respondWith(networkFirstHTML(req));
    return;
  }

  // 3. Same-origin static (CSS, JS, images, manifest, fonts) → SWR
  if (url.origin === self.location.origin) {
    event.respondWith(staleWhileRevalidate(req, RUNTIME));
    return;
  }

  // 4. Everything else: try network, fall back to cache silently
  event.respondWith(
    fetch(req).catch(() => caches.match(req))
  );
});

// ── message: skip waiting on demand ────────────────────────────────────
self.addEventListener("message", (event) => {
  if (event.data === "SKIP_WAITING") self.skipWaiting();
});
