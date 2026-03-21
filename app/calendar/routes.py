from __future__ import annotations
from app.utils import to_utc_iso
from datetime import datetime, time, timezone
from functools import wraps

from dateutil import parser

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

from app import csrf, db
from app.models import Event, Team, EventCategory
from app.calendar.forms import EventForm, UpdateEventForm
from app.main.routes import RightColumn, Next

try:
    from zoneinfo import ZoneInfo  # py3.9+
except Exception:  # pragma: no cover
    ZoneInfo = None


calendar = Blueprint("calendar", __name__)


# ============================================================
# TIMEZONE HELPERS (robust: local aj prod)
# ============================================================

def _app_tz():
    """
    Timezone aplikácie (pre interpretáciu naive datetime z klienta).
    Nastav v configu:
        APP_TIMEZONE = "Europe/Bratislava"
    """
    tz_name = current_app.config.get("APP_TIMEZONE", "Europe/Bratislava")

    if ZoneInfo is None:
        # Fallback ak by nebola zoneinfo (malo by byť zbytočné na py3.9+)
        return timezone.utc

    try:
        return ZoneInfo(tz_name)
    except Exception:
        return ZoneInfo("Europe/Bratislava")


def _to_local_naive(dt: datetime) -> datetime:
    """
    Z datetime spraví LOCAL-naive (tzinfo=None) pre DB.
    Teda 19:00 ostane 19:00.
    """
    if dt.tzinfo:
        return dt.astimezone(_app_tz()).replace(tzinfo=None)
    return dt

def parse_client_dt(val: str | None, fallback_dt: datetime | None = None) -> datetime | None:
    """
    Parsovanie dátumu/času z klienta:

    - ISO s tzinfo (Z alebo +01:00) → konvertuj na APP_TIMEZONE a ulož ako local-naive
    - naive ISO bez tz → ber ako lokálny čas a ulož bez posunu
    - date-only (YYYY-MM-DD) → zachovaj čas z fallback_dt (ak existuje)
    """
    if not val:
        return None

    dt = parser.isoparse(val)

    if (
        isinstance(dt, datetime)
        and dt.time() == time(0, 0)
        and "T" not in val
        and fallback_dt
    ):
        dt = dt.replace(
            hour=fallback_dt.hour,
            minute=fallback_dt.minute,
            second=fallback_dt.second,
            microsecond=fallback_dt.microsecond,
        )

    if isinstance(dt, datetime):
        return _to_local_naive(dt)

    if fallback_dt:
        combined = datetime.combine(dt, fallback_dt.time())
    else:
        combined = datetime.combine(dt, time(0, 0))

    return _to_local_naive(combined)



def _event_to_fc(e: Event) -> dict:
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
    
# def iso_utc_z(dt: datetime | None) -> str | None:
#     """
#     DB má UTC-naive → pošli klientovi ISO s 'Z' (UTC).
#     """
#     if not dt:
#         return None
#     return dt.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")


# ============================================================
# AUTH / ROLES
# ============================================================

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

    if not current_user.has_roles("Trener"):
        return []

    m = getattr(current_user, "member", None)
    if not m:
        return []

    teams = getattr(m, "teams", None) or []
    ids: list[int] = []
    for t in teams:
        try:
            ids.append(int(t.id))
        except Exception:
            pass
    return ids


def _editable_team_ids() -> list[int]:
    """
    Kto môže upravovať:
    - Admin/WebAdmin: všetky tímy
    - Tréner: iba svoje tímy
    """
    if _is_admin_like():
        return [t.id for t in Team.query.with_entities(Team.id).all()]
    return _trainer_team_ids()





# ============================================================
# ROUTES
# ============================================================

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
            current_date=datetime.now(timezone.utc),
            next22=next22,
            teamz=teamz,
            next_match=next_match,
            score_table=score_table,
        )

    except Exception:
        current_app.logger.exception("calendar.index ERROR")
        return "Chyba pri načítaní kalendára", 500


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

        editable_team_ids = _editable_team_ids()

        return render_template(
            "calendar/calendar_modal_fragment.html",
            form=form,
            form2=form2,
            teams=teams,
            cats=cats,
            editable_team_ids=editable_team_ids,
            current_date=datetime.now(timezone.utc),
        )
    except Exception:
        current_app.logger.exception("calendar.modal ERROR")
        return "Chyba pri načítaní kalendára", 500


