// Dharma AI service worker — network-first so updates always show; cache is offline fallback only.
const CACHE = "dharma-ai-v9";
const SHELL = [
  "/",
  "/index.html",
  "/styles.css",
  "/app.js",
  "/avatars.js",
  "/manifest.webmanifest",
  "/icons/icon.svg",
];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

// ---- Daily Guidance push ----
self.addEventListener("push", (e) => {
  let data = {};
  try { data = e.data ? e.data.json() : {}; } catch (err) {}
  e.waitUntil(
    self.registration.showNotification(data.title || "Dharma AI", {
      body: data.body || "Your verse of the day awaits. 🙏",
      icon: "/icons/icon-192.png",
      badge: "/icons/icon-192.png",
      data: { url: (data && data.url) || "/" },
    })
  );
});

self.addEventListener("notificationclick", (e) => {
  e.notification.close();
  e.waitUntil(
    clients.matchAll({ type: "window", includeUncontrolled: true }).then((list) => {
      for (const c of list) { if ("focus" in c) return c.focus(); }
      return clients.openWindow((e.notification.data && e.notification.data.url) || "/");
    })
  );
});

self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url);
  if (url.pathname.startsWith("/api/")) return; // never cache the API
  // Network-first: always serve fresh when online; fall back to cache offline.
  e.respondWith(
    fetch(e.request)
      .then((resp) => {
        const copy = resp.clone();
        caches.open(CACHE).then((c) => c.put(e.request, copy)).catch(() => {});
        return resp;
      })
      .catch(() => caches.match(e.request))
  );
});
