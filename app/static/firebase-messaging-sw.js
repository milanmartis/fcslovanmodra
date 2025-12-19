/* /firebase-messaging-sw.js */

/**
 * Poznámky k iOS:
 * - iOS Safari PWA (Web Push) berie badge primárne z Notification option `badge`.
 *   `setAppBadge` často nefunguje / je nespoľahlivé.
 * - Preto badge nastavujeme:
 *    1) cez showNotification({ badge: <int> })
 *    2) a sekundárne sa pokúsime aj o registration.setAppBadge (ak existuje)

importScripts("https://www.gstatic.com/firebasejs/10.12.5/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/10.12.5/firebase-messaging-compat.js");

*/
// ------------------------------
// Helpers
// ------------------------------
function toInt(v, fallback = null) {
  const n = Number(v);
  return Number.isFinite(n) ? Math.max(0, Math.floor(n)) : fallback;
}

async function swSetBadge(count) {
  const n = toInt(count, null);
  if (n === null) return;

  try {
    if (
      self.registration &&
      "setAppBadge" in self.registration &&
      "clearAppBadge" in self.registration
    ) {
      if (n > 0) await self.registration.setAppBadge(n);
      else await self.registration.clearAppBadge();
    }
  } catch {
    // ignore
  }
}

async function broadcastBadge(count) {
  const n = toInt(count, 0);
  try {
    const clientsList = await self.clients.matchAll({ type: "window", includeUncontrolled: true });
    for (const c of clientsList) c.postMessage({ type: "badge", count: n });
  } catch {
    // ignore
  }
}

async function showTalkerNotification({ title, body, url, roomId, totalUnread }) {
  const badgeInt = toInt(totalUnread, null);

  // 1) iOS-friendly: badge cez Notification option
  // iOS chce URL/relative path na badge image, ale keď dáš number, Safari to mapuje na app badge.
  // Nie je to 100% zdokumentované jednotne, ale v praxi najstabilnejšie je dať `badge: <number>`.
  // Ak by ti to Safari ignorovalo, stále sa pokúsime o swSetBadge().
  const options = {
    body: body || "",
    icon: "/static/icons/apple-180.png",
    tag: roomId ? `talker-room-${roomId}` : "talker",
    renotify: true,
    data: {
      url: url || "/",
      roomId: roomId || null,
      totalUnread: badgeInt ?? undefined,
    },
  };

  if (badgeInt !== null) {
    // kľúčové pre iOS
    options.badge = badgeInt;
  }

  // 2) showNotification
  await self.registration.showNotification(title || "Talker", options);

  // 3) secondary badge set + broadcast
  if (badgeInt !== null) {
    await swSetBadge(badgeInt);
    await broadcastBadge(badgeInt);
  }
}

async function parsePushPayload(event) {
  // podpor:
  // - JSON payload (event.data.json())
  // - text payload, ktorý môže byť JSON string
  // - plain text body
  let payload = {};
  if (!event || !event.data) return payload;

  try {
    payload = event.data.json();
    return payload || {};
  } catch {
    // ignore
  }

  try {
    const txt = event.data.text ? await event.data.text() : "";
    if (!txt) return {};
    try {
      return JSON.parse(txt);
    } catch {
      return { body: txt };
    }
  } catch {
    return {};
  }
}

// ------------------------------
// Firebase init (optional from page)
// ------------------------------
self.addEventListener("message", (event) => {
  if (!event || !event.data) return;

  // event.data = { type:"FIREBASE_INIT", config:{...} }
  if (event.data.type === "FIREBASE_INIT" && event.data.config) {
    try {
      if (!firebase.apps.length) firebase.initializeApp(event.data.config);
    } catch {
      // ignore
    }
  }

  // možnosť z page poslať priamo badge update
  if (event.data.type === "SET_BADGE") {
    const n = toInt(event.data.count, null);
    if (n !== null) event.waitUntil((async () => {
      await swSetBadge(n);
      await broadcastBadge(n);
    })());
  }
});

// ------------------------------
// FCM background (Android/desktop)
// ------------------------------
try {
  if (self.firebase && firebase.messaging) {
    const messaging = firebase.messaging();

    messaging.onBackgroundMessage((payload) => {
      // payload: { notification:{title,body}, data:{url,roomId,totalUnread} }
      const title = payload?.notification?.title || "Talker";
      const body = payload?.notification?.body || "";
      const data = payload?.data || {};

      const url = data.url || "/";
      const roomId = data.roomId || null;

      // môže prísť totalUnread alebo total_unread, alebo badge
      const totalUnread =
        data.totalUnread ?? data.total_unread ?? data.badge ?? null;

      return showTalkerNotification({
        title,
        body,
        url,
        roomId,
        totalUnread,
      });
    });
  }
} catch {
  // ignore
}

// ------------------------------
// WebPush (iOS PWA Safari + všeobecný WebPush)
// ------------------------------
self.addEventListener("push", (event) => {
  event.waitUntil((async () => {
    const payload = await parsePushPayload(event);

    // ak pošleš payload ako:
    // { title, body, url, roomId, totalUnread }
    // alebo:
    // { notification:{title,body}, data:{url,roomId,totalUnread} }
    const title =
      payload.title ||
      payload?.notification?.title ||
      "Talker";

    const body =
      payload.body ||
      payload?.notification?.body ||
      "";

    const data = payload.data || payload?.notification?.data || {};

    const url = payload.url || data.url || "/";
    const roomId = payload.roomId || data.roomId || null;

    const totalUnread =
      payload.totalUnread ??
      payload.total_unread ??
      payload.badge ??
      data.totalUnread ??
      data.total_unread ??
      data.badge ??
      null;

    await showTalkerNotification({
      title,
      body,
      url,
      roomId,
      totalUnread,
    });
  })());
});

// ------------------------------
// Click handling
// ------------------------------
self.addEventListener("notificationclick", (event) => {
  event.notification.close();

  event.waitUntil((async () => {
    const url = (event.notification && event.notification.data && event.notification.data.url) || "/";

    // ak existuje otvorené okno, fokusni a naviguj
    const allClients = await self.clients.matchAll({ type: "window", includeUncontrolled: true });

    for (const c of allClients) {
      try {
        await c.focus();
        // navigate existuje pre WindowClient
        if ("navigate" in c) {
          try { await c.navigate(url); } catch {}
        }
        // pošli message do page (ak chceš otvoriť room)
        try { c.postMessage({ type: "open", url }); } catch {}
        return;
      } catch {
        // ignore
      }
    }

    // inak otvor nové
    if (self.clients.openWindow) {
      await self.clients.openWindow(url);
    }
  })());
});
