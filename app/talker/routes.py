from __future__ import annotations

import json
from typing import Any

from flask import Blueprint, render_template, request, jsonify, abort, current_app, Response
# from flask_security import login_required, current_user
from flask_socketio import join_room, emit
from sqlalchemy.exc import IntegrityError
from firebase_admin import messaging

from app import db, socketio, csrf
from app.models import TalkRoom, TalkMessage, PushToken, Team
from .permissions import user_can_access_room, is_admin_user
from app.firebase_client import init_firebase

# WebPush
try:
    from pywebpush import webpush, WebPushException  # type: ignore
except Exception:  # pragma: no cover
    webpush = None
    WebPushException = Exception

# subscription model (optional)
try:
    from app.models import WebPushSubscription  # type: ignore
except Exception:  # pragma: no cover
    WebPushSubscription = None  # type: ignore

from flask_login import login_user, current_user, logout_user, login_required
from functools import wraps
from flask import abort


def roles_required(*roles):
    def deco(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)

            # ✅ robust: podporí has_role aj has_roles (aby to nepadalo podľa implementácie User)
            checker = getattr(current_user, "has_role", None) or getattr(current_user, "has_roles", None)
            if not checker or not checker(*roles):
                abort(403)

            return fn(*args, **kwargs)
        return wrapper
    return deco


talker = Blueprint("talker", __name__, url_prefix="/talker")


# ============================================================
# SERVICE WORKER – DEPRECATED TALKER PATH + ROOT SW GENERATOR
# ============================================================

@talker.get("/firebase-messaging-sw.js")
def _deprecated_sw_path():
    """
    ⚠️ DEPRECATED:
    Staré URL pod /talker. Nesmie sa používať na register().
    Vraciame 410 Gone, aby sa staré cache/registrácie postupne "odlepili".
    """
    return Response(
        "/* DEPRECATED – use /firebase-messaging-sw.js (root). */",
        status=410,
        mimetype="application/javascript; charset=utf-8",
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )


