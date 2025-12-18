from __future__ import annotations

import json
import re
import time
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, List, Optional
from app import csrf

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from urllib.parse import (
    urlparse, parse_qsl, urlencode, urlunparse, quote_plus
)

from flask import (
    Blueprint, render_template, url_for, flash,
    redirect, request, jsonify, current_app, abort
)
from flask_login import login_required, current_user

from app import db
from app.main.routes import RightColumn, Next
from app.team.forms import TeamForm
from app.models import (
    Team, ScoreTable, User, Player, Position, Member, Role,
    Event, EventCategory,
    teams_members,
    TeamLineup, TeamLineupSlot,
)

team = Blueprint("team", __name__)


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


# ------------------------- Sportnet API (events) -------------------------

def _fetch_json(url: str, retries: int = 3, base_timeout: float = 8.0):
    text = _fetch_html(url, retries=retries, base_timeout=base_timeout)
    try:
        return json.loads(text)
    except Exception as e:
        current_app.logger.exception("JSON parse error for %s: %s", url, e)
        return {}


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
    """
    Nájde ID kategórie 'Zápas' (tvoja DB ju má ako 'Zßpas').
    """
    cat = EventCategory.query.filter(EventCategory.name.ilike("Z%pas")).first()
    if cat:
        return int(cat.id)
    return 1


