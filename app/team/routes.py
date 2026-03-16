from __future__ import annotations

from app.posts.routes import s3_presign
from app.users.routes import make_member_key

import json
import re
import time
from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Dict, List, Optional

import pandas as pd
import requests
from bs4 import BeautifulSoup
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse, quote_plus

from flask import (
    Blueprint, render_template, url_for, flash,
    redirect, request, jsonify, current_app, abort
)
from flask_login import login_required, current_user

from app import csrf, db
from app.main.routes import RightColumn, Next
from app.team.forms import TeamForm
from app.models import (
    Team, ScoreTable, User, Player, Position, Member, Role,
    Event, EventCategory,
    teams_members, roles_users,
    TeamLineup, TeamLineupSlot,
)

team_bp = Blueprint("team", __name__)


def _is_ajax() -> bool:
    # robustnejšie než len X-Requested-With
    xrw = (request.headers.get("X-Requested-With") or "").lower()
    accept = (request.headers.get("Accept") or "").lower()
    return xrw == "xmlhttprequest" or "application/json" in accept


# ------------------------- Roles helper (kompatibilný) -------------------------
def roles_required_compat(*roles):
    """
    Kompatibilný wrapper:
    - ak má current_user.has_role(...) (Flask-Security) -> použije
    - ak má current_user.has_roles(...) -> použije
    - inak fallback: 403
    """
    def deco(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)

            if hasattr(current_user, "has_role") and callable(getattr(current_user, "has_role")):
                ok = current_user.has_role(*roles)
            elif hasattr(current_user, "has_roles") and callable(getattr(current_user, "has_roles")):
                ok = current_user.has_roles(*roles)
            else:
                ok = False

            if not ok:
                abort(403)

            return fn(*args, **kwargs)
        return wrapper
    return deco


# ------------------------- Pomocné funkcie -------------------------

BASE_ORIGIN = "https://sportnet.sme.sk"


def _abs_url(src: str) -> str:
    if not src:
        return ""
    if src.startswith("//"):
        return "https:" + src
    if src.startswith("/"):
        return BASE_ORIGIN + src
    return src