def firebase_messaging_sw():
    """
    ROOT SW pre celý web (scope "/") – PUSH + OFFLINE v jednom súbore.

    Tento view musí byť namapovaný na /firebase-messaging-sw.js na úrovni appky (nie blueprint),
    napr. v __init__.py:
      @app.get("/firebase-messaging-sw.js")
      def firebase_messaging_sw_root(): return firebase_messaging_sw()

    Dôležité:
      - register() rob len na /firebase-messaging-sw.js so scope "/"
      - iné SW (napr. /service-worker.js) NEregistruj, lebo sa bude biť scope
    """
    cfg = {
        "apiKey": current_app.config.get("FIREBASE_API_KEY") or "",
        "authDomain": current_app.config.get("FIREBASE_AUTH_DOMAIN") or "",
        "projectId": current_app.config.get("FIREBASE_PROJECT_ID") or "",
        "messagingSenderId": current_app.config.get("FIREBASE_MESSAGING_SENDER_ID") or "",
        "appId": current_app.config.get("FIREBASE_APP_ID") or "",
    }
    cfg_json = json.dumps(cfg)

    js = f"""\
/* /firebase-messaging-sw.js (ROOT) */
"use strict";

// -------------------------
// Firebase (FCM) SW
// -------------------------
try {{
importScripts("https://www.gstatic.com/firebasejs/8.10.0/firebase-app.js");
importScripts("https://www.gstatic.com/firebasejs/8.10.0/firebase-messaging.js");
}} catch (e) {{
  console.error("FCM SW importScripts failed:", e);
}}

const FIREBASE_CONFIG = {cfg_json};

let messaging = null;

try {{
  if (typeof firebase !== "undefined" && FIREBASE_CONFIG && FIREBASE_CONFIG.messagingSenderId) {{
    try {{
      firebase.initializeApp(FIREBASE_CONFIG);
    }} catch (e) {{
      // ignore already-initialized
    }}
    try {{
      messaging = firebase.messaging();
    }} catch (e) {{
      console.error("FCM SW firebase.messaging() failed:", e);
    }}
  }}
}} catch (e) {{
  console.error("FCM SW init failed:", e);
}}


function toInt(v) {{
  try {{
    if (v === null || v === undefined) return null;
    const n = parseInt(String(v), 10);
    return Number.isFinite(n) ? n : null;
  }} catch (e) {{
    return null;
  }}
}}

function broadcastBadge(count) {{
  try {{
    self.clients.matchAll({{ type: "window", includeUncontrolled: true }}).then((wins) => {{
      for (const w of wins) {{
        try {{ w.postMessage({{ type: "badge", count }}); }} catch (e) {{}}
      }}
    }});
  }} catch (e) {{}}
}}

function showNotif(title, body, data) {{
  try {{
    const totalUnread = toInt(data && (data.totalUnread ?? data.total_unread ?? data.badge));
    const roomId = data && (data.room_id || data.roomId);
    const url = (data && data.url) || (roomId ? `/talker/rooms/${{roomId}}?embed=1` : "/talker/");

    const opts = {{
      body: body || "",
      icon: (data && data.icon) || "/static/main/ico.png",

      // badge v NotificationOptions je IKONKA (nie číslo)
      badge: "/static/main/ico.png",

      tag: roomId ? `talker-room-${{roomId}}` : "talker",
      renotify: true,
      data: Object.assign({{ url, roomId, totalUnread }}, data || {{}}),
    }};

    // pošli count do klienta -> ten si zavolá navigator.setAppBadge()
    if (totalUnread !== null) broadcastBadge(totalUnread);

    return self.registration.showNotification(title || "Talker", opts);
  }} catch (e) {{
    console.error("showNotif error:", e);
  }}
}}

if (messaging) {{
  messaging.onBackgroundMessage((payload) => {{
    try {{
      const notif = payload?.notification || {{}};
      const data  = payload?.data || {{}};
      return showNotif(notif.title || "Talker", notif.body || "", data);
    }} catch (e) {{
      console.error("FCM SW onBackgroundMessage error:", e);
    }}
  }});
}}

// -------------------------
// WebPush (iOS PWA) – "push" event
// -------------------------
async function parsePushPayload(event) {{
  let payload = {{}};
  try {{
    payload = event.data ? event.data.json() : {{}};
    return payload || {{}};
  }} catch {{
    // ignore
  }}
  try {{
    const txt = event.data && event.data.text ? await event.data.text() : "";
    if (!txt) return {{}};
    try {{
      return JSON.parse(txt);
    }} catch {{
      return {{ body: txt }};
    }}
  }} catch {{
    return {{}};
  }}
}}

self.addEventListener("push", (event) => {{
  event.waitUntil((async () => {{
    const payload = await parsePushPayload(event);

    const title = payload.title || payload?.notification?.title || "Talker";
    const body  = payload.body  || payload?.notification?.body  || "";

    const data = payload.data || {{}};

    // umožni poslať url/roomId aj top-level
    if (payload.url && !data.url) data.url = payload.url;
    if (payload.roomId && !data.roomId) data.roomId = payload.roomId;
    if (payload.room_id && !data.room_id) data.room_id = payload.room_id;

    // badge / total unread
    if ((payload.totalUnread !== undefined) && (data.totalUnread === undefined)) data.totalUnread = payload.totalUnread;
    if ((payload.total_unread !== undefined) && (data.total_unread === undefined)) data.total_unread = payload.total_unread;

    await showNotif(title, body, data);
  }})());
}});

// -------------------------
// Notification click
// -------------------------
self.addEventListener("notificationclick", (event) => {{
  event.notification.close();
  const data = event.notification?.data || {{}};
  const url = data.url || "/talker/";

  event.waitUntil(
    clients.matchAll({{ type: "window", includeUncontrolled: true }}).then(async (wins) => {{
      for (const w of wins) {{
        try {{
          await w.focus();
          if ("navigate" in w) {{
            try {{ await w.navigate(url); }} catch (e) {{}}
          }}
          try {{ w.postMessage({{ type: "open", url }}); }} catch (e) {{}}
          return;
        }} catch (e) {{}}
      }}
      return clients.openWindow(url);
    }})
  );
}});

// -------------------------
// OFFLINE CACHE (network-first HTML, cache-first /static)
// -------------------------
const CACHE = "static-v6";
const PRECACHE = [
  "/offline.html",
  "/static/main/ico.png"
];

self.addEventListener("install", (event) => {{
  event.waitUntil(
    caches.open(CACHE).then((cache) => cache.addAll(PRECACHE)).catch(() => {{}})
  );
  self.skipWaiting();
}});

self.addEventListener("activate", (event) => {{
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
}});

self.addEventListener("fetch", (event) => {{
  const req = event.request;
  const url = new URL(req.url);

  if (url.origin !== self.location.origin) return;

  // cache-first static
  if (url.pathname.startsWith("/static/")) {{
    event.respondWith(
      caches.match(req).then((hit) => {{
        if (hit) return hit;
        return fetch(req).then((resp) => {{
          const copy = resp.clone();
          caches.open(CACHE).then((cache) => cache.put(req, copy)).catch(() => {{}});
          return resp;
        }});
      }})
    );
    return;
  }}

  // network-first html
  const accept = req.headers.get("accept") || "";
  if (accept.includes("text/html")) {{
    event.respondWith(
      fetch(req)
        .then((resp) => {{
          const copy = resp.clone();
          caches.open(CACHE).then((cache) => cache.put(req, copy)).catch(() => {{}});
          return resp;
        }})
        .catch(() => caches.match(req).then((hit) => hit || caches.match("/offline.html")))
    );
    return;
  }}
}});
"""
    return Response(
        js,
        mimetype="application/javascript; charset=utf-8",
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )


