# from flask_socketio import join_room, emit
# from flask_security import current_user
# from firebase_admin import messaging

# from app import db, socketio
# from app.models import TalkRoom, TalkMessage, PushToken, Team, User
# from .permissions import user_can_access_room
# from app.firebase_client import init_firebase


# @socketio.on("talker_join")
# def on_join(data):
#     room_id = int(data.get("room_id"))
#     room = TalkRoom.query.get(room_id)

#     if not room or not user_can_access_room(room):
#         emit("talker_error", {"error": "forbidden"})
#         return

#     join_room(str(room.id))
#     emit("talker_joined", {"room_id": room.id})



# @socketio.on("talker_send")
# def on_send(data):
#     init_firebase()  # bezpečné, ak je funkcia idempotentná

#     try:
#         room_id = int(data.get("room_id"))
#     except Exception:
#         emit("talker_error", {"error": "bad_room_id"})
#         return

#     text = (data.get("text") or "").strip()
#     if not text:
#         return

#     room = TalkRoom.query.get(room_id)
#     if not room or not user_can_access_room(room):
#         emit("talker_error", {"error": "forbidden"})
#         return

#     # 1) ULOŽ SPRÁVU DO DB
#     msg = TalkMessage(
#         room_id=room.id,
#         user_id=current_user.id,
#         text=text,
#         created_at=datetime.utcnow(),  # ak máš server_default, môžeš vyhodiť
#     )

#     try:
#         db.session.add(msg)
#         db.session.commit()
#     except IntegrityError as e:
#         db.session.rollback()
#         emit("talker_error", {"error": "db_integrity_error", "detail": str(e.orig)})
#         return
#     except Exception as e:
#         db.session.rollback()
#         emit("talker_error", {"error": "db_error", "detail": str(e)})
#         return

#     # 2) EMITNI SPRÁVU DO ROOMKY (aby ju videli všetci otvorení v tom roome)
#     payload = {
#         "id": msg.id,
#         "room_id": room.id,
#         "user_id": current_user.id,
#         "username": getattr(current_user, "username", "user"),
#         "text": msg.text,
#         "created_at": getattr(msg, "created_at", None).isoformat() if getattr(msg, "created_at", None) else None,
#     }
#     emit("talker_message", payload, room=str(room.id), include_self=True)

#     # 3) PUSH NOTIFIKÁCIA (FCM) – len tým čo majú token a nie sú odosielateľ
#     # Používam User.push_token, lebo ho už ukladáš cez /save-token 
#     try:
#         tokens = (
#             db.session.query(User.push_token)
#             .filter(User.push_token.isnot(None))
#             .filter(User.id != current_user.id)
#             .all()
#         )
#         tokens = [t[0] for t in tokens if t and t[0]]

#         if tokens:
#             notification = messaging.Notification(
#                 title=f"{getattr(current_user, 'username', 'user')} • {room.name}",
#                 body=text[:120],
#             )

#             multicast = messaging.MulticastMessage(
#                 tokens=tokens,
#                 notification=notification,
#                 data={
#                     "room_id": str(room.id),
#                     "type": "talker_message",
#                 },
#             )
#             messaging.send_multicast(multicast)
#     except Exception as e:
#         # push nech neprerazí request – len zaloguj
#         print("FCM push error:", e)

# def get_recipients_for_room(room: TalkRoom) -> list[int]:
#     # custom room
#     if room.team_id is None:
#         return [u.id for u in room.members if u.id != current_user.id]

#     # team room: Team.members (je to backref z Member.teams)
#     team = Team.query.get(room.team_id)
#     if not team:
#         return []
#     return [m.user_id for m in team.members if m.user_id != current_user.id]


# def send_push_to_users(user_ids: list[int], title: str, body: str, data: dict | None = None) -> int:
#     if not user_ids:
#         return 0

#     app = init_firebase()
#     if not app:
#         return 0  # push disabled

#     tokens = [t.token for t in PushToken.query.filter(PushToken.user_id.in_(user_ids)).all()]
#     if not tokens:
#         return 0

#     mm = messaging.MulticastMessage(
#         notification=messaging.Notification(title=title, body=body),
#         data={k: str(v) for k, v in (data or {}).items()},
#         tokens=tokens,
#     )
#     resp = messaging.send_multicast(mm)

#     # cleanup invalid tokenov
#     if resp.failure_count:
#         bad_tokens = [tokens[i] for i, r in enumerate(resp.responses) if not r.success]
#         if bad_tokens:
#             PushToken.query.filter(PushToken.token.in_(bad_tokens)).delete(synchronize_session=False)
#             db.session.commit()

#     return resp.success_count