def _event_data_from_api_match(item: dict) -> dict | None:
    """
    Z jedného JSON zápasu z API spraví dict pre Event.

    - address = "Navigácia na štadión"
    - link = Google Maps dir na "Štadión {home_team_name}"
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

        dt_str = start_str.replace("Z", "")
        try:
            start_dt = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            start_dt = datetime.strptime(dt_str.split(".")[0], "%Y-%m-%dT%H:%M:%S")

        end_str = item.get("endDate") or item.get("dateTo") or item.get("date_to")
        if end_str:
            dt_to = end_str.replace("Z", "")
            try:
                end_dt = datetime.strptime(dt_to, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                end_dt = datetime.strptime(dt_to.split(".")[0], "%Y-%m-%dT%H:%M:%S")
        else:
            end_dt = start_dt + timedelta(hours=2)

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
            starters.append({"player": m, "slot": len(starters), "pos": int(getattr(m, "position", 0) or 0)})

    return starters[:11], subs


# ------------------------- Routes -------------------------

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
@roles_required_compat("Admin", "WebAdmin")
def new_team():
    form = TeamForm()
    if form.validate_on_submit():
        team_obj = Team(
            name=form.name.data,
            score_scrap=form.score_scrap.data,
            player_list_scrap=form.player_list_scrap.data,
        )
        # ak máš tieto polia vo Forme/Modeli, doplní sa automaticky cez update,
        # tu to nechávame minimalne, aby to nepuklo.
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

    team_obj = Team.query.filter(Team.name.like(team_name)).first_or_404()

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


@team.route("/teams/<int:team_id>/update", methods=["GET", "POST"])
@csrf.exempt
@login_required
@roles_required_compat("Admin", "WebAdmin")
def update_team(team_id):
    team_obj = Team.query.get_or_404(team_id)
    form = TeamForm(obj=team_obj)
    what = request.form.get("what")

    # ------------------ 1) TABUĽKA (score_scrap) ------------------
    score_scrap = request.form.get("score_scrap")
    if what == "score" and score_scrap:
        ScoreTable.query.filter(ScoreTable.team_id == team_id).delete()
        html = ""
        try:
            html = _fetch_html(score_scrap)

            dom_rows = _parse_score_table_dom(html)
            inserted = 0

            if dom_rows:
                for row in dom_rows:
                    rec = ScoreTable(
                        club=str(row.get("club", "")).strip(),
                        logo=str(row.get("logo", "")).strip(),
                        games=int(row.get("Z", 0)),
                        wins=int(row.get("V", 0)),
                        draws=int(row.get("R", 0)),
                        loses=int(row.get("P", 0)),
                        score=str(row.get("Skóre", "")).strip(),
                        points=int(row.get("B", 0)),
                        team_id=team_id,
                    )
                    db.session.add(rec)
                    inserted += 1

                db.session.commit()
                flash(f"Tabuľka výsledkov aktualizovaná ({inserted} záznamov).", "success")

            else:
                tables = _best_read_html_tables(html)
                if not tables:
                    flash("Na stránke nebola nájdená žiadna tabuľka výsledkov.", "warning")
                    return redirect(url_for("team.update_team", team_id=team_id))

                expected = {
                    "klub": "Klub", "mužstvo": "Klub", "muzstvo": "Klub", "tím": "Klub", "tim": "Klub",
                    "team": "Klub", "club": "Klub", "družstvo": "Klub", "druzstvo": "Klub",
                    "name": "Klub", "názov": "Klub", "nazov": "Klub",
                    "z": "Z", "v": "V", "r": "R", "p": "P",
                    "skóre": "Skóre", "skore": "Skóre", "b": "B",
                }

                inserted = 0
                for raw_df in tables:
                    df = _normalize_columns(raw_df)
                    lower_map = {c.lower(): c for c in df.columns}
                    needed = {}
                    for k, nice in expected.items():
                        if k in lower_map:
                            needed[nice] = lower_map[k]

                    minimal = {"Klub", "Z", "V", "R", "P", "B"}
                    if minimal.issubset(set(needed.keys())):
                        rename_map = {needed[nice]: nice for nice in needed.keys()}
                        work = df.rename(columns=rename_map)
                        order = ["Klub", "Z", "V", "R", "P", "Skóre", "B"]
                        work = work[[c for c in order if c in work.columns]].copy()
                    else:
                        if not minimal.issubset(set(df.columns)):
                            continue
                        use_cols = list(minimal | {"Skóre"})
                        use_cols = [c for c in use_cols if c in df.columns]
                        work = df[use_cols].copy()

                    if "Klub" in work.columns:
                        work["Klub"] = work["Klub"].fillna("").astype(str).str.strip()
                    for col in ("Z", "V", "R", "P", "B"):
                        if col in work.columns:
                            work[col] = _to_int_series(work[col])
                    if "Skóre" in work.columns:
                        work["Skóre"] = work["Skóre"].fillna("").astype(str).str.strip()
                    else:
                        work["Skóre"] = ""

                    work = _fix_club_column(work)

                    for _, row in work.iterrows():
                        rec = ScoreTable(
                            club=str(row.get("Klub", "")).strip(),
                            logo="",
                            games=int(row.get("Z", 0)),
                            wins=int(row.get("V", 0)),
                            draws=int(row.get("R", 0)),
                            loses=int(row.get("P", 0)),
                            score=str(row.get("Skóre", "")).strip(),
                            points=int(row.get("B", 0)),
                            team_id=team_id,
                        )
                        db.session.add(rec)
                        inserted += 1

                db.session.commit()
                flash(f"Tabuľka výsledkov aktualizovaná ({inserted} záznamov).", "success")

        except requests.RequestException as e:
            db.session.rollback()
            current_app.logger.exception("HTTP/Network chyba score_scrap: %s", e)
            flash("Nepodarilo sa načítať tabuľku (sieťová chyba).", "danger")
        except Exception as e:
            db.session.rollback()
            current_app.logger.exception("Chyba pri parsovaní score_scrap: %s", e)
            current_app.logger.debug("HTML preview: %s", _html_preview_for_log(html))
            flash("Nepodarilo sa spracovať tabuľku výsledkov.", "danger")

        return redirect(url_for("team.update_team", team_id=team_id))

    # ------------------ 2) EVENTS z API (events_results_scrap) ------------------
    events_results_scrap = request.form.get("events_results_scrap") or getattr(team_obj, "events_results_scrap", None)

    if what == "events" and events_results_scrap:
        match_cat_id = _get_match_event_category_id()

        Event.query.filter(
            Event.event_team_id == team_id,
            Event.event_category_id == match_cat_id
        ).delete()

        try:
            all_items = _fetch_all_api_items(events_results_scrap)

            seen_keys = set()
            inserted = 0

            for item in all_items:
                data = _event_data_from_api_match(item)
                if not data:
                    continue

                key = (data["match_id"], data["start_dt"])
                if key in seen_keys:
                    continue
                seen_keys.add(key)

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
                db.session.add(ev)
                inserted += 1

            db.session.commit()
            if inserted:
                flash(f"Kalendár zápasov aktualizovaný z API ({inserted} zápasov).", "success")
            else:
                flash("API nenašlo žiadne zápasy.", "warning")

        except requests.RequestException as e:
            db.session.rollback()
            current_app.logger.exception("HTTP/Network chyba events_results_scrap: %s", e)
            flash("Nepodarilo sa načítať zápasy z API (sieťová chyba).", "danger")
        except Exception as e:
            db.session.rollback()
            current_app.logger.exception("Chyba pri spracovaní zápasov z API: %s", e)
            flash("Nepodarilo sa spracovať zápasy z API.", "danger")

        return redirect(url_for("team.update_team", team_id=team_id))

    # ------------------ 3) SAVE META (hlavný submit bez what) ------------------
    if form.validate_on_submit() and not what:
        # nastavujeme len ak tie atribúty existujú (aby to nepuklo, keď máš inú DB schému)
        team_obj.name = form.name.data

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

        try:
            db.session.commit()
            flash("A Team has been updated!", "success")
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.exception("DB commit error (Team meta): %s", e)
            flash("Chyba pri ukladaní údajov tímu.", "danger")

        return redirect(url_for("team.list_teams"))

    # GET: form je už naplnený cez obj=team_obj
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
            flash("A Team has been deleted!", "success")
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.exception("DB delete error (Team): %s", e)
            flash("Chyba pri mazaní tímu.", "danger")
    return redirect(url_for("team.list_teams"))


# ------------------------- Lineup API -------------------------

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