# -------------------------
# VIEWS
# -------------------------

@talker.get("/")
@login_required
def talker_index():
    return render_template("talker/index.html")


@talker.get("/rooms")
@login_required
def talker_rooms():
    rooms = TalkRoom.query.all()
    out = []
    for r in rooms:
        if user_can_access_room(r):
            out.append({"id": r.id, "name": r.name, "team_id": r.team_id})
    return jsonify(out)


@talker.post("/rooms")
@login_required
def talker_create_room():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    team_id = data.get("team_id")

    if not name:
        return jsonify(error="missing_name"), 400

    room = TalkRoom(name=name)
    if team_id:
        try:
            room.team_id = int(team_id)
        except Exception:
            return jsonify(error="bad_team_id"), 400

    db.session.add(room)
    db.session.commit()
    return jsonify(id=room.id, name=room.name, team_id=room.team_id), 201


@talker.get("/rooms/<int:room_id>")
@login_required
def talker_room(room_id: int):
    room = TalkRoom.query.get(room_id)
    if not room or not user_can_access_room(room):
        abort(404)
    return render_template("talker/room_detail.html", room=room)


@talker.get("/rooms/<int:room_id>/messages")
@login_required
def talker_room_messages(room_id: int):
    room = TalkRoom.query.get(room_id)
    if not room or not user_can_access_room(room):
        abort(404)

    msgs = (
        TalkMessage.query
        .filter_by(room_id=room_id)
        .order_by(TalkMessage.id.asc())
        .limit(500)
        .all()
    )

    out = []
    for m in msgs:
        out.append({
            "id": m.id,
            "room_id": m.room_id,
            "user_id": m.user_id,
            "text": m.text,
            "created_at": m.created_at.isoformat() if getattr(m, "created_at", None) else None,
        })
    return jsonify(out)


# -------------------------
# PUSH CONFIG / TOKEN / STATUS
# -------------------------

@talker.get("/push/config")
@login_required
def push_config():
    return jsonify(
        firebase={
            "apiKey": current_app.config.get("FIREBASE_API_KEY"),
            "authDomain": current_app.config.get("FIREBASE_AUTH_DOMAIN"),
            "projectId": current_app.config.get("FIREBASE_PROJECT_ID"),
            "messagingSenderId": current_app.config.get("FIREBASE_MESSAGING_SENDER_ID"),
            "appId": current_app.config.get("FIREBASE_APP_ID"),
        },
        vapidPublicKey=current_app.config.get("VAPID_PUBLIC_KEY"),
        fcmVapidPublicKey=current_app.config.get("FCM_VAPID_PUBLIC_KEY"),
    )


