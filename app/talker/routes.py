# app/talker/routes.py
from __future__ import annotations

import json
from typing import Any

from flask import Blueprint, render_template, request, jsonify, abort, current_app, Response
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

from flask_login import current_user, login_required
from functools import wraps


def roles_required(*roles):
    def deco(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)

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
    try {{ firebase.initializeApp(FIREBASE_CONFIG); }} catch (e) {{}}
    try {{ messaging = firebase.messaging(); }} catch (e) {{
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

async function setBadgeEverywhere(count) {{
  const n = Number(count || 0);

  // 1) Nastav badge priamo v SW (funguje aj keď je appka zavretá), ak je podporované
  try {{
    if (self.registration && "setAppBadge" in self.registration) {{
      if (n > 0) await self.registration.setAppBadge(n);
      else if ("clearAppBadge" in self.registration) await self.registration.clearAppBadge();
    }}
  }} catch (e) {{
    // ignore
  }}

  // 2) Ak sú otvorené okná, pošli im to (UI si môže zosúladiť aj vlastné počítadlá)
  try {{
    const wins = await self.clients.matchAll({{ type: "window", includeUncontrolled: true }});
    for (const w of wins) {{
      try {{
        w.postMessage({{ type: "SET_BADGE", count: n }});
      }} catch (e) {{}}
    }}
  }} catch (e) {{
    // ignore
  }}
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

    // nastav badge aj keď je appka zavretá + pošli to oknám, ak sú otvorené
    if (totalUnread !== null) setBadgeEverywhere(totalUnread);

    return self.registration.showNotification(title || "Talker", opts);
  }} catch (e) {{
    console.error("showNotif error:", e);
  }}
}}

