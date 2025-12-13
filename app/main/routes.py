from datetime import datetime
from flask import render_template, request, Blueprint, flash, url_for, redirect
from sqlalchemy.sql import func, and_
from sqlalchemy.orm import subqueryload
from app.aws_utils import make_sponsor_key, s3_presign
from app import db
from app.models import Post, Category, Team, Event, ScoreTable, Sponsor
from collections import defaultdict
from datetime import datetime, timedelta
main = Blueprint('main', __name__)

def get_current_season() -> str:
    """
    Jednoduchá helper funkcia – ak ešte nemáš season v DB,
    môžeš ju zatiaľ ignorovať. Použiteľná do budúcna.
    Napr. 2024/25 podľa aktuálneho dátumu.
    """
    now = datetime.now()
    year = now.year
    if now.month >= 7:
        # sezóna začína v lete
        return f"{year}/{str(year + 1)[-2:]}"
    else:
        return f"{year - 1}/{str(year)[-2:]}"

@main.route("/stats")
def stats():
    """
    NHL-style štatistiky:
    - hore taby pre tímy
    - v rámci tímu: najbližší zápas + tabuľka + výsledky + program zápasov
    """

    current_date = datetime.now()

    # ==============
    # Tímy (teamz)
    # ==============
    try:
        teamz = (
            db.session.query(Team)
            .order_by(Team.id.asc())
            .all()
        )
    except Exception:
        flash('Chyba pri načítavaní tímov.', 'danger')
        teamz = []

    if not teamz:
        # aj keď nie sú tímy, nech stránka nespadne
        return render_template(
            "teams/teams_stats.html",
            current_date=current_date,
            teamz=[],
            next_match_by_team={},
            calendar_by_team={},
            results_by_team={},
            table_by_team={},
            partners=[],
            selected_team_id=None,
            hide_sidebar_tables=True,
        )

    selected_team_name = request.args.get("team")
    selected_team_id = None
    if selected_team_name:
        for t in teamz:
            if t.name == selected_team_name:
                selected_team_id = t.id
                break

    team_ids = [t.id for t in teamz]

    # ==========================
    # Tabuľka – ScoreTable
    # ==========================
    try:
        score_rows = (
            db.session.query(ScoreTable)
            .filter(ScoreTable.team_id.in_(team_ids))
            .order_by(
                ScoreTable.team_id.asc(),
                ScoreTable.points.desc(),
                ScoreTable.games.asc()
            )
            .all()
        )
    except Exception:
        flash('Chyba pri načítavaní tabuľky výsledkov.', 'danger')
        score_rows = []

    table_by_team = defaultdict(list)
    for row in score_rows:
        table_by_team[row.team_id].append(row)

    # ==========================
    # Eventy – výsledky + program
    # ==========================
    # vezmeme rozumne dlhé obdobie dozadu aj dopredu
    now_dt = datetime.now()
    from_date = now_dt - timedelta(days=365)   # rok dozadu na výsledky
    to_date = now_dt + timedelta(days=180)     # pol roka dopredu na program

    try:
        events = (
            db.session.query(Event)
            .filter(Event.event_team_id.in_(team_ids))
            .filter(Event.start_event >= from_date)
            .filter(Event.start_event <= to_date)
            # ak chceš filtrovať len na ligové zápasy:
            # .filter(Event.event_category_id == 1)
            .order_by(Event.start_event.asc())
            .all()
        )
    except Exception:
        flash('Chyba pri načítavaní zápasov.', 'danger')
        events = []

    calendar_by_team = defaultdict(list)  # budúce zápasy (program)
    results_by_team = defaultdict(list)   # minulé zápasy (výsledky / odohrané)

    for e in events:
        if e.event_team_id not in team_ids:
            continue

        if e.start_event and e.start_event >= now_dt:
            # budúci zápas (program)
            calendar_by_team[e.event_team_id].append(e)
        else:
            # minulý zápas – zobrazíme ho vo "Výsledkoch" aj bez score
            results_by_team[e.event_team_id].append(e)

    # zoradenie – program chronologicky dopredu, výsledky od najnovších
    for tid in calendar_by_team:
        calendar_by_team[tid].sort(key=lambda m: m.start_event or datetime.max)

    for tid in results_by_team:
        results_by_team[tid].sort(
            key=lambda m: m.start_event or datetime.min,
            reverse=True  # najnovší navrchu
        )

    # =======================================
    # Najbližší zápas pre každý tím (next)
    # =======================================
    next_match_by_team = {tid: None for tid in team_ids}
    try:
        today_sql = func.now()

        subq = (
            db.session.query(
                Event.event_team_id.label("team_id"),
                func.min(Event.start_event).label("min_start"),
            )
            .filter(Event.event_team_id.in_(team_ids))
            .filter(Event.start_event >= today_sql)
            # .filter(Event.event_category_id == 1)
            .group_by(Event.event_team_id)
            .subquery()
        )

        next_events = (
            db.session.query(Event)
            .join(
                subq,
                and_(
                    Event.event_team_id == subq.c.team_id,
                    Event.start_event == subq.c.min_start,
                ),
            )
            .all()
        )

        for ev in next_events:
            next_match_by_team[ev.event_team_id] = ev

    except Exception:
        flash('Chyba pri načítavaní najbližších zápasov.', 'danger')

    # =======================================
    # Render
    # =======================================
    return render_template(
        "teams/teams_stats.html",
        current_date=current_date,
        teamz=teamz,
        next_match_by_team=next_match_by_team,
        calendar_by_team=calendar_by_team,
        results_by_team=results_by_team,
        table_by_team=table_by_team,
        selected_team_id=selected_team_id,
    )