def _fetch_html(url: str, retries: int = 3, base_timeout: float = 8.0) -> str:
    """Stiahne HTML s redirectom, s krátkym retry/backoffom."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/119.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "sk-SK,sk;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Connection": "keep-alive",
    }

    last_err = None
    for attempt in range(1, retries + 1):
        try:
            print(f"********* FETCH URL: {url}")
            resp = requests.get(url, headers=headers, timeout=base_timeout, allow_redirects=True)
            resp.raise_for_status()
            print(f"********* FETCH OK (attempt {attempt}/{retries}): {url} | len: {len(resp.text)}")
            return resp.text
        except requests.RequestException as e:
            last_err = e
            time.sleep(0.7 * (2 ** (attempt - 1)))

    raise requests.ConnectionError(last_err)


def _to_int_series(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce").fillna(0).astype(int)


def _best_read_html_tables(html: str) -> List[pd.DataFrame]:
    """Robustná verzia pd.read_html nad už stiahnutým HTML – skúsi viac 'flavors'."""
    flavors_to_try = [
        ["lxml"], ["bs4"], ["html5lib"],
        ["lxml", "bs4"], ["lxml", "html5lib"], ["bs4", "html5lib"],
        ["lxml", "bs4", "html5lib"],
    ]
    last_exc: Optional[Exception] = None
    for flavors in flavors_to_try:
        try:
            dfs = pd.read_html(html, flavor=flavors, match=r".+")
            return dfs
        except Exception as e:
            last_exc = e
            print(f"********* read_html FAIL - flavors: {flavors} | error: {repr(e)}")
            continue
    if last_exc:
        raise last_exc
    return []


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(-1)
    df.columns = [str(c).strip() for c in df.columns]
    return df


def _html_preview_for_log(html: str, n: int = 800) -> str:
    text = (html or "").strip().replace("\n", " ")
    return (text[:n] + "...") if len(text) > n else text


def _safe_int_val(v) -> int:
    try:
        s = str(v).strip()
        if not s:
            return 0
        if ":" in s:
            return 0
        return int(float(s))
    except Exception:
        return 0


# --- Pomocné pre identifikáciu textového stĺpca „Klub“ vs. poradové číslo ---

_CLUB_NAME_SYNONYMS = {
    "klub", "mužstvo", "muzstvo", "tím", "tim", "team", "club", "družstvo", "druzstvo",
    "name", "názov", "nazov"
}


def _looks_texty(series: pd.Series, threshold: float = 0.5) -> bool:
    s = series.astype(str).str.strip()
    ratio = s.str.contains(r"[A-Za-zÁ-ž]", regex=True).mean()
    return bool(ratio > threshold)


def _fix_club_column(work: pd.DataFrame) -> pd.DataFrame:
    if "Klub" not in work.columns:
        print("********* _fix_club_column: 'Klub' column NOT present.")
        return work

    vals = work["Klub"].astype(str).str.strip()
    sample = vals.head(5).tolist()
    looks_numeric = pd.to_numeric(vals, errors="coerce").notna().mean() > 0.6
    print(f"********* _fix_club_column: initial sample={sample} | rows={len(vals)} | mostly_numeric={looks_numeric}")

    if looks_numeric:
        name_candidates = [c for c in work.columns if c.lower().strip() in _CLUB_NAME_SYNONYMS]
        print(f"********* _fix_club_column: name_candidates={name_candidates}")
        for c in name_candidates:
            if c == "Klub":
                continue
            if _looks_texty(work[c]):
                print(f"********* _fix_club_column: switched Klub -> '{c}'")
                work["Klub"] = work[c].astype(str).str.strip()
                break
        else:
            cols = list(work.columns)
            if len(cols) >= 2 and _looks_texty(work[cols[1]]):
                print(f"********* _fix_club_column: fallback using second column '{cols[1]}'")
                work["Klub"] = work[cols[1]].astype(str).str.strip()
            else:
                print("********* _fix_club_column: last resort - stripping leading numbers in 'Klub'")
                work["Klub"] = vals.str.replace(r"^\s*\d+\s*", "", regex=True).str.strip()

    work["Klub"] = work["Klub"].astype(str).str.replace(r"^\s*\d+\s*", "", regex=True).str.strip()
    print(f"********* _fix_club_column: final sample={work['Klub'].head(5).tolist()}")
    return work


# --------- DOM parser pre Sportnet tabuľku (logo + názov + čísla) ---------

def _parse_score_table_dom(html: str) -> List[Dict]:
    soup = BeautifulSoup(html, "lxml")
    rows = []
    tbodies = soup.find_all("tbody")
    if not tbodies:
        print("********* SCORE DOM: no <tbody> found")
        return rows

    for tbody in tbodies:
        for tr in tbody.find_all("tr"):
            tds = tr.find_all("td")
            if len(tds) < 2:
                continue

            logo_url = ""
            club_from_img = ""
            img = tr.find("img")
            if img:
                logo_url = _abs_url(img.get("src", "").strip())
                club_from_img = (img.get("alt", "") or "").strip()

            club_from_link = ""
            a = tds[1].find("a")
            if a:
                club_from_link = a.get_text(strip=True)

            club = club_from_link or club_from_img
            if not club:
                club = tds[1].get_text(strip=True)

            def _td_text(i: int) -> str:
                return tds[i].get_text(strip=True) if i < len(tds) else ""

            z_txt = _td_text(2)
            v_txt = _td_text(3)
            r_txt = _td_text(4)
            p_txt = _td_text(5)
            score_txt = _td_text(6)
            b_txt = _td_text(7)

            row = {
                "club": club,
                "logo": logo_url,
                "Z": _safe_int_val(z_txt),
                "V": _safe_int_val(v_txt),
                "R": _safe_int_val(r_txt),
                "P": _safe_int_val(p_txt),
                "Skóre": score_txt,
                "B": _safe_int_val(b_txt),
            }
            rows.append(row)

    print(f"********* SCORE DOM: total parsed rows={len(rows)}")
    return rows


# ------------------------- PLAYERS parsing -------------------------

def _normalize_player_name(name: str) -> str:
    name = re.sub(r"\s+", " ", (name or "")).strip()
    return name


def _find_player_name_col(df: pd.DataFrame) -> str:
    cols = [str(c).strip() for c in df.columns]
    low = {c.lower(): c for c in cols}
    for k in ("hráč", "hrac", "meno", "name", "player"):
        if k in low:
            return low[k]
    return cols[0]


def _parse_players_from_html(html: str) -> List[Dict]:
    tables = _best_read_html_tables(html)
    if not tables:
        return []

    best_df = None
    best_score = -1
    for raw in tables:
        df = _normalize_columns(raw)
        colset = {str(c).lower().strip() for c in df.columns}

        score = 0
        if any(x in colset for x in ["hráč", "hrac", "meno", "name", "player"]):
            score += 2
        if any(x in colset for x in ["g", "goals", "žk", "zk", "čk", "ck", "karty", "cards"]):
            score += 1
        if len(df.columns) >= 2 and len(df) >= 5:
            score += 1

        if score > best_score:
            best_score = score
            best_df = df

    if best_df is None:
        return []

    name_col = _find_player_name_col(best_df)
    cols_low = {str(c).lower().strip(): c for c in best_df.columns}

    goals_col = cols_low.get("g") or cols_low.get("goals") or cols_low.get("skóre") or cols_low.get("skore")
    yellow_col = cols_low.get("žk") or cols_low.get("zk") or cols_low.get("yellow")
    red_col = cols_low.get("čk") or cols_low.get("ck") or cols_low.get("red")
    pos_col = cols_low.get("post") or cols_low.get("poz") or cols_low.get("pozícia") or cols_low.get("pozicia") or cols_low.get("position")

    out: List[Dict] = []
    seen = set()

    for _, row in best_df.iterrows():
        name = _normalize_player_name(str(row.get(name_col, "")))
        if not name or name.lower() in {"nan", "none"}:
            continue
        if name in seen:
            continue
        seen.add(name)

        out.append({
            "name": name,
            "score": _safe_int_val(row.get(goals_col)) if goals_col else 0,
            "yellow_card": _safe_int_val(row.get(yellow_col)) if yellow_col else 0,
            "red_card": _safe_int_val(row.get(red_col)) if red_col else 0,
            "position": _safe_int_val(row.get(pos_col)) if pos_col else 0,
        })

    return out


# ------------------------- Sportnet API (events) -------------------------

def _fetch_all_api_items(base_url: str) -> list[dict]:
    parsed = urlparse(base_url)
    qs = dict(parse_qsl(parsed.query, keep_blank_values=True))
    if "limit" not in qs:
        qs["limit"] = "100"
    if "offset" not in qs:
        qs["offset"] = "0"
    url = urlunparse(parsed._replace(query=urlencode(qs, doseq=True)))

    print("********* FETCH API PAGE:", url)
    text = _fetch_html(url)
    try:
        data = json.loads(text)
    except Exception as e:
        print("********* API JSON parse error:", e)
        return []

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        for key in ("matches", "items", "data", "results"):
            if isinstance(data.get(key), list):
                return data[key]

        embedded = data.get("_embedded") or data.get("embedded")
        if isinstance(embedded, dict):
            for key in ("matches", "items", "data", "results"):
                if isinstance(embedded.get(key), list):
                    return embedded[key]

        for v in data.values():
            if isinstance(v, list) and v and isinstance(v[0], dict):
                return v

    return []


def _get_match_event_category_id() -> int:
    cat = EventCategory.query.filter(EventCategory.name.ilike("Z%pas")).first()
    if cat:
        return int(cat.id)
    return 1


def _parse_api_datetime_utc(start_str: str) -> datetime:
    """
    Sportnet typicky posiela ISO s 'Z' (UTC).
    Vrátime AWARE datetime v UTC.
    """
    if not start_str:
        raise ValueError("empty datetime string")

    s = start_str.strip()

    # Ak končí Z -> UTC
    if s.endswith("Z"):
        s2 = s[:-1]
        # môže byť aj s .ms
        if "." in s2:
            s2 = s2.split(".")[0]
        dt = datetime.strptime(s2, "%Y-%m-%dT%H:%M:%S")
        return dt.replace(tzinfo=timezone.utc)

    # Ak má offset (+01:00) -> fromisoformat to zvládne (py3.11+)
    try:
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            # fallback: ber ako UTC
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        # fallback na tvoj pôvodný parsing bez TZ -> ber ako UTC
        s2 = s
        if "." in s2:
            s2 = s2.split(".")[0]
        dt = datetime.strptime(s2, "%Y-%m-%dT%H:%M:%S")
        return dt.replace(tzinfo=timezone.utc)


def _event_data_from_api_match(item: dict) -> dict | None:
    """
    FIX TIMEZONE:
    - API datetime parsujeme ako UTC aware
    - do DB ukladáme NAIVE UTC (bez tzinfo), aby tvoja to_local() fungovala jednotne
    """
    try:
        match_id = item.get("_id") or item.get("id") or item.get("matchId")
        if not match_id:
            return None

        home = item.get("homeTeam") or {}
        away = item.get("awayTeam") or {}
        home_name = (home.get("name") or "").strip()
        away_name = (away.get("name") or "").strip()
        if not home_name or not away_name:
            return None

        state = (item.get("matchState") or "").upper()
        home_score = home.get("score")
        away_score = away.get("score")

        has_scores = (
            state == "ODOHRATY"
            and isinstance(home_score, (int, float))
            and isinstance(away_score, (int, float))
        )

        if has_scores:
            title = f"{home_name} {int(home_score)}:{int(away_score)} {away_name}"
        else:
            title = f"{home_name} - {away_name}"

        start_str = item.get("startDate") or item.get("dateFrom") or item.get("date_from")
        if not start_str:
            return None

        start_dt_utc_aware = _parse_api_datetime_utc(start_str)

        end_str = item.get("endDate") or item.get("dateTo") or item.get("date_to")
        if end_str:
            end_dt_utc_aware = _parse_api_datetime_utc(end_str)
        else:
            end_dt_utc_aware = start_dt_utc_aware + timedelta(hours=2)

        # ✅ DB: NAIVE UTC
        start_dt = start_dt_utc_aware.replace(tzinfo=None)
        end_dt = end_dt_utc_aware.replace(tzinfo=None)

        event_address = "Navigácia na štadión"
        destination_str = f"Štadión {home_name}"
        gm_url = "https://www.google.com/maps/dir/?api=1&destination=" + quote_plus(destination_str)

        return {
            "match_id": match_id,
            "title": title.strip(),
            "start_dt": start_dt,
            "end_dt": end_dt,
            "address": event_address,
            "link": gm_url,
        }

    except Exception as e:
        print("********* API ITEM PARSE ERROR:", e)
        return None


# ------------------------- Lineup helpers -------------------------

def _pos_sort_key(p: Player):
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
                position=int(getattr(p, "position", 0) or 0),
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
            starters.append({"player": p, "slot": int(s.order_index), "pos": int(getattr(p, "position", 0) or 0)})

    subs = []
    for s in sub_slots:
        p = players_by_id.get(s.player_id)
        if p:
            subs.append({"player": p, "pos": int(getattr(p, "position", 0) or 0)})

    if len(starters) < 11:
        used_ids = {x["player"].id for x in starters} | {x["player"].id for x in subs}
        missing = [p for p in ordered_players if p.id not in used_ids]
        for m in missing[: (11 - len(starters))]:
            starters.append({"player": m, "slot": len(starters), "pos": int(getattr(m, "position", 0) or 0)})

    return starters[:11], subs


# ------------------------- Routes -------------------------

@team_bp.route("/info")
def team_youth():
    return render_template(
        "teams/youth.html",
        current_date=datetime.now(timezone.utc),  # ✅ UTC aware
        next22=Next.next(),
        teamz=RightColumn.main_menu(),
        next_match=RightColumn.next_match(),
        score_table=RightColumn.score_table(),
    )


@team_bp.route("/teams")
def list_teams():
    teams = Team.query.order_by(Team.id.asc()).all()
    return render_template(
        "teams/list_teams.html",
        teams=teams,
        current_date=datetime.now(timezone.utc),  # ✅ UTC aware
        next22=Next.next(),
        teamz=RightColumn.main_menu(),
        next_match=RightColumn.next_match(),
        score_table=RightColumn.score_table(),
    )


@team_bp.route("/teams/new", methods=["GET", "POST"])
@login_required
@roles_required_compat("Admin", "WebAdmin")
def new_team():
    form = TeamForm()
    if form.validate_on_submit():
        team_obj = Team(
            name=form.name.data,
            score_scrap=form.score_scrap.data,
            player_list_scrap=form.player_list_scrap.data,
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


@team_bp.route("/team/<team_name>")
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

    team_obj = Team.query.filter(Team.name.like(team_name)).first_or_404()
    can_edit = team_obj.can_edit_lineup(current_user)
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

    coaches = (
        Member.query
        .join(User)
        .join(roles_users)
        .join(Role)
        .join(teams_members)
        .filter(
            teams_members.c.team_id == team_obj.id,
            Role.name == "Coach"
        )
        .all()
    )

    fallback = url_for('static', filename='img/avatar.svg')

    coach_cards = []
    for m in coaches:
        img = None
        if m.image_file and m.image_file != "default.png":
            try:
                img = s3_presign(make_member_key(m.id, m.image_file))
            except Exception:
                img = None

        coach_cards.append({
            "name": m.name,
            "phone": m.phone,
            "positions": [p.name for p in (m.position or [])],  # Tréner / Asistent trénera
            "image_url": img or fallback,
        })

    return render_template(
        "teams/team.html",
        team=team_obj,
        starters=starters,
        subs=subs,
        formation=(lineup.formation or "4-3-3"),
        trener=trener,
        teamz=RightColumn.main_menu(),
        current_date=datetime.now(timezone.utc),  # ✅ UTC aware
        next22=Next.next(),
        next_match=RightColumn.next_match(),
        score_table=RightColumn.score_table(),
        can_edit_lineup=can_edit,
        coaches=coaches,
        coach_cards=coach_cards,
    )


@team_bp.route("/teams/<int:team_id>/update", methods=["GET", "POST"])
@login_required
@csrf.exempt
@any_roles_required(global_roles=["Admin"], club_roles=["Coach", "WebAdmin"])
def update_team(team_id):
    team_obj = _team_or_404(team_id)
    form = TeamForm(obj=team_obj)

    raw_what = (request.form.get("what") or request.form.get("action") or "").strip().lower()
    what = raw_what or None

    WHAT_SCORE = {"score", "table", "league", "score_table", "scoretable"}
    WHAT_PLAYERS = {"players", "player", "lineup", "player_list"}
    WHAT_EVENTS = {"events", "event", "results", "matches", "fixtures"}

    if request.method == "POST" and _is_ajax() and what and (what not in (WHAT_SCORE | WHAT_PLAYERS | WHAT_EVENTS)):
        return jsonify({"ok": False, "category": "danger", "message": f"Neznáma akcia what='{what}'"}), 400

    current_app.logger.warning(
        "UPDATE_TEAM CID=%s team_id=%s what=%r form_keys=%s score_scrap=%r",
        _cid(), team_id, what, list(request.form.keys()), request.form.get("score_scrap")
    )

    if request.method == "GET":
        return render_template(
            "teams/create_team.html",
            title="Update Team",
            form=form,
            team=team_obj,
            legend="Update Team",
            teamz=RightColumn.main_menu(),
            current_date=datetime.now(),
            next22=Next.next(),
            next_match=RightColumn.next_match(),
            score_table=RightColumn.score_table(),
        )

    # ==========================================================
    # 1) TABLE OF LIGUE
    # ==========================================================
    if what in WHAT_SCORE:
        score_scrap = (request.form.get("score_scrap") or getattr(team_obj, "score_scrap", None) or "").strip()
        if not score_scrap:
            msg = "Table of Ligue: link je prázdny."
            current_app.logger.warning("SCORE: missing score_scrap")
            if _is_ajax():
                return jsonify({"ok": False, "category": "warning", "message": msg}), 400
            flash(msg, "warning")
            return redirect(url_for("team.update_team", team_id=team_id))

        try:
            html = _fetch_html(score_scrap)
            dom_rows = _parse_score_table_dom(html)

            current_app.logger.warning("SCORE: parsed rows=%s", len(dom_rows))

            if not dom_rows:
                msg = "Table of Ligue: nenašiel som tabuľku."
                current_app.logger.warning("SCORE: no rows after parse")
                if _is_ajax():
                    return jsonify({"ok": False, "category": "warning", "message": msg}), 400
                flash(msg, "warning")
                return redirect(url_for("team.update_team", team_id=team_id))

            seen = set()
            cleaned = []
            for row in dom_rows:
                club = str(row.get("club", "")).strip()
                if not club:
                    continue
                k = club.lower()
                if k in seen:
                    continue
                seen.add(k)
                cleaned.append(row)

            current_app.logger.warning("SCORE: cleaned unique rows=%s", len(cleaned))

            if not cleaned:
                msg = "Table of Ligue: tabuľka sa našla, ale riadky sú prázdne/duplicitné."
                current_app.logger.warning("SCORE: cleaned empty")
                if _is_ajax():
                    return jsonify({"ok": False, "category": "warning", "message": msg}), 400
                flash(msg, "warning")
                return redirect(url_for("team.update_team", team_id=team_id))

            ScoreTable.query.filter(
                ScoreTable.team_id == team_id,
                ScoreTable.club_id == _cid()
            ).delete(synchronize_session=False)

            inserted = 0
            for row in cleaned:
                club = str(row.get("club", "")).strip()
                logo = str(row.get("logo", "")).strip()[:2048]
                score_txt = str(row.get("Skóre", "")).strip()[:64]

                db.session.add(ScoreTable(
                    club=club,
                    logo=logo,
                    games=int(row.get("Z", 0) or 0),
                    wins=int(row.get("V", 0) or 0),
                    draws=int(row.get("R", 0) or 0),
                    loses=int(row.get("P", 0) or 0),
                    score=score_txt,
                    points=int(row.get("B", 0) or 0),
                    team_id=team_id,
                    club_id=_cid(),
                ))
                inserted += 1

            db.session.commit()

            msg = f"Table of Ligue: úspešne aktualizované ({inserted} záznamov)."
            current_app.logger.warning("SCORE: commit OK inserted=%s", inserted)
            if _is_ajax():
                return jsonify({"ok": True, "category": "success", "message": msg})
            flash(msg, "success")
            return redirect(url_for("team.update_team", team_id=team_id))

        except IntegrityError:
            db.session.rollback()
            current_app.logger.exception("SCORE: IntegrityError")
            msg = "Table of Ligue: DB konflikt (duplicitný riadok alebo NOT NULL). Pozri log."
            if _is_ajax():
                return jsonify({"ok": False, "category": "danger", "message": msg}), 400
            flash(msg, "danger")
            return redirect(url_for("team.update_team", team_id=team_id))

        except DataError:
            db.session.rollback()
            current_app.logger.exception("SCORE: DataError")
            msg = "Table of Ligue: DB DataError (napr. príliš dlhý text). Pozri log."
            if _is_ajax():
                return jsonify({"ok": False, "category": "danger", "message": msg}), 400
            flash(msg, "danger")
            return redirect(url_for("team.update_team", team_id=team_id))

        except requests.RequestException:
            db.session.rollback()
            current_app.logger.exception("SCORE: RequestException")
            msg = "Table of Ligue: nepodarilo sa načítať stránku (sieťová chyba)."
            if _is_ajax():
                return jsonify({"ok": False, "category": "danger", "message": msg}), 400
            flash(msg, "danger")
            return redirect(url_for("team.update_team", team_id=team_id))

        except Exception:
            db.session.rollback()
            current_app.logger.exception("SCORE: Unexpected error")
            msg = "Table of Ligue: neočakávaná chyba pri spracovaní/ukladaní. Pozri log."
            if _is_ajax():
                return jsonify({"ok": False, "category": "danger", "message": msg}), 400
            flash(msg, "danger")
            return redirect(url_for("team.update_team", team_id=team_id))


    # 2) PLAYERS
    # ==========================================================

    def _strip_accents(s: str) -> str:
        s = (s or "").strip().lower()
        s = unicodedata.normalize("NFKD", s)
        return "".join(ch for ch in s if not unicodedata.combining(ch))

    def _name_key(name: str) -> str:
        return _strip_accents(re.sub(r"\s+", " ", (name or "")).strip())

    def _parse_players_from_dom(html: str) -> list[dict]:
        """
        Súpiska (hraci):
        - vyberie hráčov podľa sekcií Brankári/Obrancovia/Záložníci/Útočníci
        - + staff: Tréner/Technický vedúci/Lekár/Fyzioterapeut (101-104)
        - vráti name + position
        """
        soup = BeautifulSoup(html, "lxml")

        HEADINGS = [
            (re.compile(r"^\s*brank[aá]ri\s*$", re.I), 1),
            (re.compile(r"^\s*obrancovia\s*$", re.I), 2),
            (re.compile(r"^\s*z[aá]lo[zž]n[ií]ci\s*$", re.I), 3),
            (re.compile(r"^\s*[uú]to[cč]n[ií]ci\s*$", re.I), 4),

            # --- staff (podľa zdroja) ---
            (re.compile(r"^\s*tr[eé]ner\s*$", re.I), 101),
            (re.compile(r"^\s*technick[yý]\s+ved[uú]ci\s*$", re.I), 102),
            (re.compile(r"^\s*lek[aá]r\s*$", re.I), 103),
            (re.compile(r"^\s*fyzioterapeut\s*$", re.I), 104),
        ]

        # veci, ktoré NIKDY nechceme uložiť ako meno
        BAD_NAME_RX = re.compile(
            r"(sledujte\s+n[aá]s|copyright|inzercia|ochrana\s+osobn|nariadenie\s+dsa|sportnet\.sk|futbalnet\.sk|©|\|)",
            re.I
        )

        def match_pos(text: str) -> int:
            t = (text or "").strip()
            for rx, pos in HEADINGS:
                if rx.match(t):
                    return pos
            return 0

        def is_player_link(a) -> bool:
            href = (a.get("href") or "").strip()
            # len reálne profily členov
            return href.startswith("/futbalnet/clen/")

        def norm_name(s: str) -> str:
            return re.sub(r"\s+", " ", (s or "")).strip()

        def looks_like_real_name(name: str) -> bool:
            if not name:
                return False
            if len(name) < 3:
                return False
            # hard stop na footery
            if BAD_NAME_RX.search(name):
                return False
            # príliš dlhé = takmer určite bordel
            if len(name) > 80:
                return False
            # ak je to celé bez písmen -> nie
            if not re.search(r"[A-Za-zÁÄČĎÉÍĹĽŇÓÔÖŘŠŤÚÜÝŽáäčďéíĺľňóôöřšťúüýž]", name):
                return False
            # príliš veľa slov = podozrivé (footer text)
            if len(name.split()) > 4:
                return False
            return True

        out: list[dict] = []
        seen = set()

        # 1) nájdi nadpisy sekcií (string nodes)
        heading_nodes: list[tuple] = []
        for node in soup.find_all(string=True):
            pos = match_pos(str(node))
            if pos:
                heading_nodes.append((node, pos))

        # fallback: žiadne nadpisy -> len profily (pos=0)
        if not heading_nodes:
            for a in soup.find_all("a", href=True):
                if not is_player_link(a):
                    continue
                name = norm_name(a.get_text(" ", strip=True))
                if not looks_like_real_name(name):
                    continue
                k = _name_key(name)
                if k in seen:
                    continue
                seen.add(k)
                out.append({"name": name, "position": 0, "score": 0, "yellow_card": 0, "red_card": 0, "photo_url": ""})
            return out

        # 2) pre každý nadpis zbieraj linky až po ďalší nadpis
        #    dôležité: stopujeme aj keď narazíme na footer/nav typické texty
        for idx, (node, pos) in enumerate(heading_nodes):
            start_el = node.parent
            end_el = heading_nodes[idx + 1][0].parent if idx + 1 < len(heading_nodes) else None

            for el in start_el.next_elements:
                if end_el is not None and el is end_el:
                    break

                if not hasattr(el, "name"):
                    continue

                if el.name == "a" and el.has_attr("href") and is_player_link(el):
                    name = norm_name(el.get_text(" ", strip=True))
                    if not looks_like_real_name(name):
                        continue

                    k = _name_key(name)
                    if k in seen:
                        continue
                    seen.add(k)

                    out.append({
                        "name": name,
                        "position": int(pos),
                        "score": 0,
                        "yellow_card": 0,
                        "red_card": 0,
                        "photo_url": "",
                    })

        return out

    def _parse_player_stats_from_dom(html: str) -> dict[str, dict]:
        """
        Štatistika hráčov (statistika-hracov):
        - vytiahne photo + čísla
        - vráti dict keyed podľa normalizovaného mena
        { name_key: {score, yellow_card, red_card, photo_url} }
        """
        soup = BeautifulSoup(html, "lxml")

        def is_player_link(a) -> bool:
            href = (a.get("href") or "").strip()
            return href.startswith("/futbalnet/clen/")

        stats: dict[str, dict] = {}

        for a in soup.find_all("a", href=True):
            if not is_player_link(a):
                continue

            name = re.sub(r"\s+", " ", a.get_text(" ", strip=True)).strip()
            if not name:
                continue

            # skús nájsť obrázok v okolí
            photo_url = ""
            img = None
            # najčastejšie býva img v rovnakom "carde" ako meno
            parent = a.parent
            if parent:
                img = parent.find("img")
            if not img:
                img = a.find_previous("img")
            if img:
                photo_url = _abs_url((img.get("src") or "").strip())

            # čísla sú hneď za menom (v rovnakom kontajneri)
            nums: list[int] = []
            container = a.parent
            if container:
                # vezmeme texty zo siblingov za <a>
                for sib in a.next_siblings:
                    if len(nums) >= 4:
                        break
                    if hasattr(sib, "get_text"):
                        t = sib.get_text(" ", strip=True)
                    else:
                        t = str(sib).strip()
                    # vyber všetky standalone čísla
                    for m in re.findall(r"\b\d+\b", t):
                        nums.append(int(m))
                        if len(nums) >= 4:
                            break

            # heuristika Sportnet: [góly, ŽK, ČK, ...]
            score = nums[0] if len(nums) > 0 else 0
            yellow = nums[1] if len(nums) > 1 else 0
            red = nums[2] if len(nums) > 2 else 0

            k = _name_key(name)
            stats[k] = {
                "score": int(score),
                "yellow_card": int(yellow),
                "red_card": int(red),
                "photo_url": photo_url,
            }

        return stats


    if what in WHAT_PLAYERS:
        player_list_scrap = (
            request.form.get("player_list_scrap")
            or getattr(team_obj, "player_list_scrap", None)
            or ""
        ).strip()

        if not player_list_scrap:
            msg = "Players LineUp: link je prázdny."
            current_app.logger.warning("PLAYERS: missing player_list_scrap")
            if _is_ajax():
                return jsonify({"ok": False, "category": "warning", "message": msg}), 400
            flash(msg, "warning")
            return redirect(url_for("team.update_team", team_id=team_id))

        try:
            html, status, ct, final_url = _fetch_url(player_list_scrap)

            players: List[Dict] = []

            # 0) JSON režim
            looks_json = (
                "application/json" in (ct or "")
                or (html.lstrip().startswith("{") or html.lstrip().startswith("["))
            )
            if looks_json:
                try:
                    payload = json.loads(html)
                    players = _parse_players_from_json_payload(payload)
                    current_app.logger.warning("PLAYERS: JSON mode parsed=%s", len(players))
                except Exception:
                    current_app.logger.exception("PLAYERS: JSON parse failed")

            # 1) Sportnet roster DOM
            if not players:
                players = _parse_players_from_dom(html)

            # 2) fallback: tabuľky
            if not players:
                players = _parse_players_from_html(html)

            # 3) stats + fotky
            stats_map: dict[str, dict] = {}
            try:
                stats_url = re.sub(r"/hraci/?($|\?)", r"/statistika-hracov/\1", final_url)
                stats_html, s_status, s_ct, s_final = _fetch_url(stats_url)
                stats_map = _parse_player_stats_from_dom(stats_html)
                current_app.logger.warning("PLAYERS: stats parsed=%s from=%s", len(stats_map), s_final)
            except Exception:
                current_app.logger.exception("PLAYERS: stats fetch/parse failed (non-fatal)")

            # merge stats into players
            merged: List[Dict] = []
            for p in players:
                name = str((p or {}).get("name", "")).strip()
                if not name:
                    continue
                k = _name_key(name)
                st = stats_map.get(k, {})

                merged.append({
                    "name": name,
                    "position": int((p or {}).get("position", 0) or 0),
                    "score": int(st.get("score", (p or {}).get("score", 0) or 0)),
                    "yellow_card": int(st.get("yellow_card", (p or {}).get("yellow_card", 0) or 0)),
                    "red_card": int(st.get("red_card", (p or {}).get("red_card", 0) or 0)),
                    "photo_url": str(st.get("photo_url", (p or {}).get("photo_url", "") or "")).strip(),
                })

            current_app.logger.warning(
                "PLAYERS: parsed rows=%s status=%s ct=%s final=%s",
                len(merged), status, ct, final_url
            )

            if not merged:
                msg = "Players LineUp: nenašiel som žiadnych hráčov na stránke."
                if _is_ajax():
                    return jsonify({"ok": False, "category": "warning", "message": msg}), 400
                flash(msg, "warning")
                return redirect(url_for("team.update_team", team_id=team_id))

            # dedup + clean + DEFENZÍVNY FILTER proti footer bordelu
            BAD_NAME_RX = re.compile(
                r"(sledujte\s+n[aá]s|copyright|inzercia|ochrana\s+osobn|nariadenie\s+dsa|sportnet\.sk|futbalnet\.sk|©|\|)",
                re.I
            )

            def _looks_ok_name(n: str) -> bool:
                n = (n or "").strip()
                if not n:
                    return False
                if BAD_NAME_RX.search(n):
                    return False
                if len(n) > 80:  # ochrana proti footer textu
                    return False
                if len(n.split()) > 4:
                    return False
                return True

            seen = set()
            cleaned: List[Dict] = []
            for p in merged:
                name = str((p or {}).get("name", "")).strip()
                if not _looks_ok_name(name):
                    continue

                k = _name_key(name)
                if k in seen:
                    continue
                seen.add(k)

                photo_url = str((p or {}).get("photo_url", "") or "").strip()

                # ✅ RÝCHLY FIX BEZ MIGRÁCIE: orezanie dĺžok podľa DB limitu (250)
                name_db = name[:250]
                photo_db = photo_url[:250]

                cleaned.append({
                    "name": name_db,
                    "position": int((p or {}).get("position", 0) or 0),
                    "score": int((p or {}).get("score", 0) or 0),
                    "yellow_card": int((p or {}).get("yellow_card", 0) or 0),
                    "red_card": int((p or {}).get("red_card", 0) or 0),
                    "photo_url": photo_db,
                })

            current_app.logger.warning("PLAYERS: cleaned unique rows=%s", len(cleaned))

            if not cleaned:
                msg = "Players LineUp: našiel som dáta, ale mená hráčov sú prázdne/duplicitné alebo filtrom vyhodené."
                if _is_ajax():
                    return jsonify({"ok": False, "category": "warning", "message": msg}), 400
                flash(msg, "warning")
                return redirect(url_for("team.update_team", team_id=team_id))

            # ----------------------------------------------------
            # ✅ FIX FK: najprv zmaž sloty (a prípadne celý lineup)
            # ----------------------------------------------------
            lineup = TeamLineup.query.filter_by(team_id=team_id).first()
            if lineup is not None and hasattr(lineup, "club_id"):
                lineup = TeamLineup.query.filter_by(team_id=team_id, club_id=_cid()).first()

            if lineup:
                slots_q = TeamLineupSlot.query.filter_by(lineup_id=lineup.id)
                if hasattr(TeamLineupSlot, "club_id"):
                    slots_q = slots_q.filter(TeamLineupSlot.club_id == _cid())
                slots_q.delete(synchronize_session=False)
                db.session.flush()

            # delete old players (club-scoped)
            del_q = Player.query.filter(Player.team_id == team_id)
            if hasattr(Player, "club_id"):
                del_q = del_q.filter(Player.club_id == _cid())
            del_q.delete(synchronize_session=False)
            db.session.flush()

            # insert new players
            inserted = 0
            for p in cleaned:
                obj = Player(
                    name=p["name"],
                    position=p["position"],
                    team=team_obj.name,
                    score=p["score"],
                    yellow_card=p["yellow_card"],
                    red_card=p["red_card"],
                    team_id=team_id,
                    photo_url=p["photo_url"],
                )
                if hasattr(obj, "club_id"):
                    obj.club_id = _cid()

                db.session.add(obj)
                inserted += 1

            db.session.flush()  # nech sú player.id dostupné pre rebuild

            # ----------------------------------------------------
            # ✅ REBUILD: po inserte obnov lineup sloty
            # ----------------------------------------------------
            ordered_players = Player.query.filter_by(team_id=team_id).order_by(Player.position.asc(), Player.name.asc()).all()
            if hasattr(Player, "club_id"):
                ordered_players = Player.query.filter_by(team_id=team_id, club_id=_cid()).order_by(Player.position.asc(), Player.name.asc()).all()

            _ensure_lineup(team_id, ordered_players)

            db.session.commit()

            msg = f"Players LineUp: úspešne aktualizované ({inserted} hráčov)."
            current_app.logger.warning("PLAYERS: commit OK inserted=%s", inserted)

            if _is_ajax():
                return jsonify({"ok": True, "category": "success", "message": msg})
            flash(msg, "success")
            return redirect(url_for("team.update_team", team_id=team_id))

        except IntegrityError:
            db.session.rollback()
            current_app.logger.exception("PLAYERS: IntegrityError")
            msg = "Players LineUp: DB konflikt (duplicitný hráč / NOT NULL). Pozri log."
            if _is_ajax():
                return jsonify({"ok": False, "category": "danger", "message": msg}), 400
            flash(msg, "danger")
            return redirect(url_for("team.update_team", team_id=team_id))

        except DataError:
            db.session.rollback()
            current_app.logger.exception("PLAYERS: DataError")
            msg = "Players LineUp: DB DataError (napr. príliš dlhý text). Pozri log."
            if _is_ajax():
                return jsonify({"ok": False, "category": "danger", "message": msg}), 400
            flash(msg, "danger")
            return redirect(url_for("team.update_team", team_id=team_id))

        except requests.RequestException:
            db.session.rollback()
            current_app.logger.exception("PLAYERS: RequestException")
            msg = "Players LineUp: nepodarilo sa načítať stránku (sieťová chyba)."
            if _is_ajax():
                return jsonify({"ok": False, "category": "danger", "message": msg}), 400
            flash(msg, "danger")
            return redirect(url_for("team.update_team", team_id=team_id))

        except Exception:
            db.session.rollback()
            current_app.logger.exception("PLAYERS: Unexpected error")
            msg = "Players LineUp: nepodarilo sa spracovať hráčov (parse/neočakávaná chyba)."
            if _is_ajax():
                return jsonify({"ok": False, "category": "danger", "message": msg}), 400
            flash(msg, "danger")
            return redirect(url_for("team.update_team", team_id=team_id))


    # ==========================================================
    # 3) EVENTS
    # ==========================================================
    if what in WHAT_EVENTS:
        events_results_scrap = (request.form.get("events_results_scrap") or getattr(team_obj, "events_results_scrap", None) or "").strip()
        if not events_results_scrap:
            msg = "Matches results: link je prázdny."
            if _is_ajax():
                return jsonify({"ok": False, "category": "warning", "message": msg}), 400
            flash(msg, "warning")
            return redirect(url_for("team.update_team", team_id=team_id))

        match_cat_id = _get_match_event_category_id()

        try:
            all_items = _fetch_all_api_items(events_results_scrap)

            prepared = []
            seen_keys = set()

            for item in all_items:
                data = _event_data_from_api_match(item)
                if not data:
                    continue

                key = (str(data["match_id"]), data["start_dt"])
                if key in seen_keys:
                    continue
                seen_keys.add(key)
                prepared.append(data)

            if not prepared:
                msg = "Matches results: API nenašlo žiadne zápasy."
                if _is_ajax():
                    return jsonify({"ok": False, "category": "warning", "message": msg}), 400
                flash(msg, "warning")
                return redirect(url_for("team.update_team", team_id=team_id))

            q = Event.query.filter(
                Event.event_team_id == team_id,
                Event.event_category_id == match_cat_id
            )
            if hasattr(Event, "club_id"):
                q = q.filter(Event.club_id == _cid())
            q.delete(synchronize_session=False)

            inserted = 0
            for data in prepared:
                ev = Event(
                    title=data["title"],
                    start_event=data["start_dt"],
                    end_event=data["end_dt"],
                    address=data["address"],
                    link=data["link"],
                    user_id=current_user.id,
                    event_category_id=match_cat_id,
                    event_team_id=team_id,
                )
                if hasattr(ev, "club_id"):
                    ev.club_id = _cid()

                db.session.add(ev)
                inserted += 1

            db.session.commit()

            msg = f"Matches results: úspešne aktualizované ({inserted} zápasov)."
            if _is_ajax():
                return jsonify({"ok": True, "category": "success", "message": msg})
            flash(msg, "success")
            return redirect(url_for("team.update_team", team_id=team_id))

        except IntegrityError:
            db.session.rollback()
            current_app.logger.exception("EVENTS: IntegrityError")
            msg = "Matches results: DB konflikt (duplicitný event / NOT NULL). Pozri log."
            if _is_ajax():
                return jsonify({"ok": False, "category": "danger", "message": msg}), 400
            flash(msg, "danger")
            return redirect(url_for("team.update_team", team_id=team_id))

        except requests.RequestException:
            db.session.rollback()
            current_app.logger.exception("EVENTS: RequestException")
            msg = "Matches results: nepodarilo sa načítať API (sieťová chyba)."
            if _is_ajax():
                return jsonify({"ok": False, "category": "danger", "message": msg}), 400
            flash(msg, "danger")
            return redirect(url_for("team.update_team", team_id=team_id))

        except Exception:
            db.session.rollback()
            current_app.logger.exception("EVENTS: Unexpected error")
            msg = "Matches results: neočakávaná chyba pri spracovaní/ukladaní. Pozri log."
            if _is_ajax():
                return jsonify({"ok": False, "category": "danger", "message": msg}), 400
            flash(msg, "danger")
            return redirect(url_for("team.update_team", team_id=team_id))

    def _posted_visible_int(default: int = 0) -> int:
        """
        Bezpečne zoberie visible z request.form aj keď príde viac hodnôt
        (hidden 0 + checkbox 1, alebo len SelectField).
        Vyberieme POSLEDNÚ hodnotu, lebo tá býva '1' ak je checkbox zaškrtnutý.
        """
        vals = request.form.getlist("visible")
        if not vals:
            return int(default)
        try:
            return int(vals[-1])
        except Exception:
            return int(default)
    
    # ==========================================================
    # 4) SAVE META
    # ==========================================================
    if form.validate_on_submit() and not what:
        team_obj.name = form.name.data
        if hasattr(team_obj, "name_short") and hasattr(form, "name_short"):
            team_obj.name_short = (form.name_short.data or "").strip()
        if hasattr(team_obj, "visible"):
            team_obj.visible = _posted_visible_int(default=getattr(team_obj, "visible", 0))
        if hasattr(team_obj, "main_league") and hasattr(form, "main_league"):
            team_obj.main_league = form.main_league.data
        if hasattr(team_obj, "score_scrap") and hasattr(form, "score_scrap"):
            team_obj.score_scrap = form.score_scrap.data
        if hasattr(team_obj, "player_list_scrap") and hasattr(form, "player_list_scrap"):
            team_obj.player_list_scrap = form.player_list_scrap.data
        if hasattr(team_obj, "events_results_scrap") and hasattr(form, "events_results_scrap"):
            team_obj.events_results_scrap = form.events_results_scrap.data
        if hasattr(team_obj, "events_program_scrap") and hasattr(form, "events_program_scrap"):
            team_obj.events_program_scrap = form.events_program_scrap.data

        if hasattr(team_obj, "club_id"):
            team_obj.club_id = team_obj.club_id or _cid()

        try:
            db.session.commit()
            flash("A Team has been updated!", "success")
        except SQLAlchemyError:
            db.session.rollback()
            flash("Chyba pri ukladaní údajov tímu.", "danger")

        return redirect(url_for("team.list_teams"))

    if _is_ajax() and request.method == "POST" and what:
        return jsonify({"ok": False, "category": "danger", "message": "Akcia sa nevybavila (nesedí what alebo chýba handler)."}), 400

    return render_template(
        "teams/create_team.html",
        title="Update Team",
        form=form,
        team=team_obj,
        legend="Update Team",
        teamz=RightColumn.main_menu(),
        current_date=datetime.now(),
        next22=Next.next(),
        next_match=RightColumn.next_match(),
        score_table=RightColumn.score_table(),
    )


@team_bp.route("/teams/<int:team_id>/delete", methods=["GET", "POST"])
@csrf.exempt
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
            flash("A Team has been deleted!", "success")
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.exception("DB delete error (Team): %s", e)
            flash("Chyba pri mazaní tímu.", "danger")
    return redirect(url_for("team.list_teams"))


# ------------------------- Lineup API -------------------------
# (fetch z JS bez CSRF tokenu -> preto exempt)

@team_bp.route("/api/team/<int:team_id>/lineup/formation", methods=["POST"])
@csrf.exempt
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


@team_bp.route("/api/team/<int:team_id>/lineup/swap", methods=["POST"])
@csrf.exempt
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


@team_bp.route("/api/team/<int:team_id>/lineup/swap-slots", methods=["POST"])
@csrf.exempt
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