// -------------------------
// WebPush (iOS PWA) – "push" event
// -------------------------
async function parsePushPayload(event) {{
  let payload = {{}};
  try {{
    payload = event.data ? event.data.json() : {{}};
    return payload || {{}};
  }} catch (e) {{ /* ignore */ }}

  try {{
    const txt = event.data && event.data.text ? await event.data.text() : "";
    if (!txt) return {{}};
    try {{
      return JSON.parse(txt);
    }} catch (e) {{
      return {{ body: txt }};
    }}
  }} catch (e) {{
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
        fcmVapidPublicKey=current_app.config.get("FCM_VAPID_PUBLIC_KEY")
        or current_app.config.get("VAPID_PUBLIC_KEY"),
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
            msgs = q.order_by(TalkMessage.id.desc()).limit(limit).all()
            msgs = list(reversed(msgs))
    else:
        msgs = q.order_by(TalkMessage.id.desc()).limit(limit).all()
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
    has_fcm = PushToken.query.filter_by(user_id=current_user.id).first() is not None

    has_webpush = False
    if WebPushSubscription is not None:
        has_webpush = WebPushSubscription.query.filter_by(user_id=current_user.id).first() is not None

    return jsonify(
        has_token=bool(has_fcm or has_webpush),
        has_fcm=bool(has_fcm),
        has_webpush=bool(has_webpush),
    )


# -------------------------
# UNREAD (menu + badge)
# -------------------------

@talker.get("/unread/menu")
@login_required
def unread_menu():
    payload = _build_unread_payload_for_user(int(current_user.id))
    return jsonify(
        unread_counts=payload.get("unread_counts", []),
        total_unread_count=payload.get("total_unread_count", 0),
    ), 200


@talker.route("/update-unread-count/<int:room_id>", methods=["GET", "POST"])
@csrf.exempt
@login_required
def update_unread_count(room_id):
    payload = _build_unread_payload_for_user(int(current_user.id))
    return jsonify(
        user_id=int(current_user.id),
        user_email=getattr(current_user, "email", None),
        unread_counts=payload.get("unread_counts", []),
        total_unread_count=payload.get("total_unread_count", 0),
    ), 200


@talker.post("/reset-unread-count/<int:room_id>")
@csrf.exempt
@login_required
def reset_unread_count(room_id):
    room = TalkRoom.query.get_or_404(room_id)
    if not user_can_access_room(room) and not is_admin_user():
        return jsonify({"error": "forbidden"}), 403

    from app.models import TalkRoomReadState

    last_msg = (
        TalkMessage.query
        .filter_by(room_id=room_id)
        .order_by(TalkMessage.id.desc())
        .first()
    )
    if not last_msg:
        return jsonify(ok=True, updated=False), 200

    state = TalkRoomReadState.query.filter_by(user_id=current_user.id, room_id=room_id).first()
    if not state:
        state = TalkRoomReadState(user_id=current_user.id, room_id=room_id, last_read_message_id=last_msg.id)
        db.session.add(state)
    else:
        state.last_read_message_id = last_msg.id

    db.session.commit()
    return jsonify(ok=True, updated=True), 200


@talker.post("/rooms/<int:room_id>/mark-read")
@login_required
@csrf.exempt
def mark_room_read(room_id):
    from app.models import TalkRoomReadState

    last_msg = (
        TalkMessage.query
        .filter_by(room_id=room_id)
        .order_by(TalkMessage.id.desc())
        .first()
    )
    if not last_msg:
        return jsonify(ok=True)

    state = TalkRoomReadState.query.filter_by(user_id=current_user.id, room_id=room_id).first()
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


# -------------------------
# SOCKET.IO EVENTS
# -------------------------

@socketio.on("connect", namespace="/")
def on_socket_connect():
    if not current_user.is_authenticated:
        return False
    try:
        join_room(f"user:{current_user.id}", namespace="/")
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

    # realtime správa pre online userov v room (vrátane odosielateľa)
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

    # ✅ recipients (bez odosielateľa)
    recipient_user_ids = get_recipients_for_room(room)

    # ✅ realtime badge+dropdown update (osobná room user:<id>)
    try:
        for uid in recipient_user_ids:
            payload = _build_unread_payload_for_user(int(uid))
            socketio.emit("unread_update", payload, room=f"user:{int(uid)}", namespace="/")
    except Exception:
        pass

    # ✅ push pre offline userov (len recipienti)
    try:
        preview = f"{username}: {msg.text[:120]}"
        data_payload = {
            "room_id": room.id,
            "roomId": room.id,
            "type": "talker_message",
            "url": f"/talker/rooms/{room.id}?embed=1",
        }
        if recipient_user_ids:
            send_push_to_users(
                user_ids=recipient_user_ids,
                title=room.name,
                body=preview,
                data=data_payload,
            )
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
    try:
        # ✅ ADMIN vidí všetko → aj unread počítaj pre všetky rooms
        u = None
        try:
            # ak je to práve prihlásený user, môžeš použiť current_user
            if current_user.is_authenticated and int(getattr(current_user, "id", 0) or 0) == int(user_id):
                u = current_user
        except Exception:
            u = None

        if u is not None:
            # podľa toho, čo používaš: has_role / role / is_admin flag
            if getattr(u, "is_admin", False) is True:
                return True
            if getattr(u, "has_role", None) and u.has_role("admin"):
                return True
            if getattr(u, "has_roles", None) and u.has_roles("admin"):
                return True

        # (ďalej nechaj pôvodnú logiku membership)
        if getattr(room, "team_id", None) is None:
            members = getattr(room, "members", None) or []
            for m in members:
                if int(getattr(m, "id", 0) or 0) == int(user_id):
                    return True
            return False

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
    try:
        from app.models import TalkRoomReadState  # local import

        rooms = TalkRoom.query.all()
        unread_counts: list[dict] = []

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
    unread_counts = _unread_counts_for_user(int(user_id))
    total = sum(int(x.get("unread_count", 0) or 0) for x in unread_counts)
    return {
        "total_unread_count": int(total),
        "unread_counts": unread_counts,
    }


def _total_unread_for_user(user_id: int) -> int:
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


def _send_webpush_to_user(
    user_id: int,
    title: str,
    body: str,
    url: str,
    room_id: int | None,
    total_unread: int,
    data: dict | None = None
) -> int:
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
                ttl=60 * 60,
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
    Hybrid:
      1) WebPush per-user (iOS PWA) – badge total_unread musí byť per-user
      2) FCM multicast (Android/desktop) – tokeny z PushToken
    """
    sent_total = 0
    data = data or {}

    # WebPush (iOS) – PER USER
    try:
        url = (data.get("url") or "/talker/") if isinstance(data, dict) else "/talker/"
        room_id = data.get("room_id") if isinstance(data, dict) else None
        if room_id is None and isinstance(data, dict):
            room_id = data.get("roomId")

        try:
            room_id_int = int(room_id) if room_id is not None else None
        except Exception:
            room_id_int = None

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
                    continue
    except Exception:
        pass

    # FCM (multicast)
    if not user_ids:
        return sent_total

    fb_app = init_firebase()
    if not fb_app:
        return sent_total

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
        resp = messaging.send_each_for_multicast(mm, app=fb_app)

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
        # fallback per token
        results = []
        for tok in tokens:
            msg = messaging.Message(
                notification=messaging.Notification(title=title, body=body),
                data=fcm_data,
                token=tok,
            )
            try:
                messaging.send(msg, app=fb_app)
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
