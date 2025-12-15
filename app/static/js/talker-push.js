(async () => {
    function isIosSafariPwa() {
      const ua = navigator.userAgent || "";
      const isIOS = /iPhone|iPad|iPod/i.test(ua);
      const isSafari = /^((?!chrome|crios|fxios|android).)*safari/i.test(ua);
      const isStandalone =
        window.matchMedia("(display-mode: standalone)").matches ||
        window.navigator.standalone === true;
      return isIOS && isSafari && isStandalone;
    }
  
    async function getPushConfig() {
      const res = await fetch("/talker/push/config", { credentials: "include" });
      if (!res.ok) throw new Error("push/config failed");
      return await res.json(); // { firebase:{...}, vapidPublicKey:"..." }
    }
  
    async function registerRootSW() {
      // ROOT scope – musí sedieť s tým, že SW je na /firebase-messaging-sw.js
      return await navigator.serviceWorker.register("/firebase-messaging-sw.js", { scope: "/" });
    }
  
    // -----------------------
    // BADGE (Page context)
    // -----------------------
    async function setBadge(count) {
      if (!("setAppBadge" in navigator) || !("clearAppBadge" in navigator)) return;
  
      try {
        if (count > 0) await navigator.setAppBadge(count);
        else await navigator.clearAppBadge();
      } catch (e) {
        // niektoré prehliadače to môžu blokovať bez user gesture / bez povolení
        console.log("Badge failed:", e);
      }
    }
  
    async function refreshUnreadBadge() {
      try {
        // ⚠️ ZMEŇ si URL ak máš iný endpoint
        const res = await fetch("/talker/unread/total", { credentials: "include" });
        if (!res.ok) return;
  
        const data = await res.json();
        const total = Number(data.totalUnread ?? data.total_unread ?? 0);
        await setBadge(total);
      } catch (e) {
        console.log("refreshUnreadBadge failed:", e);
      }
    }
  
    async function enableWebPushIOS() {
      const cfg = await getPushConfig();
      const vapidPublicKey = cfg.vapidPublicKey;
      if (!vapidPublicKey) throw new Error("Missing VAPID public key");
  
      const reg = await registerRootSW();
  
      // permission
      const perm = await Notification.requestPermission();
      if (perm !== "granted") return { ok: false, reason: "permission_not_granted" };
  
      // subscribe
      const sub = await reg.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(vapidPublicKey),
      });
  
      // save to backend
      const r = await fetch("/talker/webpush/subscribe", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(sub),
      });
      if (!r.ok) throw new Error("webpush/subscribe failed");
  
      // po aktivácii zosúladíme badge
      await refreshUnreadBadge();
  
      return { ok: true, mode: "webpush", sub: await r.json() };
    }
  
    async function enableFcmNonIOS() {
      const cfg = await getPushConfig();
  
      // musíš mať v page načítané firebase-app-compat.js + firebase-messaging-compat.js
      // a tento init nerob už v SW, ale v okne:
      if (!window.firebase) throw new Error("firebase not loaded in page");
  
      const firebaseCfg = cfg.firebase || {};
      if (!firebaseCfg.messagingSenderId) throw new Error("Missing firebase config");
  
      // init once
      if (!firebase.apps || !firebase.apps.length) {
        firebase.initializeApp(firebaseCfg);
      }
  
      const reg = await registerRootSW();
  
      const perm = await Notification.requestPermission();
      if (perm !== "granted") return { ok: false, reason: "permission_not_granted" };
  
      const messaging = firebase.messaging();
      // dôležité – použiť rovnaký SW:
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
  
      // po aktivácii zosúladíme badge
      await refreshUnreadBadge();
  
      return { ok: true, mode: "fcm", token, saved: await r.json() };
    }
  
    // helper: VAPID key
    function urlBase64ToUint8Array(base64String) {
      const padding = "=".repeat((4 - (base64String.length % 4)) % 4);
      const base64 = (base64String + padding).replace(/-/g, "+").replace(/_/g, "/");
      const rawData = atob(base64);
      const outputArray = new Uint8Array(rawData.length);
      for (let i = 0; i < rawData.length; ++i) outputArray[i] = rawData.charCodeAt(i);
      return outputArray;
    }
  
    async function enablePush() {
      if (!("serviceWorker" in navigator) || !("Notification" in window)) {
        return { ok: false, reason: "not_supported" };
      }
  
      if (Notification.permission === "denied") {
        return { ok: false, reason: "denied" };
      }
  
      if (isIosSafariPwa()) {
        return await enableWebPushIOS();
      } else {
        return await enableFcmNonIOS();
      }
    }
  
    // napojenie na button
    document.addEventListener("DOMContentLoaded", () => {
      const btn = document.getElementById("enable-notifications");
      if (!btn) return;
  
      // pri štarte stránky skús nastaviť badge z backendu (keď je app otvorená)
      refreshUnreadBadge();
  
      btn.addEventListener("click", async () => {
        btn.disabled = true;
        try {
          const res = await enablePush();
          console.log("push enable result:", res);
  
          // ešte raz pre istotu
          await refreshUnreadBadge();
        } catch (e) {
          console.error("enablePush error:", e);
        } finally {
          btn.disabled = false;
        }
      });
    });
  })();
  