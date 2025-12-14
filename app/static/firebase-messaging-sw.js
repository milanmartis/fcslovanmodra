/* /firebase-messaging-sw.js */

/* Firebase compat pre service worker */
importScripts("https://www.gstatic.com/firebasejs/10.12.5/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/10.12.5/firebase-messaging-compat.js");

/**
 * !!! DOPLŇ podľa Firebase Console -> Project settings -> General -> Web app config
 * Toto sú PUBLIC údaje, môžu byť v SW.
 */
firebase.initializeApp({
  apiKey: "PASTE_FIREBASE_API_KEY",
  authDomain: "xindel-9f309.firebaseapp.com",
  projectId: "xindel-9f309",
  messagingSenderId: "PASTE_MESSAGING_SENDER_ID",
  appId: "PASTE_FIREBASE_APP_ID",
});

const messaging = firebase.messaging();

/**
 * FCM background handler (keď je app zatvorená alebo v pozadí)
 * Backend posiela: notification(title/body) + data(room_id, type)
 */
messaging.onBackgroundMessage((payload) => {
  const title = payload?.notification?.title || "Talker";
  const body = payload?.notification?.body || "";
  const data = payload?.data || {};

  const roomId = data.room_id || data.roomId;
  const url = roomId ? `/talker/rooms/${roomId}` : (data.url || "/talker/");

  const icon = data.icon || "/static/main/ico.png";
  const badge = data.badge || "/static/main/ico.png";

  self.registration.showNotification(title, {
    body,
    icon,
    badge,
    data: { url, roomId, ...data },
    actions: [
      { action: "open", title: "Otvoriť" },
      { action: "close", title: "Zavrieť" },
    ],
  });
});

/**
 * Klik na notifikáciu -> otvorí /talker/rooms/<id> (ak je)
 */
self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  if (event.action === "close") return;

  const data = event.notification?.data || {};
  const url = data.url || "/talker/";

  event.waitUntil(
    clients.matchAll({ type: "window", includeUncontrolled: true }).then((wins) => {
      // ak existuje otvorené okno, fokusni ho a naviguj
      for (const w of wins) {
        if (w.url && w.url.startsWith(self.location.origin)) {
          w.focus();
          return w.navigate(url);
        }
      }
      return clients.openWindow(url);
    })
  );
});
