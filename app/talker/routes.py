from __future__ import annotations
import json
from typing import Any
from flask import current_app
from flask import Blueprint, render_template, request, jsonify, abort
from flask_security import login_required, current_user
from flask_socketio import join_room, emit
from sqlalchemy.exc import IntegrityError
from firebase_admin import messaging
from app import csrf

from flask import Response
from app import db, socketio
from app.models import TalkRoom, TalkMessage, PushToken, Team
from .permissions import user_can_access_room, is_admin_user
from app.firebase_client import init_firebase


talker = Blueprint("talker", __name__, url_prefix="/talker")




@talker.get("/firebase-messaging-sw.js")
def firebase_messaging_sw():
    # PUBLIC hodnoty – musia existovať (aspoň sender_id a app_id)
    cfg = {
        "apiKey": current_app.config.get("FIREBASE_API_KEY") or "",
        "authDomain": current_app.config.get("FIREBASE_AUTH_DOMAIN") or "",
        "projectId": current_app.config.get("FIREBASE_PROJECT_ID") or "",
        "messagingSenderId": current_app.config.get("FIREBASE_MESSAGING_SENDER_ID") or "",
        "appId": current_app.config.get("FIREBASE_APP_ID") or "",
    }

    # vždy vráť validný JS (aj keď config chýba), aby to nikdy nepadlo na HTML error page
    cfg_json = json.dumps(cfg)

    js = f"""\
/* /talker/firebase-messaging-sw.js */
"use strict";

try {{
importScripts("/static/vendor/firebase/firebase-app-compat.js");
importScripts("/static/vendor/firebase/firebase-messaging-compat.js");
}} catch (e) {{
  // ak by importScripts zlyhalo (offline/CSP/proxy), nech SW aspoň nespadne
  console.error("FCM SW importScripts failed:", e);
}}

const FIREBASE_CONFIG = {cfg_json};

if (!FIREBASE_CONFIG.messagingSenderId || !FIREBASE_CONFIG.appId) {{
  console.warn("FCM SW: missing firebase config fields (messagingSenderId/appId).", FIREBASE_CONFIG);
}} else {{
  try {{
    firebase.initializeApp(FIREBASE_CONFIG);
  }} catch (e) {{
    console.error("FCM SW firebase.initializeApp failed:", e);
  }}

  let messaging = null;
  try {{
    messaging = firebase.messaging();
  }} catch (e) {{
    console.error("FCM SW firebase.messaging() failed:", e);
  }}

  if (messaging) {{
    messaging.onBackgroundMessage((payload) => {{
      try {{
        const title = (payload && payload.notification && payload.notification.title) ? payload.notification.title : "Talker";
        const body  = (payload && payload.notification && payload.notification.body)  ? payload.notification.body  : "";
        const data  = (payload && payload.data) ? payload.data : {{}};

        const roomId = data.room_id || data.roomId;
        const url = roomId ? `/talker/rooms/${{roomId}}` : (data.url || "/talker/");

        const icon  = data.icon  || "/static/main/ico.png";
        const badge = data.badge || "/static/main/ico.png";

        self.registration.showNotification(title, {{
          body,
          icon,
          badge,
          data: Object.assign({{ url, roomId }}, data),
          actions: [
            {{ action: "open",  title: "Otvoriť" }},
            {{ action: "close", title: "Zavrieť" }},
          ],
        }});
      }} catch (e) {{
        console.error("FCM SW onBackgroundMessage error:", e);
      }}
    }});
  }}
}}

self.addEventListener("notificationclick", (event) => {{
  event.notification.close();
  if (event.action === "close") return;

  const data = (event.notification && event.notification.data) ? event.notification.data : {{}};
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
    # SW sa NESMIE agresívne cachovať, inak sa budeš trápiť s “nezmenil sa”
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    # umožni scope /talker/
    resp.headers["Service-Worker-Allowed"] = "/talker/"
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
    
    
    
@talker.get("/push/test")
@login_required
@csrf.exempt
def push_test():
    send_push_to_users(
        user_ids=[current_user.id],
        title="Test",
        body="Ahoj, toto je test push",
        data={"url": "/talker/", "type": "test"},
    )
    return jsonify(ok=True)
    
    
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
    team_id = data.get("team_id", None)  # môže byť None

    if not name:
        return jsonify(error="missing_name"), 400

    room = TalkRoom(
        name=name,
        team_id=team_id,
        created_by_user_id=current_user.id,  # u teba NOT NULL
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

    msgs = (
        TalkMessage.query
        .filter_by(room_id=room.id)
        .order_by(TalkMessage.id.desc())
        .limit(50)
        .all()
    )

    return jsonify([
        {
            "id": m.id,
            "text": m.text,
            "user_id": m.user_id,
            "username": m.author.username if getattr(m, "author", None) else "",
            "created_at": m.created_at.isoformat() if getattr(m, "created_at", None) else None,
        }
        for m in reversed(msgs)
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
    has = PushToken.query.filter_by(user_id=current_user.id).first() is not None
    return jsonify(has_token=has)


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

    # 1) ULOŽ SPRÁVU
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

    # 2) REALTIME EMIT
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

    # 3) PUSH (best-effort)
    try:
        user_ids = get_recipients_for_room(room)
        send_push_to_users(
            user_ids=user_ids,
            title=room.name,
            body=f"{username}: {msg.text[:120]}",
            data={"room_id": room.id, "type": "talker_message"},
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

    # custom room: room.members
    if getattr(room, "team_id", None) is None:
        members = getattr(room, "members", None) or []
        for u in members:
            uid = getattr(u, "id", None)
            if uid and uid != me:
                ids.append(int(uid))
        return sorted(set(ids))

    # team room: Team.members (member.user_id)
    team = Team.query.get(room.team_id)
    if not team:
        return []

    members = getattr(team, "members", None) or []
    for m in members:
        uid = getattr(m, "user_id", None)
        if uid and uid != me:
            ids.append(int(uid))

    return sorted(set(ids))


def send_push_to_users(user_ids: list[int], title: str, body: str, data: dict | None = None) -> int:
    if not user_ids:
        return 0

    app = init_firebase()
    if not app:
        return 0  # push disabled / not configured

    tokens = [
        t.token
        for t in PushToken.query.filter(PushToken.user_id.in_(user_ids)).all()
        if t and t.token
    ]
    if not tokens:
        return 0

    mm = messaging.MulticastMessage(
        notification=messaging.Notification(title=title, body=body),
        data={k: str(v) for k, v in (data or {}).items()},
        tokens=tokens,
    )
    resp = messaging.send_multicast(mm)

    # cleanup invalid tokenov
    if resp.failure_count:
        bad_tokens = [tokens[i] for i, r in enumerate(resp.responses) if not r.success]
        if bad_tokens:
            try:
                PushToken.query.filter(PushToken.token.in_(bad_tokens)).delete(synchronize_session=False)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print("PushToken cleanup error:", e)

    return int(resp.success_count or 0)
