from datetime import datetime
from dateutil import parser
from app import csrf

from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    flash,
    current_app,
    abort,
)
from flask_login import current_user, login_required
from functools import wraps

from app import db
from app.models import Event, Team, EventCategory
from app.calendar.forms import EventForm, UpdateEventForm
from app.main.routes import RightColumn, Next


calendar = Blueprint("calendar", __name__)


# ----------------------------
# Roles decorator (kompatibilný s has_role aj has_roles)
# ----------------------------
def roles_required(*roles):
    def deco(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)

            has = None
            if hasattr(current_user, "has_roles"):
                has = current_user.has_roles(*roles)
            elif hasattr(current_user, "has_role"):
                has = current_user.has_role(*roles)

            if not has:
                abort(403)

            return fn(*args, **kwargs)

        return wrapper

    return deco


def _is_admin_like() -> bool:
    """Admin alebo WebAdmin."""
    if not current_user.is_authenticated:
        return False
    return bool(current_user.has_roles("Admin", "WebAdmin"))


def _trainer_team_ids() -> list[int]:
    """
    Trénerove tímy podľa tvojho modelu:
    User -> member (1:1) -> teams (M2M)
    """
    if not current_user.is_authenticated:
        return []

    # ak nie je tréner, vráť prázdne
    if not current_user.has_roles("Trener"):
        return []

    m = getattr(current_user, "member", None)
    if not m:
        return []

    teams = getattr(m, "teams", None) or []
    ids = []
    for t in teams:
        try:
            ids.append(int(t.id))
        except Exception:
            pass
    return ids


def _editable_team_ids() -> list[int]:
    """
    Kto môže upravovať:
    - Admin/WebAdmin: všetky tímy (vraciame všetky team id)
    - Tréner: iba svoje tímy (member.teams)
    """
    if _is_admin_like():
        return [t.id for t in Team.query.with_entities(Team.id).all()]
    return _trainer_team_ids()


def _event_to_fc(e: Event) -> dict:
    """
    FullCalendar v3 JSON.
    Pridávam aj team/category id (už máš v modeli), aby sa dal zobraziť chip.
    """
    return {
        "id": e.id,
        "title": e.title,
        "start": e.start_event.isoformat() if e.start_event else None,
        "end": e.end_event.isoformat() if e.end_event else None,
        "address": e.address,
        "link": e.link,
        "team": e.event_team_id,
        "category": e.event_category_id,
    }


# ----------------------------
# EXISTUJÚCE: stránka kalendára (ponechané)
# ----------------------------
@calendar.route("/calendar", methods=["GET"])
@login_required
def index():
    try:
        events = Event.query.all()
        teams = Team.query.all()
        cats = EventCategory.query.all()

        form = EventForm()
        form.team.choices = [(t.id, t.name) for t in teams]
        form.category.choices = [(c.id, c.name) for c in cats]

        form2 = UpdateEventForm()
        form2.team2.choices = [(t.id, t.name) for t in teams]
        form2.category2.choices = [(c.id, c.name) for c in cats]

        next22 = Next.next()
        teamz = RightColumn.main_menu()
        next_match = RightColumn.next_match()
        score_table = RightColumn.score_table()

        return render_template(
            "calendar/calendar.html",
            form=form,
            form2=form2,
            calendar=events,
            current_date=datetime.now(),
            next22=next22,
            teamz=teamz,
            next_match=next_match,
            score_table=score_table,
        )

    except Exception:
        current_app.logger.exception("calendar.index ERROR")
        return "Chyba pri načítaní kalendára", 500


# ----------------------------
# NOVÉ: HTMX fragment pre modal (žiadny iframe)
# ----------------------------
@calendar.route("/calendar/modal", methods=["GET"])
@login_required
def modal():
    """
    Vracia fragment HTML do modalu (layout.html -> hx-get="/calendar/modal")
    """
    try:
        teams = Team.query.all()
        cats = EventCategory.query.all()

        form = EventForm()
        form.team.choices = [(t.id, t.name) for t in teams]
        form.category.choices = [(c.id, c.name) for c in cats]

        form2 = UpdateEventForm()
        form2.team2.choices = [(t.id, t.name) for t in teams]
        form2.category2.choices = [(c.id, c.name) for c in cats]

        # práva pre frontend:
        editable_team_ids = _editable_team_ids()

        return render_template(
            "calendar/calendar_modal_fragment.html",
            form=form,
            form2=form2,
            teams=teams,
            cats=cats,
            editable_team_ids=editable_team_ids,
            current_date=datetime.now(),
        )
    except Exception:
        current_app.logger.exception("calendar.modal ERROR")
        return "Chyba pri načítaní kalendára", 500


# ----------------------------
# NOVÉ: FullCalendar zdroj udalostí
# ----------------------------
@calendar.route("/calendar/events", methods=["GET"])
@login_required
def events_list():
    """
    FullCalendar posiela ?start=...&end=... (ISO).
    Filtrujeme interval kvôli výkonu.
    """
    try:
        start_q = request.args.get("start")
        end_q = request.args.get("end")

        q = Event.query

        if start_q and end_q:
            try:
                start_dt = parser.isoparse(start_q)
                end_dt = parser.isoparse(end_q)
                # event prekrýva interval
                q = q.filter(Event.start_event < end_dt, Event.end_event > start_dt)
            except Exception:
                pass

        items = q.all()
        return jsonify([_event_to_fc(e) for e in items])
    except Exception:
        current_app.logger.exception("calendar.events_list ERROR")
        return jsonify({"error": "Chyba pri načítaní udalostí"}), 500