@talker.post("/push/token")
@login_required
def push_token_save():
    data = request.get_json(silent=True) or {}
    token = (data.get("token") or "").strip()
    platform = (data.get("platform") or "web").strip()
    device = (data.get("device") or "").strip()

    if not token:
        return jsonify(error="missing_token", received=list(data.keys())), 400

    existing = PushToken.query.filter_by(token=token).first()
    if existing:
        existing.user_id = current_user.id
        existing.platform = platform
        existing.device = device
        db.session.commit()
        return jsonify(ok=True, updated=True), 200

    pt = PushToken(user_id=current_user.id, token=token, platform=platform, device=device)
    db.session.add(pt)
    db.session.commit()
    return jsonify(ok=True, created=True), 201


@talker.get("/push/status")
@login_required
def push_status():
    """
    Vraciame oboje:
      - FCM token (PushToken)
      - WebPush subscription (WebPushSubscription)
    """
    has_fcm = PushToken.query.filter_by(user_id=current_user.id).first() is not None

    has_webpush = False
    if WebPushSubscription is not None:
        has_webpush = WebPushSubscription.query.filter_by(user_id=current_user.id).first() is not None

    return jsonify(
        has_token=bool(has_fcm or has_webpush),
        has_fcm=bool(has_fcm),
        has_webpush=bool(has_webpush),
    )


def _total_unread_for_user(user_id: int) -> int:
    try:
        from app.models import TalkRoomReadState  # local import
        total = 0
        rooms = TalkRoom.query.all()
        for room in rooms:
            if not _user_can_access_room_for_user(int(user_id), room):
                continue

            state = TalkRoomReadState.query.filter_by(user_id=int(user_id), room_id=room.id).first()
            last_id = int(getattr(state, "last_read_message_id", 0) or 0)

            cnt = (
                TalkMessage.query
                .filter(
                    TalkMessage.room_id == room.id,
                    TalkMessage.id > last_id,
                    TalkMessage.user_id != int(user_id),
                )
                .count()
            )
            total += int(cnt or 0)
        return int(total)
    except Exception:
        return 0


def _send_webpush_to_user(
    user_id: int,
    title: str,
    body: str,
    url: str,
    room_id: int | None,
    total_unread: int,
    data: dict,
) -> bool:
    if WebPushSubscription is None or webpush is None:
        return False

    sub = WebPushSubscription.query.filter_by(user_id=int(user_id)).first()
    if not sub:
        return False

    vapid_private_key = current_app.config.get("VAPID_PRIVATE_KEY")
    if not vapid_private_key:
        return False

    payload = {
        "title": title,
        "body": body,
        "url": url,
        "room_id": room_id,
        "totalUnread": int(total_unread),
        "data": data or {},
    }

    try:
        webpush(
            subscription_info=sub.subscription_json,
            data=json.dumps(payload),
            vapid_private_key=vapid_private_key,
            vapid_claims={"sub": "mailto:admin@example.com"},
        )
        return True
    except WebPushException as e:
        try:
            if getattr(e, "response", None) is not None and e.response.status_code in (404, 410):
                db.session.delete(sub)
                db.session.commit()
        except Exception:
            pass
        return False
    except Exception:
        return False


def send_push_to_users(user_ids: list[int], title: str, body: str, data: dict):
    """
    Pošle:
      - FCM (ak user má PushToken)
      - WebPush (ak má WebPushSubscription)
    """
    try:
        init_firebase()
    except Exception:
        pass

    user_ids = sorted({int(x) for x in (user_ids or []) if int(x) > 0})
    if not user_ids:
        return 0

    sent = 0

    # --- FCM ---
    tokens = PushToken.query.filter(PushToken.user_id.in_(user_ids)).all()
    fcm_tokens = [t.token for t in tokens if getattr(t, "token", None)]
    if fcm_tokens:
        try:
            msg = messaging.MulticastMessage(
                tokens=fcm_tokens,
                notification=messaging.Notification(title=title, body=body),
                data={k: str(v) for k, v in (data or {}).items()},
            )
            resp = messaging.send_multicast(msg)
            sent += int(resp.success_count or 0)
        except Exception:
            pass

    # --- WebPush ---
    if WebPushSubscription is not None:
        for uid in user_ids:
            try:
                badge = _total_unread_for_user(uid)
                ok = _send_webpush_to_user(
                    user_id=uid,
                    title=title,
                    body=body,
                    url=str((data or {}).get("url") or "/talker/"),
                    room_id=int((data or {}).get("room_id") or (data or {}).get("roomId") or 0) or None,
                    total_unread=int(badge),
                    data=data,
                )
                sent += 1 if ok else 0
            except Exception:
                continue

    return sent


