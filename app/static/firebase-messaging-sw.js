/* /firebase-messaging-sw.js */

// Ak používaš Firebase Messaging v SW cez compat:
importScripts("https://www.gstatic.com/firebasejs/10.12.5/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/10.12.5/firebase-messaging-compat.js");

// --- Badge helper (SW side) ---
async function swSetBadge(count) {
  try {
    // v SW je badge API na registration (ak prehliadač podporuje)
    if (self.registration && "setAppBadge" in self.registration && "clearAppBadge" in self.registration) {
      if ((count || 0) > 0) await self.registration.setAppBadge(Number(count));
      else await self.registration.clearAppBadge();
    }
  } catch (e) {
    // ignore
  }
}

async function broadcastBadge(count) {
  const clientsList = await self.clients.matchAll({ type: "window", includeUncontrolled: true });
  for (const c of clientsList) {
    c.postMessage({ type: "badge", count: Number(count) || 0 });
  }
}

// ------------------------------
// FCM background (Android/desktop)
// ------------------------------
self.addEventListener("message", (event) => {
  // voliteľné: init config z page (ak nechceš hardcode)
  // event.data = { type:"FIREBASE_INIT", config:{...} }
  if (event.data && event.data.type === "FIREBASE_INIT" && event.data.config) {
    try {
      if (!firebase.apps.length) firebase.initializeApp(event.data.config);
    } catch {}
  }
});

function ensureFirebaseInitialized() {
  // Ak chceš initovať na pevno, daj sem config.
  // Odporúčam poslať config z page po load-e (nižšie v layoute),
  // ale ak už máš config serverom vygenerovaný v SW route, vieš ho vložiť priamo.
  return !!(self.firebase && firebase.apps && firebase.apps.length);
}

try {
  // Pozn.: ak inituješ firebase priamo, musíš mať config.
  // Ak init posielaš z page, toto môže byť bez initu.
  if (self.firebase && !firebase.apps.length) {
    // firebase.initializeApp({ ... }); // (ak máš config v SW)
  }

  if (self.firebase && firebase.messaging) {
    const messaging = firebase.messaging();

    messaging.onBackgroundMessage(async (payload) => {
      const title = payload?.notification?.title || "Talker";
      const body = payload?.notification?.body || "";
      const data = payload?.data || {};
      const totalUnread = Number(data.totalUnread);

      // badge
      if (Number.isFinite(totalUnread)) {
        await swSetBadge(totalUnread);
        await broadcastBadge(totalUnread);
      }

      // notifikácia
      await self.registration.showNotification(title, {
        body,
        icon: "/static/icons/apple-180.png",
        data: {
          url: data.url || "/", // môžeš poslať URL do payloadu
          roomId: data.roomId || null,
        },
      });
    });
  }
} catch (e) {
  // ignore init errors
}

// ------------------------------
// WebPush (iOS PWA Safari)
// ------------------------------
self.addEventListener("push", (event) => {
  event.waitUntil((async () => {
    let payload = {};
    try {
      payload = event.data ? event.data.json() : {};
    } catch {
      try { payload = { body: event.data?.text?.() || "" }; } catch { payload = {}; }
    }

    // payload môže byť napr. { title, body, data:{ totalUnread } } alebo priamo totalUnread
    const title = payload.title || "Talker";
    const body = payload.body || "";
    const totalUnread = Number(payload.totalUnread ?? payload?.data?.totalUnread);

    if (Number.isFinite(totalUnread)) {
      await swSetBadge(totalUnread);
      await broadcastBadge(totalUnread);
    }

    await self.registration.showNotification(title, {
      body,
      icon: "/static/icons/apple-180.png",
      data: payload.data || {},
    });
  })());
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  event.waitUntil((async () => {
    const url = event.notification?.data?.url || "/";
    const allClients = await self.clients.matchAll({ type: "window", includeUncontrolled: true });

    // ak už existuje okno, fokusni ho
    for (const c of allClients) {
      if ("focus" in c) {
        await c.focus();
        // môžeš poslať message, aby si otvoril konkrétnu miestnosť
        c.postMessage({ type: "open", url });
        return;
      }
    }

    // inak otvor nové
    if (self.clients.openWindow) await self.clients.openWindow(url);
  })());
});