# ----------------------------
# VOLITEĽNÉ NOVÉ: modern create endpoint (stále môžeš používať /calendar/insert)
# - práva: Admin/WebAdmin alebo Trener pre vlastný tím
# ----------------------------
@calendar.route("/calendar/events", methods=["POST"])
@csrf.exempt
@login_required
def events_create():
    data = request.get_json(silent=True) or {}
    if not data:
        return jsonify({"error": "Chýbajú dáta"}), 400

    # práva
    is_admin = _is_admin_like()
    editable = set(_editable_team_ids())

    try:
        team_id = int(data.get("team") or 0)
    except Exception:
        team_id = 0

    if not is_admin and team_id not in editable:
        return jsonify({"error": "forbidden"}), 403

    try:
        ev = Event(
            title=(data.get("title") or "").strip(),
            start_event=parser.isoparse(data["start"]),
            end_event=parser.isoparse(data["end"]),
            address=(data.get("address") or ""),
            link=(data.get("link") or ""),
            user_id=current_user.id,
            event_category_id=int(data.get("category")),
            event_team_id=team_id,
        )
        db.session.add(ev)
        db.session.commit()
        return jsonify({"id": ev.id, "event": _event_to_fc(ev)})

    except Exception:
        db.session.rollback()
        current_app.logger.exception("calendar.events_create ERROR")
        return jsonify({"error": "Chyba pri pridávaní udalosti"}), 500
    finally:
        db.session.remove()


# ----------------------------
# EXISTUJÚCE: insert (ponechané)
# - doplnil som kontrolu práv na tím pre trénera
# ----------------------------
@calendar.route("/calendar/insert", methods=["POST"])
@csrf.exempt
@login_required
def insert():
    data = request.get_json() or {}
    if not data:
        return jsonify({"error": "Chýbajú dáta"}), 400

    # práva
    is_admin = _is_admin_like()
    editable = set(_editable_team_ids())

    try:
        team_id = int(data.get("team") or 0)
    except Exception:
        team_id = 0

    # Admin/WebAdmin OK, Tréner len svoje tímy
    if not is_admin and team_id not in editable:
        return jsonify({"error": "forbidden"}), 403

    try:
        event = Event(
            title=data["title"],
            start_event=parser.isoparse(data["start"]),
            end_event=parser.isoparse(data["end"]),
            user_id=current_user.id,
            address=data.get("address", ""),
            link=data.get("link", ""),
            event_category_id=int(data["category"]),
            event_team_id=team_id,
        )
        db.session.add(event)
        db.session.commit()
        return jsonify(event.id)

    except Exception:
        db.session.rollback()
        current_app.logger.exception("calendar.insert ERROR")
        flash("Chyba pri pridávaní udalosti. Skúste to znova.", "danger")
        return jsonify({"error": "Chyba pri pridávaní udalosti"}), 500
    finally:
        db.session.remove()


# ----------------------------
# EXISTUJÚCE: update (ponechané)
# - doplnil som kontrolu práv na tím pre trénera
# ----------------------------
@calendar.route("/calendar/update", methods=["POST", "GET"])
@csrf.exempt
@login_required
def update():
    data = request.get_json() or {}

    if request.method == "GET":
        return jsonify({"info": "GET not implemented"}), 200

    # práva
    is_admin = _is_admin_like()
    editable = set(_editable_team_ids())

    try:
        team_id = int(data.get("team2") or 0)
    except Exception:
        team_id = 0

    if not is_admin and team_id not in editable:
        return jsonify({"error": "forbidden"}), 403

    try:
        id_ = int(data["id2"])
        event = Event.query.get(id_)
        if not event:
            return jsonify({"error": "not_found"}), 404

        event.title = data.get("title2", event.title)
        event.start_event = parser.isoparse(data["start2"])
        event.end_event = parser.isoparse(data["end2"])
        event.address = data.get("address2", "")
        event.link = data.get("link2", "")
        event.event_category_id = int(data["category2"])
        event.event_team_id = team_id

        db.session.commit()
        return jsonify("success")

    except Exception:
        db.session.rollback()
        current_app.logger.exception("calendar.update ERROR")
        flash("Chyba pri aktualizácii udalosti. Skúste to znova.", "danger")
        return jsonify({"error": "Chyba pri aktualizácii udalosti"}), 500
    finally:
        db.session.remove()


# ----------------------------
# EXISTUJÚCE: ajax_delete (ponechané)
# - doplnil som login + práva (admin/webadmin alebo tréner pre svoj tím)
# ----------------------------
@calendar.route("/calendar/ajax_delete", methods=["POST"])
@csrf.exempt
@login_required
def ajax_delete():
    data = request.get_json() or {}
    if not data:
        return jsonify({"error": "Chýbajú dáta"}), 400

    is_admin = _is_admin_like()
    editable = set(_editable_team_ids())

    try:
        getid = int(data["id"])
        ev = db.session.get(Event, getid)
        if not ev:
            return jsonify({"error": "not_found"}), 404

        # tréner môže mazať len svoje tímové eventy
        if not is_admin and int(ev.event_team_id) not in editable:
            return jsonify({"error": "forbidden"}), 403

        db.session.delete(ev)
        db.session.commit()
        return jsonify(getid)

    except Exception:
        db.session.rollback()
        current_app.logger.exception("calendar.ajax_delete ERROR")
        flash("Chyba pri mazaní udalosti. Skúste to znova.", "danger")
        return jsonify({"error": "Chyba pri mazaní udalosti"}), 500
    finally:
        db.session.remove()
