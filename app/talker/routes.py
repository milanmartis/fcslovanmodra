from __future__ import annotations

from typing import Any
from flask import current_app
from flask import Blueprint, render_template, request, jsonify, abort
from flask_security import login_required, current_user
from flask_socketio import join_room, emit
from sqlalchemy.exc import IntegrityError
from firebase_admin import messaging

from app import db, socketio
from app.models import TalkRoom, TalkMessage, PushToken, Team
from .permissions import user_can_access_room, is_admin_user
from app.firebase_client import init_firebase


talker = Blueprint("talker", __name__, url_prefix="/talker")


from flask import Response

@talker.get("/firebase-messaging-sw.js")
def firebase_messaging_sw():
    # PUBLIC hodnoty – môžu ísť do klienta
    api_key = current_app.config.get("FIREBASE_API_KEY") or ""
    auth_domain = current_app.config.get("FIREBASE_AUTH_DOMAIN") or ""
    project_id = current_app.config.get("FIREBASE_PROJECT_ID") or ""
    sender_id = current_app.config.get("FIREBASE_MESSAGING_SENDER_ID") or ""
    app_id = current_app.config.get("FIREBASE_APP_ID") or ""

    js = f"""
/* /talker/firebase-messaging-sw.js */
importScripts("https://www.gstatic.com/firebasejs/10.12.5/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/10.12.5/firebase-messaging-compat.js");

firebase.initializeApp({{
  apiKey: {api_key!r},
  authDomain: {auth_domain!r},
  projectId: {project_id!r},
  messagingSenderId: {sender_id!r},
  appId: {app_id!r},
}});

const messaging = firebase.messaging();

messaging.onBackgroundMessage((payload) => {{
  const title = payload?.notification?.title || "Talker";
  const body  = payload?.notification?.body  || "";
  const data  = payload?.data || {{}};

  const roomId = data.room_id || data.roomId;
  const url = roomId ? `/talker/rooms/${{roomId}}` : (data.url || "/talker/");

  const icon  = data.icon  || "/static/main/ico.png";
  const badge = data.badge || "/static/main/ico.png";

  self.registration.showNotification(title, {{
    body, icon, badge,
    data: {{ url, roomId, ...data }},
    actions: [
      {{ action: "open",  title: "Otvoriť" }},
      {{ action: "close", title: "Zavrieť" }},
    ],
  }});
}});

self.addEventListener("notificationclick", (event) => {{
  event.notification.close();
  if (event.action === "close") return;

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
    return Response(js, mimetype="application/javascript")





@talker.get("/push/config")
@login_required
def push_config():
    # ⚠️ toto sú PUBLIC hodnoty – môžu ísť do klienta
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


@talker.get("/rooms/<int:room_id>")
@login_required
def room_detail(room_id: int):
    room = TalkRoom.query.get_or_404(room_id)
    if not user_can_access_room(room):
        abort(403)
    return render_template("talker/room.html", room=room)


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