@main.route("/tabz")
def tabz():
    return render_template(
        'tabz.html',
        current_date=datetime.now(),
        next22=Next.next(),
        teamz=RightColumn.main_menu(),
        next_match=RightColumn.next_match(),
        score_table=RightColumn.score_table(),
    )


@main.route("/")
@main.route("/home")
def home():
    page = request.args.get('page', 1, type=int)

    posts = (
        db.session.query(Post)
        .options(subqueryload(Post.gallery))
        .order_by(Post.date_posted.desc())
        .paginate(page=page, per_page=5, error_out=False)
    )

    category = db.session.query(Category).all()



    return render_template(
        'home.html',
        title='',
        posts=posts,
        current_date=datetime.now(),
        next22=Next.next(),
        category=category,
        teamz=RightColumn.main_menu(),
        next_match=RightColumn.next_match(),
        score_table=RightColumn.score_table(),    
    )


@main.route("/oklube")
def about():

    return render_template(
        'about.html',
        title='About',
        current_date=datetime.now(),
        next22=Next.next(),
        teamz=RightColumn.main_menu(),
        next_match=RightColumn.next_match(),
        score_table=RightColumn.score_table(),
    )


@main.route("/dokumenty")
def dokumenty():
    return render_template(
        'dokumenty.html',
        title='Dokumenty',
        current_date=datetime.now(),
        next22=Next.next(),
        teamz=RightColumn.main_menu(),
        next_match=RightColumn.next_match(),
        score_table=RightColumn.score_table()
    )


# @main.route("sponsors")
# def sponsors():
#     return render_template(
#         'sponsors/sponsors.html',
#         title='Sponsors',
#         current_date=datetime.now(),
#         next22=Next.next(),
#         teamz=RightColumn.main_menu(),
#         next_match=RightColumn.next_match(),
#         score_table=RightColumn.score_table()
#     )


@main.route("/sidebar/next-matches-fragment")
def sidebar_next_matches_fragment():
    return render_template("partials/next_matches_sidebar.html")

class Next:
    @staticmethod
    def next():
        try:
            today = func.now()

            # napr. chceš A-tím, U19, U17, U15, atď.
            wanted_team_ids = [1, 2, 3, 4, 5, 6]  # sem doplň ID U15

            teams = (
                db.session.query(Team.id, Team.name)
                .filter(Team.id.in_(wanted_team_ids))
                .order_by(Team.id.asc())
                .all()
            )

            next_events = []
            for team_id, team_name in teams:
                subq = (
                    db.session.query(
                        Event.event_team_id,
                        func.min(Event.start_event).label('min_start'),
                    )
                    .filter(Event.start_event >= today)
                    .filter(Event.event_category_id == 1)  # prípadne IN (...)
                    .filter(Event.event_team_id == team_id)
                    .group_by(Event.event_team_id)
                    .subquery()
                )

                event = (
                    db.session.query(Event)
                    .join(
                        subq,
                        and_(
                            Event.event_team_id == subq.c.event_team_id,
                            Event.start_event == subq.c.min_start,
                        ),
                    )
                    .order_by(Event.start_event.asc())
                    .first()
                )

                next_events.append(event if event else f"Bez údajov pre tím {team_name}")

            return next_events
        except Exception:
            flash('Chyba pri načítavaní menu tímov.', 'danger')
            return []

class RightColumn:
    @staticmethod
    def main_menu():
        try:
            return db.session.query(Team).order_by(Team.id.asc()).all()
        except Exception:
            flash('Chyba pri načítavaní menu tímov.', 'danger')
            return []

    @staticmethod
    def next_match():
        try:
            today = datetime.today()
            return (
                db.session.query(Event.title, Event.start_event)
                .filter(Event.start_event >= today)
                .filter(Event.event_category_id == 1)
                .order_by(Event.start_event.asc())
                .all()
            )
        except Exception:
            flash('Chyba pri načítavaní nasledujúcich zápasov.', 'danger')
            return []


    @staticmethod
    def score_table():
        try:
            return ScoreTable.query.all()
        except Exception:
            flash('Chyba pri načítavaní tabuľky výsledkov.', 'danger')
            return []

