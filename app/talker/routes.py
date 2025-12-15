from __future__ import annotations

import json
from typing import Any

from flask import Blueprint, render_template, request, jsonify, abort, current_app, Response
from flask_security import login_required, current_user
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

talker = Blueprint("talker", __name__, url_prefix="/talker")


# ============================================================
# SERVICE WORKER pre FCM/WebPush – ROOT scope "/"
# ============================================================

@talker.get("/firebase-messaging-sw.js")
def _deprecated_sw_path():
    """
    Staré URL (v scope /talker) – nech to nepadá 404, ak to niekde cachelo.
    Pozor: service worker súbor nesmie byť redirectovaný.
    """
    return Response(
        "/* moved to /firebase-messaging-sw.js (root). Update your registration. */",
        mimetype="application/javascript; charset=utf-8",
        headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"},
    )


def firebase_messaging_sw():
    """
    ROOT SW pre push.
    Tento view musí byť namapovaný na /firebase-messaging-sw.js na úrovni appky (nie blueprint),
    napr. v __init__.py:
      @app.get("/firebase-messaging-sw.js")
      def firebase_messaging_sw_root(): return firebase_messaging_sw()

    Dôležité: SW, na ktorý sa robí subscribe(), musí byť ten istý, ktorý má push listener.
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
/* /firebase-messaging-sw.js */
"use strict";

try {{
  importScripts("/static/vendor/firebase/firebase-app-compat.js");
  importScripts("/static/vendor/firebase/firebase-messaging-compat.js");
}} catch (e) {{
  console.error("FCM SW importScripts failed:", e);
}}

const FIREBASE_CONFIG = {cfg_json};

try {{
  if (typeof firebase !== "undefined" && FIREBASE_CONFIG && FIREBASE_CONFIG.messagingSenderId) {{
    firebase.initializeApp(FIREBASE_CONFIG);
  }}
}} catch (e) {{
  console.error("FCM SW firebase.initializeApp failed:", e);
}}

let messaging = null;
try {{
  if (typeof firebase !== "undefined") {{
    messaging = firebase.messaging();
  }}
}} catch (e) {{
  console.error("FCM SW firebase.messaging() failed:", e);
}}

if (messaging) {{
  messaging.onBackgroundMessage((payload) => {{
    try {{
      const notif = payload?.notification || {{}};
      const data  = payload?.data || {{}};

      const roomId = data.room_id || data.roomId;
      const url = roomId ? `/talker/rooms/${{roomId}}` : (data.url || "/talker/");

      self.registration.showNotification(notif.title || "Talker", {{
        body: notif.body || "",
        icon: data.icon || "/static/main/ico.png",
        badge: data.badge || "/static/main/ico.png",
        data: Object.assign({{ url, roomId }}, data),
      }});
    }} catch (e) {{
      console.error("FCM SW onBackgroundMessage error:", e);
    }}
  }});
}}

// WebPush (iOS PWA) – push event
self.addEventListener("push", (event) => {{
  try {{
    let payload = {{}};
    try {{
      payload = event.data ? event.data.json() : {{}};
    }} catch (e) {{
      payload = {{}};
    }}

    const title = payload.title || payload?.notification?.title || "Talker";
    const body  = payload.body  || payload?.notification?.body  || "";

    const data = payload.data || {{}};
    const roomId = data.room_id || data.roomId;
    const url = data.url || (roomId ? `/talker/rooms/${{roomId}}` : "/talker/");

    event.waitUntil(
      self.registration.showNotification(title, {{
        body,
        icon: data.icon || "/static/main/ico.png",
        badge: data.badge || "/static/main/ico.png",
        data: Object.assign({{ url, roomId }}, data),
      }})
    );
  }} catch (e) {{
    console.error("SW push handler error:", e);
  }}
}});

self.addEventListener("notificationclick", (event) => {{
  event.notification.close();
  const data = event.notification?.data || {{}};
  const url = data.url || "/talker/";

  event.waitUntil(
    clients.matchAll({{ type: "window", includeUncontrolled: true }}).then((wins) => {{
      for (const w of wins) {{
        if (w.url && w.url.startsWith(self.location.origin)) {{
          w.focus();
          return w.navigate(url);
        }}
      }}
      return clients.openWindow(url);
    }})
  );
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
      - ?after_id=123  -> vráti len správy s id > after_id (aby si dotiahol zmeškané)

    Dôležité:
      - keď after_id NIE JE, chceme "posledných N" správ (nie najstarších)
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
        # posledných N
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
    Predtým si tu vracal iba FCM token (PushToken).
    Na iOS PWA však ide WebPushSubscription → preto vraciame oboje.
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
    try:
        user_ids = get_recipients_for_room(room)
        if user_ids:
            send_push_to_users(
                user_ids=user_ids,
                title=room.name,
                body=f"{username}: {msg.text[:120]}",
                data={"room_id": room.id, "type": "talker_message", "url": f"/talker/rooms/{room.id}"},
            )
    except Exception as e:
        print("Talker push error:", e)


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


def _send_webpush_to_users(user_ids: list[int], title: str, body: str, data: dict | None = None) -> int:
    if WebPushSubscription is None or webpush is None:
        return 0
    if not user_ids:
        return 0

    vapid_private = (current_app.config.get("VAPID_PRIVATE_KEY") or "").strip()
    vapid_subject = (current_app.config.get("VAPID_SUBJECT") or "mailto:admin@example.com").strip()

    # vapid_subject by mal byť mailto: alebo https://
    if not vapid_private:
        return 0

    subs = WebPushSubscription.query.filter(WebPushSubscription.user_id.in_(user_ids)).all()
    if not subs:
        return 0

    payload = json.dumps({
        "title": title,
        "body": body,
        "data": {k: str(v) for k, v in (data or {}).items()},
    })

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
                data=payload,
                vapid_private_key=vapid_private,
                vapid_claims={"sub": vapid_subject},
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
      - WebPush → WebPushSubscription (iOS PWA)
      - FCM → PushToken (Android/desktop)
    """
    sent_total = 0

    # WebPush (iOS)
    try:
        sent_total += int(_send_webpush_to_users(user_ids, title, body, data))
    except Exception:
        pass

    # FCM
    if not user_ids:
        return sent_total

    app = init_firebase()
    if not app:
        return sent_total

    # dedupe + remove empties
    raw_tokens = PushToken.query.filter(PushToken.user_id.in_(user_ids)).all()
    tokens = []
    seen = set()
    for t in raw_tokens:
        tok = (t.token or "").strip() if t else ""
        if not tok:
            continue
        if tok in seen:
            continue
        seen.add(tok)
        tokens.append(tok)

    if not tokens:
        return sent_total

    mm = messaging.MulticastMessage(
        notification=messaging.Notification(title=title, body=body),
        data={k: str(v) for k, v in (data or {}).items()},
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
        # fallback per token
        results = []
        for tok in tokens:
            msg = messaging.Message(
                notification=messaging.Notification(title=title, body=body),
                data={k: str(v) for k, v in (data or {}).items()},
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
