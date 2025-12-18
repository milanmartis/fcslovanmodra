from datetime import datetime
from functools import wraps

from flask import (
    Blueprint, render_template, url_for, flash,
    redirect, request, jsonify, current_app, abort
)
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError

from app import db
from app.main.routes import RightColumn, Next
from app.team.forms import TeamForm

from app.models import (
    Team, User, Player, Member, Role,
    teams_members,
    TeamLineup, TeamLineupSlot,
)

team = Blueprint("team", __name__)


def roles_required(*roles):
    def deco(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if not current_user.has_role(*roles):
                abort(403)
            return fn(*args, **kwargs)
        return wrapper
    return deco


def _pos_sort_key(p):
    try:
        return int(getattr(p, "position", 99) or 99)
    except Exception:
        return 99


def _ensure_lineup(team_id: int, ordered_players: list[Player]) -> TeamLineup:
    lineup = TeamLineup.query.filter_by(team_id=team_id).first()
    if lineup:
        return lineup

    lineup = TeamLineup(team_id=team_id, formation="4-3-3")
    db.session.add(lineup)
    db.session.flush()

    for i, p in enumerate(ordered_players):
        db.session.add(
            TeamLineupSlot(
                lineup_id=lineup.id,
                player_id=p.id,
                is_starter=(i < 11),
                order_index=(i if i < 11 else i - 11),
                position=int(p.position or 0),
            )
        )

    db.session.commit()
    return lineup


def _load_starters_subs_with_slots(lineup: TeamLineup, ordered_players: list[Player]):
    players_by_id = {p.id: p for p in ordered_players}
    slots = TeamLineupSlot.query.filter_by(lineup_id=lineup.id).all()

    starter_slots = sorted([s for s in slots if s.is_starter], key=lambda s: s.order_index)
    sub_slots = sorted([s for s in slots if not s.is_starter], key=lambda s: s.order_index)

    starters = []
    for s in starter_slots:
        p = players_by_id.get(s.player_id)
        if p:
            starters.append({"player": p, "slot": int(s.order_index), "pos": int(s.position)})

    subs = []
    for s in sub_slots:
        p = players_by_id.get(s.player_id)
        if p:
            subs.append({"player": p, "pos": int(s.position)})

    if len(starters) < 11:
        used_ids = {x["player"].id for x in starters} | {x["player"].id for x in subs}
        missing = [p for p in ordered_players if p.id not in used_ids]
        for m in missing[: (11 - len(starters))]:
            starters.append({"player": m, "slot": len(starters), "pos": int(m.position or 0)})

    return starters[:11], subs


@team.route("/info")
def team_youth():
    return render_template(
        "teams/youth.html",
        current_date=datetime.now(),
        next22=Next.next(),
        teamz=RightColumn.main_menu(),
        next_match=RightColumn.next_match(),
        score_table=RightColumn.score_table(),
    )


@team.route("/teams")
def list_teams():
    teams = Team.query.order_by(Team.id.asc()).all()
    return render_template(
        "teams/list_teams.html",
        teams=teams,
        current_date=datetime.now(),
        next22=Next.next(),
        teamz=RightColumn.main_menu(),
        next_match=RightColumn.next_match(),
        score_table=RightColumn.score_table(),
    )


@team.route("/teams/new", methods=["GET", "POST"])
@login_required
@roles_required("Admin", "WebAdmin")
def new_team():
    form = TeamForm()
    if form.validate_on_submit():
        team_obj = Team(
            name=form.name.data,
            score_scrap=form.score_scrap.data,
            player_list_scrap=form.player_list_scrap.data
        )
        db.session.add(team_obj)
        db.session.commit()
        flash("A New Team has been created!", "success")
        return redirect(url_for("team.list_teams"))

    return render_template(
        "teams/create_team.html",
        title="New Team",
        form=form,
        legend="New Team",
        teamz=RightColumn.main_menu(),
        next_match=RightColumn.next_match(),
        score_table=RightColumn.score_table(),
    )


@team.route("/team/<team_name>")
def team_name(team_name):
    trener = (
        Member.query
        .join(Member.position)
        .join(Member.teams)
        .join(User, Member.user_id == User.id)
        .join(Role, User.roles)
        .filter(Role.name.in_(["Tréner", "Asistent trénera"]))
        .options(joinedload(Member.position), joinedload(Member.teams))
        .distinct()
        .all()
    )

    team_obj = Team.query.filter(Team.name.like(team_name)).first()
    members = (
        Player.query.filter(Team.id == Player.team_id)
        .filter(Team.name.like(team_name))
        .all()
    )

    ordered_players = sorted(
        [p for p in members if int(getattr(p, "position", 0) or 0) in (1, 2, 3, 4)],
        key=_pos_sort_key,
    )

    lineup = _ensure_lineup(team_obj.id, ordered_players)
    starters, subs = _load_starters_subs_with_slots(lineup, ordered_players)

    return render_template(
        "teams/team.html",
        team=team_obj,
        starters=starters,
        subs=subs,
        formation=(lineup.formation or "4-3-3"),
        trener=trener,
        teamz=RightColumn.main_menu(),
        current_date=datetime.now(),
        next22=Next.next(),
        next_match=RightColumn.next_match(),
        score_table=RightColumn.score_table(),
    )


@team.route("/api/team/<int:team_id>/lineup/formation", methods=["POST"])
def save_formation(team_id):
    data = request.get_json(force=True)
    formation = data.get("formation", "4-3-3")

    lineup = TeamLineup.query.filter_by(team_id=team_id).first()
    if not lineup:
        lineup = TeamLineup(team_id=team_id, formation=formation)
        db.session.add(lineup)

    lineup.formation = formation
    db.session.commit()
    return jsonify({"ok": True, "formation": lineup.formation})


@team.route("/api/team/<int:team_id>/lineup/swap", methods=["POST"])
def swap_players(team_id):
    data = request.get_json(force=True)
    sub_id = int(data["sub_id"])
    starter_id = int(data["starter_id"])

    lineup = TeamLineup.query.filter_by(team_id=team_id).first()
    if not lineup:
        return jsonify({"ok": False, "error": "Lineup not initialized"}), 400

    sub_slot = TeamLineupSlot.query.filter_by(lineup_id=lineup.id, player_id=sub_id).first()
    st_slot = TeamLineupSlot.query.filter_by(lineup_id=lineup.id, player_id=starter_id).first()

    if not sub_slot or not st_slot:
        return jsonify({"ok": False, "error": "Players not in lineup slots"}), 400
    if sub_slot.is_starter:
        return jsonify({"ok": False, "error": "sub_id is not a sub"}), 400
    if not st_slot.is_starter:
        return jsonify({"ok": False, "error": "starter_id is not a starter"}), 400

    sub_slot.is_starter = True
    st_slot.is_starter = False

    sub_slot.order_index, st_slot.order_index = st_slot.order_index, sub_slot.order_index
    sub_slot.position, st_slot.position = st_slot.position, sub_slot.position

    db.session.commit()
    return jsonify({"ok": True})


@team.route("/api/team/<int:team_id>/lineup/swap-slots", methods=["POST"])
def swap_starter_slots(team_id):
    data = request.get_json(force=True)
    a_id = int(data["a_id"])
    b_id = int(data["b_id"])

    lineup = TeamLineup.query.filter_by(team_id=team_id).first()
    if not lineup:
        return jsonify({"ok": False, "error": "Lineup not initialized"}), 400

    a = TeamLineupSlot.query.filter_by(lineup_id=lineup.id, player_id=a_id, is_starter=True).first()
    b = TeamLineupSlot.query.filter_by(lineup_id=lineup.id, player_id=b_id, is_starter=True).first()
    if not a or not b:
        return jsonify({"ok": False, "error": "Both must be starters"}), 400

    a.order_index, b.order_index = b.order_index, a.order_index
    db.session.commit()
    return jsonify({"ok": True})


@team.route("/teams/<int:team_id>/delete", methods=["GET", "POST"])
@login_required
def delete_team(team_id):
    team_obj = Team.query.get_or_404(team_id)
    ifemptyteam = db.session.query(teams_members).filter(teams_members.c.team_id == team_id).all()
    if ifemptyteam:
        flash("A Team is not empty!", "danger")
    else:
        try:
            db.session.delete(team_obj)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.exception("DB delete error (Team): %s", e)
            flash("Chyba pri mazaní tímu.", "danger")
            return redirect(url_for("team.list_teams"))
        flash("A Team has been deleted!", "success")
    return redirect(url_for("team.list_teams"))
