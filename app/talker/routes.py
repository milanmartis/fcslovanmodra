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

  // HTML navigácie
  if (req.mode === "navigate" || req.destination === "document") {{
    event.respondWith(
      fetch(req).catch(() => caches.match("/offline.html"))
    );
    return;
  }}

  // cache-first pre /static
  if (req.method === "GET" && url.pathname.startsWith("/static/")) {{
    event.respondWith(
      caches.match(req).then((cached) => {{
        if (cached) return cached;
        return fetch(req).then((res) => {{
          if (res && res.status === 200 && res.type === "basic") {{
            const copy = res.clone();
            caches.open(CACHE).then(cache => cache.put(req, copy));
          }}
          return res;
        }});
      }})
    );
  }}
}});
"""
    resp = Response(js, mimetype="application/javascript; charset=utf-8")
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    resp.headers["Service-Worker-Allowed"] = "/"  # ROOT scope
    return resp


@talker.get("/push/config")
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
        fcmVapidPublicKey=current_app.config.get("FCM_VAPID_PUBLIC_KEY") or current_app.config.get("VAPID_PUBLIC_KEY"),

    )


# ============================================================
# WEBPUSH SUBSCRIBE – multi-device (upsert podľa endpointu)
# ============================================================

@talker.post("/webpush/subscribe")
@login_required
@csrf.exempt
def webpush_subscribe():
    """
    Ukladá subscription z pushManager.subscribe().
    Multi-device: upsert podľa endpointu (nie 1 user = 1 sub).
    """
    if WebPushSubscription is None:
        return jsonify(error="webpush_not_configured", hint="Missing WebPushSubscription model"), 501

    sub = request.get_json(silent=True) or {}
    endpoint = (sub.get("endpoint") or "").strip()
    keys = sub.get("keys") or {}

    if not endpoint or not isinstance(keys, dict):
        return jsonify(error="invalid_subscription"), 400

    p256dh = (keys.get("p256dh") or "").strip()
    auth = (keys.get("auth") or "").strip()
    if not p256dh or not auth:
        return jsonify(error="invalid_subscription_keys"), 400

    existing = WebPushSubscription.query.filter_by(endpoint=endpoint).first()
    if existing:
        existing.user_id = current_user.id
        existing.p256dh = p256dh
        existing.auth = auth
        db.session.commit()
        return jsonify(ok=True, updated=True), 200

    s = WebPushSubscription(
        user_id=current_user.id,
        endpoint=endpoint,
        p256dh=p256dh,
        auth=auth,
    )
    db.session.add(s)
    db.session.commit()
    return jsonify(ok=True, created=True), 201


@talker.get("/push/test")
@login_required
@csrf.exempt
def push_test():
    sent = send_push_to_users(
        user_ids=[current_user.id],
        title="Test",
        body="Ahoj, toto je test push",
        data={"url": "/talker/", "type": "test"},
    )
    return jsonify(ok=True, sent=int(sent))


@talker.post("/push/unregister")
@login_required
def unregister_push_token():
    data = request.get_json(silent=True) or {}
    token = (data.get("token") or "").strip()

    q = PushToken.query.filter_by(user_id=current_user.id)
    if token:
        q = q.filter_by(token=token)

    deleted = q.delete(synchronize_session=False)
    db.session.commit()
    return jsonify(ok=True, deleted=int(deleted)), 200


# -------------------------
# HTTP ROUTES
# -------------------------

@talker.get("/")
@login_required
def index():
    if is_admin_user():
        rooms = TalkRoom.query.order_by(TalkRoom.id.desc()).all()
    else:
        all_rooms = TalkRoom.query.order_by(TalkRoom.id.desc()).all()
        rooms = [r for r in all_rooms if user_can_access_room(r)]
    return render_template("talker/index.html", rooms=rooms)


@talker.post("/rooms")
@login_required
def create_room():
    if not is_admin_user():
        abort(403)

    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    team_id = data.get("team_id", None)

    if not name:
        return jsonify(error="missing_name"), 400

    room = TalkRoom(
        name=name,
        team_id=team_id,
        created_by_user_id=current_user.id,
    )

    try:
        db.session.add(room)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        return jsonify(error="db_integrity_error", detail=str(e.orig)), 400
    except Exception as e:
        db.session.rollback()
        return jsonify(error="db_error", detail=str(e)), 500

    return jsonify(id=room.id, name=room.name, team_id=room.team_id), 201


@talker.route("/rooms/<int:room_id>")
@login_required
def room_detail(room_id):
    room = TalkRoom.query.get_or_404(room_id)

    embed = request.args.get("embed") == "1"
    base_template = "talker/embed_layout.html" if embed else "layout.html"

    return render_template(
        "talker/room_detail.html",
        room=room,
        base_template=base_template,
    )


@talker.get("/rooms/<int:room_id>/messages")
@login_required
def load_messages(room_id: int):
    """
    Podporuje:
      - ?limit=50
      - ?after_id=123  -> vráti len správy s id > after_id

    Dôležité:
      - keď after_id NIE JE, chceme "posledných N" správ
      - UI typicky chce poradie od najstaršej po najnovšiu
    """
    room = TalkRoom.query.get_or_404(room_id)
    if not user_can_access_room(room):
        abort(403)

    try:
        limit = int(request.args.get("limit", 50))
    except Exception:
        limit = 50
    limit = max(1, min(limit, 200))

    after_id = request.args.get("after_id", None)
    q = TalkMessage.query.filter_by(room_id=room.id)

    msgs: list[TalkMessage]

    if after_id:
        try:
            after_id_int = int(after_id)
            msgs = (
                q.filter(TalkMessage.id > after_id_int)
                 .order_by(TalkMessage.id.asc())
                 .limit(limit)
                 .all()
            )
        except Exception:
            msgs = (
                q.order_by(TalkMessage.id.desc())
                 .limit(limit)
                 .all()
            )
            msgs = list(reversed(msgs))
    else:
        msgs = (
            q.order_by(TalkMessage.id.desc())
             .limit(limit)
             .all()
        )
        msgs = list(reversed(msgs))

    return jsonify([
        {
            "id": m.id,
            "text": m.text,
            "user_id": m.user_id,
            "username": m.author.username if getattr(m, "author", None) else "",
            "created_at": m.created_at.isoformat() if getattr(m, "created_at", None) else None,
        }
        for m in msgs
    ])


@talker.post("/push/register")
@login_required
@csrf.exempt
def register_push_token():
    data = request.get_json(silent=True)
    if data is None:
        return jsonify(error="invalid_json", hint="Send application/json body"), 400

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

    # push pre offline userov
    # DEBUG BROADCAST: pošli push všetkým subscription + aj odosielateľovi
    try:
        preview = f"{username}: {msg.text[:120]}"
        data_payload = {
            "room_id": room.id,
            "roomId": room.id,
            "type": "talker_message",
            "url": f"/talker/rooms/{room.id}?embed=1",
        }

        # vždy pošli aj sebe (aby si hneď videl že to funguje)
        recipients = get_recipients_for_room(room)  # tu sa to spúšťa
        print("recipients:", sent)
        if recipients:
            send_push_to_users(
                user_ids=recipients,               # len tím/členovia room, bez odosielateľa
                title=room.name,
                body=preview,
                data=data_payload,
            )

        # a teraz broadcast všetkým, čo majú webpush subscription
        sent = debug_broadcast_webpush(
            title=room.name,
            body=preview,
            data=data_payload,
        )
        print("DEBUG broadcast webpush sent:", sent)

    except Exception as e:
        print("DEBUG push error:", e)

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


def _total_unread_for_user(user_id: int) -> int:
    """
    Spočíta celkové unread naprieč roomami (podľa TalkRoomReadState).
    """
    try:
        from app.models import TalkRoomReadState  # local import

        total = 0
        rooms = TalkRoom.query.all()

        for room in rooms:
            if not _user_can_access_room_for_user(user_id, room):
                continue

            state = TalkRoomReadState.query.filter_by(user_id=user_id, room_id=room.id).first()
            last_id = int(getattr(state, "last_read_message_id", 0) or 0)

            cnt = (
                TalkMessage.query
                .filter(
                    TalkMessage.room_id == room.id,
                    TalkMessage.id > last_id,
                    TalkMessage.user_id != user_id
                )
                .count()
            )
            total += int(cnt or 0)

        return int(total)
    except Exception:
        return 0


def _send_webpush_to_user(user_id: int, title: str, body: str, url: str, room_id: int | None, total_unread: int, data: dict | None = None) -> int:
    """
    WebPush pre jedného usera (kvôli per-user badge).
    """
    if WebPushSubscription is None or webpush is None:
        return 0

    vapid_private = (current_app.config.get("VAPID_PRIVATE_KEY") or "").strip()
    vapid_subject = (current_app.config.get("VAPID_SUBJECT") or "mailto:admin@example.com").strip()
    if not vapid_private:
        return 0

    subs = WebPushSubscription.query.filter_by(user_id=user_id).all()
    if not subs:
        return 0

    payload = {
        "title": title,
        "body": body,
        "url": url,
        "roomId": room_id,
        "totalUnread": int(total_unread or 0),
        "data": {k: str(v) for k, v in (data or {}).items()},
    }
    payload_json = json.dumps(payload, ensure_ascii=False)

    ok = 0
    bad_ids: list[int] = []

    for s in subs:
        try:
            sub_info = {
                "endpoint": s.endpoint,
                "keys": {"p256dh": s.p256dh, "auth": s.auth},
            }
            webpush(
                subscription_info=sub_info,
                data=payload_json,
                vapid_private_key=vapid_private,
                vapid_claims={"sub": vapid_subject},
                ttl=60 * 60,  # 1h
                headers={"Urgency": "high"},
            )
            ok += 1
        except WebPushException as ex:
            status_code = getattr(getattr(ex, "response", None), "status_code", None)
            if status_code in (404, 410):
                sid = getattr(s, "id", None)
                if sid is not None:
                    bad_ids.append(int(sid))
        except Exception:
            continue

    if bad_ids:
        try:
            WebPushSubscription.query.filter(WebPushSubscription.id.in_(bad_ids)).delete(synchronize_session=False)
            db.session.commit()
        except Exception:
            db.session.rollback()

    return ok


def send_push_to_users(user_ids: list[int], title: str, body: str, data: dict | None = None) -> int:
    """
    Hybrid "jedno miesto pravdy":

      1) WebPush per-user (iOS PWA) – kvôli badge (total_unread) musí byť per-user
      2) FCM multicast (Android/desktop) – tokeny z PushToken

    Poznámky:
      - WebPush sa posiela aj keď user nemá FCM token
      - FCM sa posiela aj keď user nemá WebPush subscription
      - payload data musí byť string -> FCM vyžaduje string values
    """
    sent_total = 0
    data = data or {}

    # -------------------------
    # WebPush (iOS) – PER USER
    # -------------------------
    try:
        url = (data.get("url") or "/talker/") if isinstance(data, dict) else "/talker/"
        room_id = data.get("room_id") if isinstance(data, dict) else None
        if room_id is None and isinstance(data, dict):
            room_id = data.get("roomId")

        try:
            room_id_int = int(room_id) if room_id is not None else None
        except Exception:
            room_id_int = None

        # pošli per-user webpush len ak máme infra (model + pywebpush)
        if WebPushSubscription is not None and webpush is not None:
            for uid in user_ids:
                try:
                    badge = _total_unread_for_user(int(uid))
                    sent_total += int(_send_webpush_to_user(
                        user_id=int(uid),
                        title=title,
                        body=body,
                        url=str(url),
                        room_id=room_id_int,
                        total_unread=int(badge),
                        data=data,
                    ))
                except Exception:
                    # nechceme zabiť celý send kvôli jednému userovi
                    continue
    except Exception:
        # webpush vetvu nikdy nenecháme zhodiť celý send
        pass

    # -------------------------
    # FCM (multicast) – tokeny
    # -------------------------
    if not user_ids:
        return sent_total

    # init firebase admin app
    app = init_firebase()
    if not app:
        return sent_total

    # vytiahni tokeny pre všetkých recipientov
    raw_tokens = PushToken.query.filter(PushToken.user_id.in_(user_ids)).all()
    tokens: list[str] = []
    seen = set()

    for t in raw_tokens:
        tok = (t.token or "").strip() if t else ""
        if not tok or tok in seen:
            continue
        seen.add(tok)
        tokens.append(tok)

    if not tokens:
        return sent_total

    # FCM data values musia byť string
    fcm_data: dict[str, str] = {}
    try:
        if isinstance(data, dict):
            fcm_data = {str(k): str(v) for k, v in data.items()}
    except Exception:
        fcm_data = {}

    mm = messaging.MulticastMessage(
        notification=messaging.Notification(title=title, body=body),
        data=fcm_data,
        tokens=tokens,
    )

    try:
        resp = messaging.send_each_for_multicast(mm, app=app)

        bad_tokens = []
        for i, r in enumerate(resp.responses):
            if not r.success:
                bad_tokens.append(tokens[i])

        if bad_tokens:
            try:
                PushToken.query.filter(PushToken.token.in_(bad_tokens)).delete(synchronize_session=False)
                db.session.commit()
            except Exception:
                db.session.rollback()

        sent_total += int(resp.success_count or 0)
        return sent_total

    except Exception:
        # fallback per token (robust)
        results = []
        for tok in tokens:
            msg = messaging.Message(
                notification=messaging.Notification(title=title, body=body),
                data=fcm_data,
                token=tok,
            )
            try:
                messaging.send(msg, app=app)
                results.append((tok, True, None))
            except Exception as ex:
                results.append((tok, False, ex))

        bad_tokens = [tok for tok, ok, _ in results if not ok]
        if bad_tokens:
            try:
                PushToken.query.filter(PushToken.token.in_(bad_tokens)).delete(synchronize_session=False)
                db.session.commit()
            except Exception:
                db.session.rollback()

        sent_total += sum(1 for _, ok, _ in results if ok)
        return sent_total





@talker.get("/webpush/test")
@login_required
def webpush_test():
    if WebPushSubscription is None or webpush is None:
        return jsonify(error="webpush_not_configured"), 501

    vapid_private = (current_app.config.get("VAPID_PRIVATE_KEY") or "").strip()
    vapid_subject = (current_app.config.get("VAPID_SUBJECT") or "mailto:admin@example.com").strip()
    if not vapid_private:
        return jsonify(error="missing_vapid_private"), 500

    sub = WebPushSubscription.query.filter_by(user_id=current_user.id).order_by(WebPushSubscription.id.desc()).first()
    if not sub:
        return jsonify(error="no_subscription"), 404

    payload = {
        "title": "iOS TEST",
        "body": "Ak toto vidíš, WebPush ide ✅",
        "url": "/talker/",
        "totalUnread": 1,
        "data": {"type": "test"},
    }

    try:
        webpush(
            subscription_info={
                "endpoint": sub.endpoint,
                "keys": {"p256dh": sub.p256dh, "auth": sub.auth},
            },
            data=json.dumps(payload, ensure_ascii=False),
            vapid_private_key=vapid_private,
            vapid_claims={"sub": vapid_subject},
            ttl=60,
            headers={"Urgency": "high"},
        )
        return jsonify(ok=True)
    except Exception as e:
        return jsonify(error="send_failed", detail=str(e)), 500



@talker.get("/rooms/<int:room_id>/unread")
@login_required
def unread_for_room(room_id):
    from app.models import TalkMessage, TalkRoomReadState

    state = TalkRoomReadState.query.filter_by(
        user_id=current_user.id,
        room_id=room_id
    ).first()

    last_id = state.last_read_message_id if state else 0

    unread = (
        TalkMessage.query
        .filter(
            TalkMessage.room_id == room_id,
            TalkMessage.id > last_id,
            TalkMessage.user_id != current_user.id
        )
        .count()
    )

    return jsonify(room_id=room_id, unread=unread)


@talker.get("/unread/total")
@login_required
def unread_total():
    from app.models import TalkMessage, TalkRoomReadState, TalkRoom

    total = 0

    rooms = TalkRoom.query.all()

    for room in rooms:
        if not user_can_access_room(room):
            continue

        state = TalkRoomReadState.query.filter_by(
            user_id=current_user.id,
            room_id=room.id
        ).first()

        last_id = state.last_read_message_id if state else 0

        cnt = (
            TalkMessage.query
            .filter(
                TalkMessage.room_id == room.id,
                TalkMessage.id > last_id,
                TalkMessage.user_id != current_user.id
            )
            .count()
        )

        total += cnt

    return jsonify(total=total)





@talker.post("/rooms/<int:room_id>/mark-read")
@login_required
@csrf.exempt
def mark_room_read(room_id):
    from app.models import TalkMessage, TalkRoomReadState

    last_msg = (
        TalkMessage.query
        .filter_by(room_id=room_id)
        .order_by(TalkMessage.id.desc())
        .first()
    )

    if not last_msg:
        return jsonify(ok=True)

    state = TalkRoomReadState.query.filter_by(
        user_id=current_user.id,
        room_id=room_id
    ).first()

    if not state:
        state = TalkRoomReadState(
            user_id=current_user.id,
            room_id=room_id,
            last_read_message_id=last_msg.id
        )
        db.session.add(state)
    else:
        state.last_read_message_id = last_msg.id

    db.session.commit()
    return jsonify(ok=True)
