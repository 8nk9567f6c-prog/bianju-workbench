// Service Worker for 编剧工作台 v5.0
// Bump CACHE_VERSION on each deploy to bust cache
const CACHE_VERSION = 'v5.0';
const CACHE_NAME = 'scripter-' + CACHE_VERSION;

const PRE_CACHE = [
  './',
  './index.html',
  './manifest.json'
];

// Install: pre-cache core assets
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return Promise.allSettled(PRE_CACHE.map(url =>
        cache.add(url).catch(() => {})
      ));
    }).then(() => self.skipWaiting())
  );
});

// Activate: clean old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

// Fetch: cache-first for all assets (data is inline in HTML, no JSON fetch needed)
self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;

  event.respondWith(
    caches.match(event.request).then(cached => {
      const fetchPromise = fetch(event.request).then(response => {
        if (response.ok) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
        }
        return response;
      }).catch(() => cached);
      return cached || fetchPromise;
    })
  );
});
