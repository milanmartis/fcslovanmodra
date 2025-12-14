// service-worker.js

/* ===============================
   CACHE (tvoja pôvodná časť)
================================ */
const CACHE = "static-v4";
const PRECACHE = [
  // voliteľné: sem môžeš pridať /static/... súbory na prednačítanie
  // "/offline.html",
];

/* ===============================
   FIREBASE (FCM) - background
   Toto je nutné pre push keď používaš FCM.
   Doplň si config z Firebase console.
================================ */
const FIREBASE_CONFIG = {
  // !!! DOPLŇ !!!
  // apiKey: "...",
  // authDomain: "...",
  // projectId: "...",
  // messagingSenderId: "...",
  // appId: "...",
};

let hasFirebase = false;
try {
  // compat verzie sú najjednoduchšie pre SW
  importScripts("https://www.gstatic.com/firebasejs/10.12.5/firebase-app-compat.js");
  importScripts("https://www.gstatic.com/firebasejs/10.12.5/firebase-messaging-compat.js");

  if (FIREBASE_CONFIG && FIREBASE_CONFIG.messagingSenderId) {
    firebase.initializeApp(FIREBASE_CONFIG);
    const messaging = firebase.messaging();

    // Keď príde FCM push na pozadí
    messaging.onBackgroundMessage((payload) => {
      // payload typicky: { notification:{title,body}, data:{room_id,type,...}}
      const title =
        (payload && payload.notification && payload.notification.title) ||
        "Talker";
      const body =
        (payload && payload.notification && payload.notification.body) ||
        "";

      const data = (payload && payload.data) ? payload.data : {};

      const roomId = data.room_id;
      const url = roomId ? `/talker/rooms/${roomId}` : (data.url || "/");

      const icon = data.icon || "/static/icons/icon-192.png";
      const badge = data.badge || "/static/icons/badge-72.png";

      self.registration.showNotification(title, {
        body,
        icon,
        badge,
        data: { url, ...data },
        actions: [
          { action: "open", title: "Otvoriť" },
          { action: "close", title: "Zavrieť" },
        ],
      });
    });

    hasFirebase = true;
  }
} catch (e) {
  // ak importScripts zlyhá, ideš ďalej cez natívny push listener
  hasFirebase = false;
}

/* ===============================
   PUSH - tvoj pôvodný listener
   (nechávam, ale vylepšený parsing)
   Pozn.: keď používaš FCM, často sem ani nepríde, lebo to chytá onBackgroundMessage.
================================ */
self.addEventListener("push", (event) => {
  // Ak máme Firebase handler, necháme to preň (aby nevznikali duplicitné notifikácie)
  // Nie je to 100% garancia, ale v praxi to znižuje šancu na dvojité push.
  if (hasFirebase) return;

  let data = {};
  try {
    // niekedy payload príde ako text
    data = event.data ? event.data.json() : {};
  } catch (e) {
    try {
      data = { body: event.data ? event.data.text() : "" };
    } catch (e2) {
      data = {};
    }
  }

  const title = data.title || "Novinka";
  const body = data.body || "";
  const icon = data.icon || "/static/icons/icon-192.png";
  const badge = data.badge || "/static/icons/badge-72.png";

  // ak príde room_id, preferuj talker link
  const roomId = data.room_id || (data.data && data.data.room_id);
  const url = roomId ? `/talker/rooms/${roomId}` : (data.url || "/");

  event.waitUntil(
    self.registration.showNotification(title, {
      body,
      icon,
      badge,
      data: { url, ...data },
      actions: [
        { action: "open", title: "Otvoriť" },
        { action: "close", title: "Zavrieť" },
      ],
    })
  );
});

/* ===============================
   NOTIFICATION CLICK
================================ */
self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  if (event.action === "close") return;

  const data = event.notification && event.notification.data ? event.notification.data : {};
  const url = data.url || "/";

  event.waitUntil(
    clients.matchAll({ type: "window", includeUncontrolled: true }).then((wins) => {
      // ak už je otvorené okno na tej istej origin, fokusni ho
      for (const w of wins) {
        try {
          if (w.url && w.url.startsWith(self.location.origin)) {
            w.focus();
            // ak chceš, pošli message klientovi (napr. aby si refreshol chat)
            w.postMessage({ type: "fromPush", data });
            return;
          }
        } catch (e) {}
      }
      return clients.openWindow(url);
    })
  );
});

/* ===============================
   INSTALL / ACTIVATE (tvoja pôvodná časť)
================================ */
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE).then((cache) => cache.addAll(PRECACHE)).catch(() => {})
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) =>
        Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
      )
      .then(() => self.clients.claim())
  );
});

/* ===============================
   FETCH STRATÉGIA (tvoja pôvodná časť)
================================ */
self.addEventListener("fetch", (event) => {
  const req = event.request;
  const url = new URL(req.url);

  if (url.origin !== self.location.origin) {
    return; // pustíme to priamo do siete
  }

  // 1) Navigácie/HTML -> NETWORK FIRST (bez ukladania do cache!)
  if (req.mode === "navigate" || req.destination === "document") {
    event.respondWith(
      fetch(req).catch(() => caches.match("/offline.html"))
    );
    return;
  }

  // 2) Len rovnaký origin a len STATIC -> CACHE FIRST
  const isStatic = url.pathname.startsWith("/static/");

  if (req.method === "GET" && isStatic) {
    event.respondWith(
      caches.match(req).then((cached) => {
        if (cached) return cached;
        return fetch(req).then((res) => {
          if (res && res.status === 200 && res.type === "basic") {
            const copy = res.clone();
            caches.open(CACHE).then((cache) => cache.put(req, copy));
          }
          return res;
        });
      })
    );
    return;
  }

  // 3) Iné požiadavky nech rieši prehliadač bez zásahu
});
