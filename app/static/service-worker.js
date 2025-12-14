// service-worker.js
const CACHE = 'static-v4';
const PRECACHE = [
  // voliteľné: sem môžeš pridať /static/... súbory na prednačítanie
];

// --- PUSH (nechávam tvoju verziu) ---
self.addEventListener('push', (event) => {
  let data = {};
  try { data = event.data ? event.data.json() : {}; } catch (e) {}
  const title = data.title || 'Novinka';
  const body  = data.body  || '';
  const icon  = data.icon  || '/static/main/ico.png';
  const badge = data.badge || '/static/main/ico.png';
  const url   = data.url   || '/';

  event.waitUntil(
    self.registration.showNotification(title, {
      body, icon, badge,
      data: { url },
      actions: [
        { action: 'open',  title: 'Otvoriť' },
        { action: 'close', title: 'Zavrieť' }
      ]
    })
  );
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  if (event.action === 'close') return;
  const url = (event.notification.data && event.notification.data.url) || '/';
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then(ws => {
      const w = ws.find(w => w.url.includes(self.location.origin));
      if (w) { w.focus(); w.postMessage({ type: 'fromPush' }); return; }
      return clients.openWindow(url);
    })
  );
});

// --- INSTALL/ACTIVATE ---
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE).then((cache) => cache.addAll(PRECACHE)).catch(() => {})
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  // zmaž staré cache
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

// --- FETCH STRATÉGIA ---
self.addEventListener('fetch', (event) => {
  const req = event.request;
  const url = new URL(req.url);

  if (url.origin !== self.location.origin) {
    return; // pustíme to priamo do siete
  }

  // 1) Navigácie/HTML -> NETWORK FIRST (bez ukladania do cache!)
  if (req.mode === 'navigate' || (req.destination === 'document')) {
    event.respondWith(
      fetch(req).catch(() => caches.match('/offline.html')) // ak chceš, pridaj offline fallback
    );
    return;
  }

  // 2) Len rovnaký origin a len STATIC -> CACHE FIRST
  const isSameOrigin = url.origin === self.location.origin;
  const isStatic = isSameOrigin && url.pathname.startsWith('/static/');

  if (req.method === 'GET' && isStatic) {
    event.respondWith(
      caches.match(req).then(cached => {
        if (cached) return cached;
        return fetch(req).then(res => {
          // ulož len "basic" (same-origin) odpovede s 200
          if (res && res.status === 200 && res.type === 'basic') {
            const copy = res.clone();
            caches.open(CACHE).then(cache => cache.put(req, copy));
          }
          return res;
        });
      })
    );
    return;
  }

  // 3) Iné požiadavky nech rieši prehliadač bez zásahu (zníži sa šanca na ORB blokovanie)
});