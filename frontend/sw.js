// Dharma AI service worker — app-shell cache, network-first for the API.
const CACHE = "dharma-ai-v1";
const SHELL = [
  "/",
  "/index.html",
  "/styles.css",
  "/app.js",
  "/manifest.webmanifest",
  "/icons/icon.svg",
];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url);
  // Never cache API calls — always go to network.
  if (url.pathname.startsWith("/api/")) return;
  // Cache-first for the app shell / static assets.
  e.respondWith(
    caches.match(e.request).then((hit) => hit || fetch(e.request))
  );
});