def debug_broadcast_webpush(title: str, body: str, data: dict):
    if WebPushSubscription is None or webpush is None:
        return 0

    # všetci users, ktorí majú subscription (aj mimo room)
    subs = WebPushSubscription.query.all()
    user_ids = sorted({int(s.user_id) for s in subs if getattr(s, "user_id", None)})

    sent = 0
    for uid in user_ids:
        try:
            badge = _total_unread_for_user(uid)
            sent += int(_send_webpush_to_user(
                user_id=uid,
                title=title,
                body=body,
                url=str(data.get("url") or "/talker/"),
                room_id=int(data.get("room_id") or data.get("roomId") or 0) or None,
                total_unread=int(badge),
                data=data,
            ))
        except Exception:
            continue

    return sent


# -------------------------
# SOCKET.IO EVENTS
# -------------------------

@socketio.on("connect")
def on_socket_connect():
    """
    ✅ Realtime unread: každý prihlásený user sa pripojí do osobnej miestnosti user:<id>
    (badge/dropdown update vieme poslať priamo jemu).
    """
    if not current_user.is_authenticated:
        return False
    try:
        join_room(f"user:{current_user.id}")
    except Exception:
        pass


@socketio.on("talker_join")
def on_join(data: dict[str, Any]):
    try:
        room_id = int((data or {}).get("room_id"))
    except Exception:
        emit("talker_error", {"error": "bad_room_id"})
        return

    room = TalkRoom.query.get(room_id)
    if not room or not user_can_access_room(room):
        emit("talker_error", {"error": "forbidden"})
        return

    join_room(str(room.id))
    emit("talker_joined", {"room_id": room.id})


@socketio.on("talker_send")
def on_send(data: dict[str, Any]):
    try:
        room_id = int((data or {}).get("room_id"))
    except Exception:
        emit("talker_error", {"error": "bad_room_id"})
        return

    text = ((data or {}).get("text") or "").strip()
    if not text:
        return

    room = TalkRoom.query.get(room_id)
    if not room or not user_can_access_room(room):
        emit("talker_error", {"error": "forbidden"})
        return

    username = getattr(current_user, "username", None) or getattr(current_user, "email", "user")
    msg = TalkMessage(room_id=room.id, user_id=current_user.id, text=text)

    try:
        db.session.add(msg)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        emit("talker_error", {"error": "db_integrity_error", "detail": str(e.orig)})
        return
    except Exception as e:
        db.session.rollback()
        emit("talker_error", {"error": "db_error", "detail": str(e)})
        return

    # realtime pre online userov
    emit(
        "talker_message",
        {
            "id": msg.id,
            "room_id": room.id,
            "text": msg.text,
            "user_id": current_user.id,
            "username": username,
            "created_at": msg.created_at.isoformat() if getattr(msg, "created_at", None) else None,
        },
        room=str(room.id),
        include_self=True,
    )

    # ✅ realtime unread update (badge + dropdown) pre recipientov
    # - webpush/FCM nemeníme, iba doplníme socket emit
    try:
        recipient_user_ids = get_recipients_for_room(room)
        for uid in recipient_user_ids:
            payload = _build_unread_payload_for_user(int(uid))
            socketio.emit("unread_update", payload, room=f"user:{int(uid)}")
    except Exception:
        pass

    # push pre offline userov (FCM + WebPush)
    # - posielame LEN recipientom z miestnosti (nie odosielateľovi)
    try:
        preview = f"{username}: {msg.text[:120]}"
        data_payload = {
            "room_id": room.id,
            "roomId": room.id,
            "type": "talker_message",
            "url": f"/talker/rooms/{room.id}?embed=1",
        }

        recipient_user_ids = get_recipients_for_room(room)

        # ✅ FCM + WebPush posielame recipientom (nie sebe)
        if recipient_user_ids:
            send_push_to_users(
                user_ids=recipient_user_ids,
                title=room.name,
                body=preview,
                data=data_payload,
            )

        # voliteľný DEBUG broadcast (ak chceš dočasne posielať všetkým subscription)
        if str(current_app.config.get("TALKER_DEBUG_BROADCAST_PUSH", "0")) == "1":
            sent = debug_broadcast_webpush(
                title=room.name,
                body=preview,
                data=data_payload,
            )
            print("DEBUG broadcast webpush sent:", sent)

    except Exception as e:
        print("push error:", e)