@calendar.route("/calendar/events", methods=["GET"])
@login_required
def events_list():
    """
    FullCalendar posiela ?start=...&end=... (ISO).
    Filtrujeme interval kvôli výkonu.
    Všetko prepočítame do UTC-naive, aby sedel typ porovnania s DB.
    """
    try:
        start_q = request.args.get("start")
        end_q = request.args.get("end")

        q = Event.query

        if start_q and end_q:
            try:
                start_dt = parse_client_dt(start_q)
                end_dt = parse_client_dt(end_q)
                if start_dt and end_dt:
                    # event prekrýva interval
                    q = q.filter(Event.start_event < end_dt, Event.end_event > start_dt)
            except Exception:
                pass

        items = q.all()
        return jsonify([_event_to_fc(e) for e in items])
    except Exception:
        current_app.logger.exception("calendar.events_list ERROR")
        return jsonify({"error": "Chyba pri načítaní udalostí"}), 500


@calendar.route("/calendar/events", methods=["POST"])
@csrf.exempt
@login_required
def events_create():
    data = request.get_json(silent=True) or {}
    if not data:
        return jsonify({"error": "Chýbajú dáta"}), 400

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
            start_event=parse_client_dt(data.get("start")),
            end_event=parse_client_dt(data.get("end")),
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


@calendar.route("/calendar/insert", methods=["POST"])
@csrf.exempt
@login_required
def insert():
    data = request.get_json(silent=True) or {}
    if not data:
        return jsonify({"error": "Chýbajú dáta"}), 400

    is_admin = _is_admin_like()
    editable = set(_editable_team_ids())

    try:
        team_id = int(data.get("team") or 0)
    except Exception:
        team_id = 0

    if not is_admin and team_id not in editable:
        return jsonify({"error": "forbidden"}), 403

    try:
        event = Event(
            title=(data.get("title") or "").strip(),
            start_event=parse_client_dt(data.get("start")),
            end_event=parse_client_dt(data.get("end")),
            user_id=current_user.id,
            address=data.get("address", ""),
            link=data.get("link", ""),
            event_category_id=int(data.get("category")),
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


@calendar.route("/calendar/update", methods=["POST", "GET"])
@csrf.exempt
@login_required
def update():
    data = request.get_json(silent=True) or {}

    if request.method == "GET":
        return jsonify({"info": "GET not implemented"}), 200

    if not data:
        return jsonify({"error": "Chýbajú dáta"}), 400

    is_admin = _is_admin_like()
    editable = set(_editable_team_ids())

    try:
        id_ = int(data.get("id2") or 0)
    except Exception:
        return jsonify({"error": "bad_id"}), 400

    try:
        event = Event.query.get(id_)
        if not event:
            return jsonify({"error": "not_found"}), 404

        # práva: kontroluj podľa existujúceho eventu (nie podľa poslaného team2)
        if not is_admin and int(event.event_team_id) not in editable:
            return jsonify({"error": "forbidden"}), 403

        # update polí - len ak prišli (neprepisuj prázdnom, ak front nič neposlal)
        if "title2" in data:
            event.title = (data.get("title2") or event.title).strip()

        if "start2" in data:
            new_start = parse_client_dt(data.get("start2"), event.start_event)
            if new_start:
                event.start_event = new_start

        if "end2" in data:
            new_end = parse_client_dt(data.get("end2"), event.end_event)
            if new_end:
                event.end_event = new_end

        if "address2" in data:
            event.address = data.get("address2") or ""

        if "link2" in data:
            event.link = data.get("link2") or ""

        if "category2" in data and data.get("category2"):
            event.event_category_id = int(data["category2"])

        # zmena tímu - ak je poslaná
        if "team2" in data and data.get("team2"):
            try:
                team_id = int(data.get("team2") or 0)
            except Exception:
                team_id = 0

            if team_id:
                # tréner môže prehodiť iba na svoj tím
                if not is_admin and team_id not in editable:
                    return jsonify({"error": "forbidden"}), 403
                event.event_team_id = team_id

        db.session.commit()
        # vráť rovno event, aby si na FE mohol urobiť setEventDates bez refetch glitchov
        return jsonify({"status": "success", "event": _event_to_fc(event)})

    except Exception:
        db.session.rollback()
        current_app.logger.exception("calendar.update ERROR")
        # flash("Chyba pri aktualizácii udalosti. Skúste to znova.", "danger")
        return jsonify({"error": "Chyba pri aktualizácii udalosti"}), 500
    finally:
        db.session.remove()


@calendar.route("/calendar/ajax_delete", methods=["POST"])
@csrf.exempt
@login_required
def ajax_delete():
    data = request.get_json(silent=True) or {}
    if not data:
        return jsonify({"error": "Chýbajú dáta"}), 400

    is_admin = _is_admin_like()
    editable = set(_editable_team_ids())

    try:
        getid = int(data["id"])
        ev = db.session.get(Event, getid)
        if not ev:
            return jsonify({"error": "not_found"}), 404

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
