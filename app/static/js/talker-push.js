(async () => {
  // -------------------------
  // Feature detect: iOS Safari PWA
  // -------------------------
  function isIosSafariPwa() {
    const ua = navigator.userAgent || "";
    const isIOS = /iPhone|iPad|iPod/i.test(ua) || (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
    const isSafari = /^((?!chrome|crios|fxios|android).)*safari/i.test(ua);
    const isStandalone =
      window.matchMedia("(display-mode: standalone)").matches ||
      window.navigator.standalone === true;
    return isIOS && isSafari && isStandalone;
  }

  // -------------------------
  // Badge API
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
  // Config + SW
  // -------------------------
  async function getPushConfig() {
    const res = await fetch("/talker/push/config", { credentials: "include" });
    if (!res.ok) throw new Error("push/config failed");
    return await res.json(); // { firebase:{...}, vapidPublicKey:"..." }
  }

  async function registerRootSW() {
    return await navigator.serviceWorker.register("/firebase-messaging-sw.js", { scope: "/" });
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
  // iOS PWA -> WebPush subscribe
  // -------------------------
  async function enableWebPushIOS() {
    const cfg = await getPushConfig();
    const vapidPublicKey = cfg.vapidPublicKey;
    if (!vapidPublicKey) throw new Error("Missing VAPID public key");

    const reg = await registerRootSW();

    const perm = await Notification.requestPermission();
    if (perm !== "granted") return { ok: false, reason: "permission_not_granted" };

    const sub = await reg.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(vapidPublicKey),
    });

    const r = await fetch("/talker/webpush/subscribe", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(sub),
    });
    if (!r.ok) throw new Error("webpush/subscribe failed");

    // po úspechu si rovno nastav badge z backendu (ak máš logiku)
    await refreshBadgeFromBackend();

    return { ok: true, mode: "webpush" };
  }

  // -------------------------
  // Non-iOS -> FCM
  // -------------------------
  async function enableFcmNonIOS() {
    const cfg = await getPushConfig();

    // ✅ používaš Firebase v šablóne – ale nepoužívaj 2 rôzne verzie naraz.
    // Táto vetva predpokladá, že na stránke je firebase v globále (compat),
    // alebo si to vieš prepnúť na modulový SDK – ale nie oboje.
    if (!window.firebase) throw new Error("firebase not loaded in page");

    const firebaseCfg = cfg.firebase || {};
    if (!firebaseCfg.messagingSenderId) throw new Error("Missing firebase config");

    if (!firebase.apps || !firebase.apps.length) {
      firebase.initializeApp(firebaseCfg);
    }

    const reg = await registerRootSW();

    const perm = await Notification.requestPermission();
    if (perm !== "granted") return { ok: false, reason: "permission_not_granted" };

    const messaging = firebase.messaging();
    messaging.useServiceWorker(reg);

    const token = await messaging.getToken({ vapidKey: cfg.vapidPublicKey });
    if (!token) return { ok: false, reason: "no_token" };

    const r = await fetch("/talker/push/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ token, platform: "web", device: navigator.userAgent }),
    });
    if (!r.ok) throw new Error("push/register failed");

    await refreshBadgeFromBackend();

    return { ok: true, mode: "fcm", token };
  }

  async function enablePush() {
    if (!("serviceWorker" in navigator) || !("Notification" in window)) {
      return { ok: false, reason: "not_supported" };
    }
    if (Notification.permission === "denied") {
      return { ok: false, reason: "denied" };
    }
    if (isIosSafariPwa()) return await enableWebPushIOS();
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
    const btn = document.getElementById("enable-notifications") || document.getElementById("enablePushBtn");
    if (btn) {
      btn.addEventListener("click", async () => {
        btn.disabled = true;
        try {
          const res = await enablePush();
          console.log("push enable result:", res);
        } catch (e) {
          console.error("enablePush error:", e);
        } finally {
          btn.disabled = false;
        }
      });
    }

    // keď sa app otvorí, skús refreshnúť badge (ak máš logiku)
    refreshBadgeFromBackend().catch(() => {});
  });

  // keď sa user vráti do appky, refreshni badge
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "visible") {
      refreshBadgeFromBackend().catch(() => {});
    }
  });
})();
