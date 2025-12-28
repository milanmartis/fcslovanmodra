/* /firebase-messaging-sw.js */

// ✅ Firebase musí byť mimo komentára
importScripts("https://www.gstatic.com/firebasejs/8.10.0/firebase-app.js");
importScripts("https://www.gstatic.com/firebasejs/8.10.0/firebase-messaging.js");
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

async function setBadgeEverywhere(count) {
  const n = Number(count || 0);

  // 1) nastav badge priamo v SW (funguje aj keď je appka zavretá), ak platforma podporuje
  try {
    if (self.navigator && "setAppBadge" in self.navigator) {
      if (n > 0) await self.navigator.setAppBadge(n);
      else if ("clearAppBadge" in self.navigator) await self.navigator.clearAppBadge();
    }
  } catch (e) {
    // ignoruj – nie všade to ide
  }

  // 2) ak je appka otvorená, pošli aj do okien (aby sa UI zosúladilo)
  try {
    const wins = await self.clients.matchAll({ type: "window", includeUncontrolled: true });
    for (const w of wins) {
      w.postMessage({ type: "SET_BADGE", count: n });
    }
  } catch (e) {}
}
async function showTalkerNotification({ title, body, url, roomId, totalUnread }) {
  const badgeInt = toInt(totalUnread, null);

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

  // iOS-friendly badge
  if (badgeInt !== null) {
    options.badge = badgeInt;
  }

  await self.registration.showNotification(title || "Talker", options);

  if (badgeInt !== null) {
    await swSetBadge(badgeInt);
    await setBadgeEverywhere(badgeInt);
  }
}

async function parsePushPayload(event) {
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

  if (event.data.type === "FIREBASE_INIT" && event.data.config) {
    try {
      if (!firebase.apps.length) firebase.initializeApp(event.data.config);
    } catch {
      // ignore
    }
  }

  if (event.data.type === "SET_BADGE") {
    const n = toInt(event.data.count, null);
    if (n !== null) {
      event.waitUntil(
        (async () => {
          await swSetBadge(n);
          await setBadgeEverywhere(n);
        })()
      );
    }
  }
});

// ------------------------------
// FCM background (Android/desktop)
// ------------------------------
try {
  if (self.firebase && firebase.messaging) {
    const messaging = firebase.messaging();

    messaging.onBackgroundMessage((payload) => {
      const title = payload?.notification?.title || "Talker";
      const body = payload?.notification?.body || "";
      const data = payload?.data || {};

      const url = data.url || "/";
      const roomId = data.roomId || null;

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
  event.waitUntil(
    (async () => {
      const payload = await parsePushPayload(event);

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
    })()
  );
});

// ------------------------------
// Click handling
// ------------------------------
self.addEventListener("notificationclick", (event) => {
  event.notification.close();

  event.waitUntil(
    (async () => {
      const url =
        (event.notification &&
          event.notification.data &&
          event.notification.data.url) ||
        "/";

      const allClients = await self.clients.matchAll({
        type: "window",
        includeUncontrolled: true,
      });

      for (const c of allClients) {
        try {
          await c.focus();
          if ("navigate" in c) {
            try {
              await c.navigate(url);
            } catch {}
          }
          try {
            c.postMessage({ type: "open", url });
          } catch {}
          return;
        } catch {
          // ignore
        }
      }

      if (self.clients.openWindow) {
        await self.clients.openWindow(url);
      }
    })()
  );
});