# -------------------------
# HELPERS
# -------------------------

def get_recipients_for_room(room: TalkRoom) -> list[int]:
    me = getattr(current_user, "id", None)
    if me is None:
        return []

    ids: list[int] = []

    if getattr(room, "team_id", None) is None:
        members = getattr(room, "members", None) or []
        for u in members:
            uid = getattr(u, "id", None)
            if uid and uid != me:
                ids.append(int(uid))
        return sorted(set(ids))

    team = Team.query.get(room.team_id)
    if not team:
        return []

    members = getattr(team, "members", None) or []
    for m in members:
        uid = getattr(m, "user_id", None)
        if uid and uid != me:
            ids.append(int(uid))

    return sorted(set(ids))


def _user_can_access_room_for_user(user_id: int, room: TalkRoom) -> bool:
    """
    Bez current_user – aby sme vedeli počítať unread pre recipientov.
    """
    try:
        # room without team: membership list
        if getattr(room, "team_id", None) is None:
            members = getattr(room, "members", None) or []
            for u in members:
                if int(getattr(u, "id", 0) or 0) == int(user_id):
                    return True
            return False

        # room with team: team membership list
        team = Team.query.get(room.team_id)
        if not team:
            return False
        members = getattr(team, "members", None) or []
        for m in members:
            if int(getattr(m, "user_id", 0) or 0) == int(user_id):
                return True
        return False
    except Exception:
        return False


def _unread_counts_for_user(user_id: int) -> list[dict]:
    """
    Vráti zoznam:
      [{room_id, room_name, unread_count}, .]
    určené pre dropdown v menu.
    """
    try:
        from app.models import TalkRoomReadState  # local import

        unread_counts: list[dict] = []

        rooms = TalkRoom.query.all()
        for room in rooms:
            if not _user_can_access_room_for_user(int(user_id), room):
                continue

            state = TalkRoomReadState.query.filter_by(user_id=int(user_id), room_id=room.id).first()
            last_id = int(getattr(state, "last_read_message_id", 0) or 0)

            cnt = (
                TalkMessage.query
                .filter(
                    TalkMessage.room_id == room.id,
                    TalkMessage.id > last_id,
                    TalkMessage.user_id != int(user_id)
                )
                .count()
            )
            cnt = int(cnt or 0)
            if cnt > 0:
                unread_counts.append({
                    "room_id": int(room.id),
                    "room_name": str(getattr(room, "name", "") or f"Room #{room.id}"),
                    "unread_count": cnt
                })

        unread_counts.sort(key=lambda x: int(x.get("unread_count", 0)), reverse=True)
        return unread_counts
    except Exception:
        return []


def _build_unread_payload_for_user(user_id: int) -> dict:
    """
    Payload pre Socket.IO event 'unread_update':
      {
        "total_unread_count": <int>,
        "unread_counts": [{room_id, room_name, unread_count}, .]
      }
    """
    unread_counts = _unread_counts_for_user(int(user_id))
    total = sum(int(x.get("unread_count", 0) or 0) for x in unread_counts)
    return {
        "total_unread_count": int(total),
        "unread_counts": unread_counts,
    }
