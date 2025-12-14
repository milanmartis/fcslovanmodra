from functools import wraps

from flask import Blueprint, render_template, request, jsonify
from flask_security import login_required, current_user
from sqlalchemy.exc import IntegrityError

from app import db

# ✅ berieme TalkRoom (podľa tvojho erroru to je tabuľka talk_room)
from app.models import TalkRoom as RoomModel

talker_admin = Blueprint("talker_admin", __name__, url_prefix="/admin/talker")


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify(error="unauthorized"), 401

        is_admin = False
        try:
            is_admin = current_user.has_role("Admin") or current_user.has_role("WebAdmin")
        except Exception:
            is_admin = False

        if not is_admin:
            return jsonify(error="forbidden"), 403

        return fn(*args, **kwargs)

    return wrapper


@talker_admin.route("/rooms", methods=["GET"])
@login_required
@admin_required
def admin_rooms_page():
    rooms = db.session.query(RoomModel).order_by(RoomModel.id.desc()).all()
    return render_template("admin/talker_rooms.html", rooms=rooms)


@talker_admin.route("/rooms", methods=["POST"])
@login_required
@admin_required
def admin_rooms_create():
    data = request.get_json(silent=True)

    if data is None:
        return jsonify(
            error="invalid_json",
            hint='Send JSON body like {"name":"General","team_id":1} with Content-Type: application/json'
        ), 400

    name = (data.get("name") or "").strip()
    if not name:
        return jsonify(error="name is required"), 400

    # team_id je u teba v INSERT (talk_room má team_id stĺpec)
    team_id = data.get("team_id", None)

    room = RoomModel(name=name)

    # ✅ FIX pre tvoj error: created_by_user_id je NOT NULL
    if hasattr(room, "created_by_user_id"):
        room.created_by_user_id = current_user.id

    # team_id nastav len ak prišiel
    if hasattr(room, "team_id") and team_id not in (None, ""):
        room.team_id = int(team_id)

    try:
        db.session.add(room)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        # vraciame 400 s dôvodom (napr. "team_id null violates not null constraint")
        return jsonify(error="integrity_error", detail=str(e.orig)), 400

    return jsonify(id=room.id, name=room.name), 201


@talker_admin.route("/rooms/<int:room_id>", methods=["DELETE"])
@login_required
@admin_required
def admin_rooms_delete(room_id):
    room = db.session.get(RoomModel, room_id)
    if not room:
        return jsonify(error="not found"), 404

    try:
        db.session.delete(room)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        return jsonify(error="integrity_error", detail=str(e.orig)), 400

    return jsonify(ok=True), 200
