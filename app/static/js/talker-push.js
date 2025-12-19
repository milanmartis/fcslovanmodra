(async () => {
  // -------------------------
  // Feature detect: iOS Safari PWA
  // -------------------------
  function isIosSafariPwa() {
    const ua = navigator.userAgent || "";
    const isIOS =
      /iPhone|iPad|iPod/i.test(ua) ||
      (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
    const isSafari = /^((?!chrome|crios|fxios|android).)*safari/i.test(ua);
    const isStandalone =
      window.matchMedia("(display-mode: standalone)").matches ||
      window.navigator.standalone === true;
    return isIOS && isSafari && isStandalone;
  }

  function canPush() {
    return "serviceWorker" in navigator && "Notification" in window;
  }

  // -------------------------
  // Badge API (page side)
  // -------------------------
  async function setBadge(count) {
    if (!("setAppBadge" in navigator) || !("clearAppBadge" in navigator)) return;
    try {
      const n = Number(count || 0);
      if (n > 0) await navigator.setAppBadge(n);
      else await navigator.clearAppBadge();
    } catch (e) {
      console.log("Badge failed:", e);
    }
  }

  async function fetchUnreadTotal() {
    try {
      const r = await fetch("/talker/unread/total", { credentials: "include" });
      if (!r.ok) return null;
      const j = await r.json();
      return Number(j.total ?? 0);
    } catch {
      return null;
    }
  }

  async function refreshBadgeFromBackend() {
    const total = await fetchUnreadTotal();
    if (total == null) return;
    await setBadge(total);
  }

  // -------------------------
  // Bootstrap modal helpers
  // -------------------------
  function getModalInstance() {
    const el = document.getElementById("pushModal");
    if (!el) return null;
    if (!window.bootstrap || !window.bootstrap.Modal) return null;
    return window.bootstrap.Modal.getOrCreateInstance(el, {
      backdrop: true,
      keyboard: true,
    });
  }

  function openModal() {
    const inst = getModalInstance();
    if (inst) inst.show();
  }

  function setStatus(text) {
    const el = document.getElementById("pushStatusText");
    if (el) el.textContent = text || "";
  }

  // -------------------------
  // Config + SW
  // -------------------------
  async function getPushConfig() {
    // nechávam tvoj endpoint
    const res = await fetch("/talker/push/config", { credentials: "include" });
    if (!res.ok) throw new Error("push/config failed");
    // očakávame { firebase:{...}, vapidPublicKey:"...", fcmVapidPublicKey:"..." }
    return await res.json();
  }

  async function registerRootSW() {
    const reg = await navigator.serviceWorker.register("/firebase-messaging-sw.js", {
      scope: "/",
    });
    await navigator.serviceWorker.ready;
    return reg;
  }

  // helper: VAPID
  function urlBase64ToUint8Array(base64String) {
    const padding = "=".repeat((4 - (base64String.length % 4)) % 4);
    const base64 = (base64String + padding).replace(/-/g, "+").replace(/_/g, "/");
    const rawData = atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    for (let i = 0; i < rawData.length; ++i) outputArray[i] = rawData.charCodeAt(i);
    return outputArray;
  }

  // -------------------------
  // Universal WebPush subscribe (VAPID / PushSubscription)
  // -------------------------
  async function ensureWebPushSubscription(reg, vapidPublicKey) {
    // ak už existuje subscription, nepýtaj znovu
    const existing = await reg.pushManager.getSubscription();
    if (existing) return existing;

    const sub = await reg.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(vapidPublicKey),
    });
    return sub;
  }

  async function enableWebPushUniversal(opts = {}) {
    const cfg = await getPushConfig();

    // Dôležité: pre WebPush používaj vapidPublicKey (nie "fcmVapidPublicKey")
    const vapidPublicKey = cfg.vapidPublicKey;
    if (!vapidPublicKey) throw new Error("Missing vapidPublicKey from /talker/push/config");

    if (opts.requireIosPwa && !isIosSafariPwa()) {
      throw new Error("iOS: funguje len v Safari PWA (Add to Home Screen).");
    }

    const reg = await registerRootSW();

    const perm = await Notification.requestPermission();
    if (perm !== "granted") return { ok: false, reason: "permission_not_granted" };

    const sub = await ensureWebPushSubscription(reg, vapidPublicKey);

    const r = await fetch("/talker/webpush/subscribe", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(sub.toJSON()), // ✅ čistý JSON
    });
    if (!r.ok) throw new Error("webpush/subscribe failed: " + (await r.text()));

    await refreshBadgeFromBackend();
    return { ok: true, mode: "webpush" };
  }

  // -------------------------
  // Non-iOS -> FCM
  // -------------------------
  async function enableFcmNonIOS() {
    const cfg = await getPushConfig();

    // ak firebase nie je dostupné, sprav fallback na webpush (aj na desktop)
    if (!window.firebase) {
      return await enableWebPushUniversal({ requireIosPwa: false });
    }

    const firebaseCfg = cfg.firebase || {};
    if (!firebaseCfg.messagingSenderId || !firebaseCfg.appId) {
      // ak nemáš firebase config, fallback webpush
      return await enableWebPushUniversal({ requireIosPwa: false });
    }

    if (!firebase.apps || !firebase.apps.length) firebase.initializeApp(firebaseCfg);

    const reg = await registerRootSW();

    const perm = await Notification.requestPermission();
    if (perm !== "granted") return { ok: false, reason: "permission_not_granted" };

    const messaging = firebase.messaging();

    // ✅ pre FCM používaj fcmVapidPublicKey (ak máš), inak vapidPublicKey
    const vapidKey = cfg.fcmVapidPublicKey || cfg.vapidPublicKey;
    if (!vapidKey) {
      // ak nemáš ani jeden, fallback webpush
      return await enableWebPushUniversal({ requireIosPwa: false });
    }

    const token = await messaging.getToken({
      vapidKey,
      serviceWorkerRegistration: reg,
    });

    if (!token) return { ok: false, reason: "no_token" };

    const r = await fetch("/talker/push/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({
        token,
        platform: "web",
        device: navigator.userAgent,
      }),
    });
    if (!r.ok) throw new Error("push/register failed: " + (await r.text()));

    await refreshBadgeFromBackend();
    return { ok: true, mode: "fcm", token };
  }

  async function enablePush() {
    if (!canPush()) return { ok: false, reason: "not_supported" };
    if (Notification.permission === "denied") return { ok: false, reason: "denied" };

    // iOS PWA -> WebPush (PushSubscription)
    if (isIosSafariPwa()) return await enableWebPushUniversal({ requireIosPwa: true });

    // ostatné -> FCM (fallback na WebPush ak treba)
    return await enableFcmNonIOS();
  }

  // -------------------------
  // SW -> window message (badge update)
  // -------------------------
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.addEventListener("message", async (event) => {
      const msg = event.data || {};
      if (msg.type === "badge") {
        await setBadge(msg.count);
      }
    });
  }

  // -------------------------
  // UI hookup
  // -------------------------
  document.addEventListener("DOMContentLoaded", () => {
    const openBtn = document.getElementById("openPushModalBtn");
    if (openBtn) openBtn.addEventListener("click", openModal);

    const btn = document.getElementById("enablePushBtn");
    if (btn) {
      btn.addEventListener("click", async () => {
        btn.disabled = true;
        setStatus("Zapínam…");
        try {
          const res = await enablePush();
          console.log("push enable result:", res);

          if (res.ok) {
            setStatus(res.mode === "webpush" ? "Zapnuté ✅ (Web Push)" : "Zapnuté ✅ (FCM)");
          } else {
            setStatus("Nepodarilo sa: " + (res.reason || "error"));
          }
        } catch (e) {
          console.error("enablePush error:", e);
          setStatus("Chyba: " + (e && e.message ? e.message : "error"));
        } finally {
          btn.disabled = false;
        }
      });
    }

    refreshBadgeFromBackend().catch(() => {});
  });

  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "visible") {
      refreshBadgeFromBackend().catch(() => {});
    }
  });
})();
