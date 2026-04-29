from __future__ import annotations

import json
import re
import time
import unicodedata
from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse, quote_plus
from zoneinfo import ZoneInfo

import pandas as pd
import requests
from bs4 import BeautifulSoup
from flask import (
    Blueprint, render_template, url_for, flash,
    redirect, request, jsonify, current_app, abort
)
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

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

BASE_ORIGIN = "https://sportnet.sme.sk"
API_LOCAL_TZ = ZoneInfo("Europe/Bratislava")


# -----------------------------------------------------------------------------
# Request / auth helpers
# -----------------------------------------------------------------------------

def _is_ajax() -> bool:
    xrw = (request.headers.get("X-Requested-With") or "").lower()
    accept = (request.headers.get("Accept") or "").lower()
    return xrw == "xmlhttprequest" or "application/json" in accept


def roles_required_compat(*roles):
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


# -----------------------------------------------------------------------------
# Generic helpers
# -----------------------------------------------------------------------------

def _abs_url(src: str) -> str:
    src = (src or "").strip()
    if not src:
        return ""
    if src.startswith("//"):
        return "https:" + src
    if src.startswith("/"):
        return BASE_ORIGIN + src
    return src


def _fetch_html(url: str, retries: int = 3, base_timeout: float = 10.0) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/119.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/json;q=0.8,*/*;q=0.7",
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
            resp.encoding = "utf-8"
            resp.raise_for_status()
            print(f"********* FETCH OK (attempt {attempt}/{retries}): {resp.url} | len: {len(resp.text or '')}")
            return resp.text or ""
        except requests.RequestException as e:
            last_err = e
            print(f"********* FETCH FAIL (attempt {attempt}/{retries}): {repr(e)}")
            time.sleep(0.7 * (2 ** (attempt - 1)))

    raise requests.ConnectionError(last_err)


def _safe_int_val(v) -> int:
    try:
        s = str(v or "").strip()
        if not s or ":" in s:
            return 0
        return int(float(s))
    except Exception:
        return 0


def _strip_accents(s: str) -> str:
    s = (s or "").strip().lower()
    s = unicodedata.normalize("NFKD", s)
    return "".join(ch for ch in s if not unicodedata.combining(ch))


def _name_key(name: str) -> str:
    return _strip_accents(re.sub(r"\s+", " ", (name or "").strip()))


# -----------------------------------------------------------------------------
# Score table parsing
# -----------------------------------------------------------------------------

def _parse_score_table_dom(html: str) -> List[Dict]:
    soup = BeautifulSoup(html or "", "lxml")
    rows: List[Dict] = []

    for tbody in soup.find_all("tbody"):
        for tr in tbody.find_all("tr"):
            tds = tr.find_all("td")
            if len(tds) < 2:
                continue

            logo_url = ""
            club_from_img = ""
            img = tr.find("img")
            if img:
                logo_url = _abs_url(img.get("src", ""))
                club_from_img = (img.get("alt", "") or "").strip()

            club_from_link = ""
            a = tds[1].find("a") if len(tds) > 1 else None
            if a:
                club_from_link = a.get_text(strip=True)

            club = club_from_link or club_from_img or tds[1].get_text(strip=True)

            def _td_text(i: int) -> str:
                return tds[i].get_text(strip=True) if i < len(tds) else ""

            rows.append({
                "club": club,
                "logo": logo_url,
                "Z": _safe_int_val(_td_text(2)),
                "V": _safe_int_val(_td_text(3)),
                "R": _safe_int_val(_td_text(4)),
                "P": _safe_int_val(_td_text(5)),
                "Skóre": _td_text(6),
                "B": _safe_int_val(_td_text(7)),
            })

    print(f"********* SCORE DOM: total parsed rows={len(rows)}")
    return rows


# -----------------------------------------------------------------------------
# Players parsing: ONLY players, no coaches / staff
# -----------------------------------------------------------------------------

def _normalize_player_name(name: str) -> str:
    return re.sub(r"\s+", " ", (name or "")).strip()


def _best_read_html_tables(html: str) -> List[pd.DataFrame]:
    flavors_to_try = [
        ["lxml"], ["bs4"], ["html5lib"],
        ["lxml", "bs4"], ["lxml", "html5lib"], ["bs4", "html5lib"],
        ["lxml", "bs4", "html5lib"],
    ]
    last_exc: Optional[Exception] = None
    for flavors in flavors_to_try:
        try:
            return pd.read_html(html, flavor=flavors, match=r".+")
        except Exception as e:
            last_exc = e
            print(f"********* read_html FAIL - flavors: {flavors} | error: {repr(e)}")
    print(f"********* read_html ALL FAIL -> returning [] | last={repr(last_exc)}")
    return []


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(-1)
    df.columns = [str(c).strip() for c in df.columns]
    return df


def _find_player_name_col(df: pd.DataFrame) -> str:
    cols = [str(c).strip() for c in df.columns]
    low = {c.lower(): c for c in cols}
    for k in ("hráč", "hrac", "meno", "name", "player"):
        if k in low:
            return low[k]
    return cols[0]


def _parse_players_from_html(html: str) -> List[Dict]:
    try:
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
            key = _name_key(name)
            if key in seen:
                continue
            seen.add(key)
            out.append({
                "name": name,
                "position": _safe_int_val(row.get(pos_col)) if pos_col else 0,
                "score": _safe_int_val(row.get(goals_col)) if goals_col else 0,
                "yellow_card": _safe_int_val(row.get(yellow_col)) if yellow_col else 0,
                "red_card": _safe_int_val(row.get(red_col)) if red_col else 0,
                "photo_url": "",
            })
        return out
    except Exception as e:
        print("********* _parse_players_from_html FAILED:", repr(e))
        return []


def _parse_players_from_dom(html: str) -> List[Dict]:
    """Parse Sportnet /hraci page. ONLY real playing positions are accepted."""
    soup = BeautifulSoup(html or "", "lxml")

    # Len hráčske sekcie. Žiadny tréner, lekár, fyzio, technický vedúci.
    HEADINGS = [
        (re.compile(r"^\s*brank[aá]ri\s*$", re.I), 1),
        (re.compile(r"^\s*obrancovia\s*$", re.I), 2),
        (re.compile(r"^\s*z[aá]lo[zž]n[ií]ci\s*$", re.I), 3),
        (re.compile(r"^\s*[uú]to[cč]n[ií]ci\s*$", re.I), 4),
    ]
    
    STOP_HEADINGS = [
        re.compile(r"^\s*tr[eé]ner\s*$", re.I),
        re.compile(r"^\s*realiza[cč]n[yý]\s+t[ií]m\s*$", re.I),
        re.compile(r"^\s*technick[yý]\s+ved[uú]ci\s*$", re.I),
        re.compile(r"^\s*lek[aá]r\s*$", re.I),
        re.compile(r"^\s*fyzioterapeut\s*$", re.I),
        re.compile(r"^\s*mas[eé]r\s*$", re.I),
    ]

    BAD_NAME_RX = re.compile(
        r"(tréner|trener|asistent|technick[yý]\s+ved[uú]ci|lek[aá]r|fyzioterapeut|"
        r"sledujte\s+n[aá]s|copyright|inzercia|ochrana\s+osobn|nariadenie\s+dsa|"
        r"sportnet\.sk|futbalnet\.sk|©|\|)",
        re.I,
    )

    def match_pos(text: str) -> int:
        t = (text or "").strip()
        for rx, pos in HEADINGS:
            if rx.match(t):
                return pos
        return 0
    
    def is_stop_heading(text: str) -> bool:
        t = (text or "").strip()
        return any(rx.match(t) for rx in STOP_HEADINGS)

    def is_player_link(a) -> bool:
        href = (a.get("href") or "").strip()
        return href.startswith("/futbalnet/clen/")

    def looks_like_real_name(name: str) -> bool:
        name = _normalize_player_name(name)
        if not name or len(name) < 3 or len(name) > 80:
            return False
        if BAD_NAME_RX.search(name):
            return False
        if len(name.split()) > 4:
            return False
        if not re.search(r"[A-Za-zÁ-ž]", name):
            return False
        return True

    out: List[Dict] = []
    seen = set()
    heading_nodes = []

    for node in soup.find_all(string=True):
        pos = match_pos(str(node))
        if pos:
            heading_nodes.append((node, pos))

    if not heading_nodes:
        # Fallback bez pozícií: len profily členov, ale stále bez staff slov.
        for a in soup.find_all("a", href=True):
            if not is_player_link(a):
                continue
            name = _normalize_player_name(a.get_text(" ", strip=True))
            if not looks_like_real_name(name):
                continue
            k = _name_key(name)
            if k in seen:
                continue
            seen.add(k)
            out.append({"name": name, "position": 0, "score": 0, "yellow_card": 0, "red_card": 0, "photo_url": ""})
        return out

    for idx, (node, pos) in enumerate(heading_nodes):
        if pos not in (1, 2, 3, 4):
            continue    
        start_el = node.parent
        end_el = heading_nodes[idx + 1][0].parent if idx + 1 < len(heading_nodes) else None

        for el in start_el.next_elements:
            if end_el is not None and el is end_el:
                break

            if isinstance(el, str) and is_stop_heading(str(el)):
                break
            if not hasattr(el, "name"):
                continue
            if el.name == "a" and el.has_attr("href") and is_player_link(el):
                name = _normalize_player_name(el.get_text(" ", strip=True))
                if not looks_like_real_name(name):
                    continue
                k = _name_key(name)
                if k in seen:
                    continue
                seen.add(k)
                out.append({"name": name, "position": int(pos), "score": 0, "yellow_card": 0, "red_card": 0, "photo_url": ""})

    return out


def _parse_players_from_json_payload(payload: Any) -> List[Dict]:
    try:
        data = payload
        if isinstance(data, dict):
            for k in ("players", "items", "data", "results", "squad", "teamPlayers"):
                if isinstance(data.get(k), list):
                    data = data[k]
                    break
        if not isinstance(data, list):
            return []

        out: List[Dict] = []
        seen = set()
        for it in data:
            if not isinstance(it, dict):
                continue
            name = it.get("name") or it.get("fullName") or it.get("playerName") or it.get("title") or ""
            name = _normalize_player_name(str(name))
            if not name:
                continue
            key = _name_key(name)
            if key in seen:
                continue
            seen.add(key)
            out.append({
                "name": name,
                "position": _safe_int_val(it.get("position") or it.get("pos") or 0),
                "score": _safe_int_val(it.get("goals") or it.get("score") or it.get("g") or 0),
                "yellow_card": _safe_int_val(it.get("yellow") or it.get("yellow_card") or it.get("zk") or 0),
                "red_card": _safe_int_val(it.get("red") or it.get("red_card") or it.get("ck") or 0),
                "photo_url": _abs_url(str(it.get("photo_url") or it.get("photoUrl") or it.get("image") or "")),
            })
        return out
    except Exception as e:
        print("********* _parse_players_from_json_payload FAILED:", repr(e))
        return []


def _parse_player_stats_from_dom(html: str) -> dict[str, dict]:
    """Parse Sportnet /statistika-hracov for photos and numbers."""
    soup = BeautifulSoup(html or "", "lxml")
    stats: dict[str, dict] = {}

    def is_player_link(a) -> bool:
        href = (a.get("href") or "").strip()
        return href.startswith("/futbalnet/clen/")

    def find_photo(a) -> str:
        for parent in list(a.parents)[:6]:
            img = parent.find("img") if parent else None
            if img:
                src = (img.get("src") or img.get("data-src") or img.get("data-lazy-src") or "").strip()
                if src:
                    return _abs_url(src)
        img = a.find_previous("img")
        if img:
            src = (img.get("src") or img.get("data-src") or img.get("data-lazy-src") or "").strip()
            if src:
                return _abs_url(src)
        return ""

    for a in soup.find_all("a", href=True):
        if not is_player_link(a):
            continue
        name = _normalize_player_name(a.get_text(" ", strip=True))
        if not name or len(name) > 80 or len(name.split()) > 4:
            continue

        container_text = ""
        for parent in list(a.parents)[:5]:
            try:
                txt = parent.get_text(" ", strip=True)
                if len(txt) > len(container_text):
                    container_text = txt
            except Exception:
                pass
        nums = [int(x) for x in re.findall(r"\b\d+\b", container_text)[:6]]
        key = _name_key(name)

        stats[key] = {
            "score": nums[0] if len(nums) > 0 else 0,
            "yellow_card": nums[1] if len(nums) > 1 else 0,
            "red_card": nums[2] if len(nums) > 2 else 0,
            "photo_url": find_photo(a),
        }

    return stats


def _players_sort_key(p: Player):
    pos = int(getattr(p, "position", 0) or 0)
    return (99 if pos == 0 else pos, getattr(p, "name", "") or "")


# -----------------------------------------------------------------------------
# Sportnet events API
# -----------------------------------------------------------------------------

def _fetch_all_api_items(base_url: str) -> list[dict]:
    parsed = urlparse(base_url)
    qs = dict(parse_qsl(parsed.query, keep_blank_values=True))
    qs.setdefault("limit", "100")
    qs.setdefault("offset", "0")
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
    return int(cat.id) if cat else 1


def _parse_api_datetime_local(start_str: str) -> datetime:
    if not start_str:
        raise ValueError("empty datetime string")
    s = start_str.strip()
    if s.endswith("Z"):
        s2 = s[:-1].split(".")[0]
        dt = datetime.strptime(s2, "%Y-%m-%dT%H:%M:%S")
        return dt.replace(tzinfo=timezone.utc).astimezone(API_LOCAL_TZ)
    try:
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=API_LOCAL_TZ)
        return dt.astimezone(API_LOCAL_TZ)
    except Exception:
        dt = datetime.strptime(s.split(".")[0], "%Y-%m-%dT%H:%M:%S")
        return dt.replace(tzinfo=API_LOCAL_TZ)


def _event_data_from_api_match(item: dict) -> dict | None:
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
        has_scores = state == "ODOHRATY" and isinstance(home_score, (int, float)) and isinstance(away_score, (int, float))
        title = f"{home_name} {int(home_score)}:{int(away_score)} {away_name}" if has_scores else f"{home_name} - {away_name}"

        start_str = item.get("startDate") or item.get("dateFrom") or item.get("date_from")
        if not start_str:
            return None
        start_local = _parse_api_datetime_local(start_str)

        end_str = item.get("endDate") or item.get("dateTo") or item.get("date_to")
        end_local = _parse_api_datetime_local(end_str) if end_str else start_local + timedelta(hours=2)

        start_dt = start_local.astimezone(timezone.utc)
        end_dt = end_local.astimezone(timezone.utc)
        gm_url = "https://www.google.com/maps/dir/?api=1&destination=" + quote_plus(f"Štadión {home_name}")

        return {
            "match_id": match_id,
            "title": title.strip(),
            "start_dt": start_dt,
            "end_dt": end_dt,
            "address": "Navigácia na štadión",
            "link": gm_url,
        }
    except Exception as e:
        print("********* API ITEM PARSE ERROR:", e)
        return None


# -----------------------------------------------------------------------------
# Lineup helpers
# -----------------------------------------------------------------------------

def _ensure_lineup(team_id: int, ordered_players: list[Player]) -> TeamLineup:
    """
    Create / repair lineup slots. Does NOT reset slots on every page load.
    That is critical, otherwise manual swaps are lost and swap endpoints fail.
    """
    lineup = TeamLineup.query.filter_by(team_id=team_id).first()
    if not lineup:
        lineup = TeamLineup(team_id=team_id, formation="4-3-3")
        db.session.add(lineup)
        db.session.flush()

    slots_q = TeamLineupSlot.query.filter_by(lineup_id=lineup.id)
    slots = slots_q.all()
    current_ids = {int(p.id) for p in ordered_players if p.id is not None}
    slot_ids = {int(s.player_id) for s in slots if s.player_id is not None}

    if not slots or slot_ids != current_ids:
        slots_q.delete(synchronize_session=False)
        db.session.flush()
        for i, p in enumerate(ordered_players):
            db.session.add(TeamLineupSlot(
                lineup_id=lineup.id,
                player_id=p.id,
                is_starter=(i < 11),
                order_index=(i if i < 11 else i - 11),
                position=int(getattr(p, "position", 0) or 0),
            ))
        db.session.flush()

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

    return starters[:11], subs


# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------

@team_bp.route("/info")
def team_youth():
    return render_template(
        "teams/youth.html",
        current_date=datetime.now(timezone.utc),
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
        current_date=datetime.now(timezone.utc),
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
            name=(form.name.data or "").strip(),
            name_short=(form.name_short.data or "").strip(),
            visible=int(form.visible.data) if hasattr(form, "visible") else 1,
            main_league=(form.main_league.data or "").strip(),
            score_scrap=(form.score_scrap.data or "").strip(),
            player_list_scrap=(form.player_list_scrap.data or "").strip(),
            events_results_scrap=(form.events_results_scrap.data or "").strip(),
            events_program_scrap=(form.events_program_scrap.data or "").strip(),
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
    team_obj = Team.query.filter(Team.name.like(team_name)).first_or_404()
    can_edit = team_obj.can_edit_lineup(current_user)

    members = (
        Player.query
        .filter(Player.team_id == team_obj.id)
        .order_by(Player.position.asc(), Player.name.asc())
        .all()
    )
    ordered_players = sorted(members, key=_players_sort_key)

    lineup = _ensure_lineup(team_obj.id, ordered_players)
    starters, subs = _load_starters_subs_with_slots(lineup, ordered_players)

    return render_template(
        "teams/team.html",
        team=team_obj,
        starters=starters,
        subs=subs,
        formation=(lineup.formation or "4-3-3"),
        trener=[],
        teamz=RightColumn.main_menu(),
        current_date=datetime.now(timezone.utc),
        next22=Next.next(),
        next_match=RightColumn.next_match(),
        score_table=RightColumn.score_table(),
        can_edit_lineup=can_edit,
        coaches=[],
        coach_cards=[],
    )


@team_bp.route("/teams/<int:team_id>/update", methods=["GET", "POST"])
@csrf.exempt
@login_required
@roles_required_compat("Admin", "WebAdmin")
def update_team(team_id):
    current_app.logger.warning("UPDATE_TEAM START team_id=%s", team_id)
    current_app.logger.warning("FORM=%s", dict(request.form))
    current_app.logger.warning("WHAT=%s", request.form.get("what"))

    team_obj = Team.query.get_or_404(team_id)
    form = TeamForm(obj=team_obj)
    what = (request.form.get("what") or "").strip().lower() or None

    if request.method == "GET":
        return render_template(
            "teams/create_team.html",
            title="Update Team",
            form=form,
            team=team_obj,
            legend="Update Team",
            teamz=RightColumn.main_menu(),
            current_date=datetime.now(timezone.utc),
            next22=Next.next(),
            next_match=RightColumn.next_match(),
            score_table=RightColumn.score_table(),
        )

    if what == "score":
        score_scrap = (request.form.get("score_scrap") or getattr(team_obj, "score_scrap", None) or "").strip()
        if not score_scrap:
            flash("Table of Ligue: link je prázdny.", "warning")
            return redirect(url_for("team.update_team", team_id=team_id))
        try:
            html = _fetch_html(score_scrap)
            dom_rows = _parse_score_table_dom(html)
            ScoreTable.query.filter(ScoreTable.team_id == team_id).delete(synchronize_session=False)
            inserted = 0
            for row in dom_rows:
                db.session.add(ScoreTable(
                    club=str(row.get("club", "")).strip(),
                    logo=str(row.get("logo", "")).strip(),
                    games=int(row.get("Z", 0) or 0),
                    wins=int(row.get("V", 0) or 0),
                    draws=int(row.get("R", 0) or 0),
                    loses=int(row.get("P", 0) or 0),
                    score=str(row.get("Skóre", "")).strip(),
                    points=int(row.get("B", 0) or 0),
                    team_id=team_id,
                ))
                inserted += 1
            db.session.commit()
            flash(f"Table of Ligue: úspešne aktualizované ({inserted} záznamov).", "success")
            return redirect(url_for("team.update_team", team_id=team_id))
        except Exception as e:
            db.session.rollback()
            current_app.logger.exception("SCORE UPDATE FAILED: %s", e)
            flash("Table of Ligue: nepodarilo sa spracovať tabuľku.", "danger")
            return redirect(url_for("team.update_team", team_id=team_id))

    if what == "players":
        player_list_scrap = (request.form.get("player_list_scrap") or getattr(team_obj, "player_list_scrap", None) or "").strip()
        if not player_list_scrap:
            msg = "Players LineUp: link je prázdny."
            if _is_ajax():
                return jsonify({"ok": False, "category": "warning", "message": msg}), 400
            flash(msg, "warning")
            return redirect(url_for("team.update_team", team_id=team_id))

        try:
            html = _fetch_html(player_list_scrap)
            players: List[Dict] = []

            if html.lstrip().startswith("{") or html.lstrip().startswith("["):
                try:
                    players = _parse_players_from_json_payload(json.loads(html))
                    current_app.logger.warning("PLAYERS: JSON parsed=%s", len(players))
                except Exception:
                    current_app.logger.exception("PLAYERS: JSON parse failed")

            if not players:
                players = _parse_players_from_dom(html)
                current_app.logger.warning("PLAYERS: DOM parsed=%s", len(players))

            if not players:
                players = _parse_players_from_html(html)
                current_app.logger.warning("PLAYERS: TABLE parsed=%s", len(players))

            stats_map = {}
            try:
                stats_url = re.sub(r"/hraci/?($|\?)", r"/statistika-hracov/\1", player_list_scrap)
                stats_html = _fetch_html(stats_url)
                stats_map = _parse_player_stats_from_dom(stats_html)
                current_app.logger.warning("PLAYERS PHOTOS/STATS: parsed=%s from=%s", len(stats_map), stats_url)
            except Exception:
                current_app.logger.exception("PLAYERS PHOTOS/STATS: fetch/parse failed")

            if not players:
                msg = "Players LineUp: nenašiel som žiadnych hráčov na stránke."
                if _is_ajax():
                    return jsonify({"ok": False, "category": "warning", "message": msg}), 400
                flash(msg, "warning")
                return redirect(url_for("team.update_team", team_id=team_id))

            cleaned: List[Dict] = []
            seen = set()
            for p in players:
                name = _normalize_player_name(str((p or {}).get("name", "")))
                if not name:
                    continue
                pos = int((p or {}).get("position", 0) or 0)
                if pos >= 100:
                    continue
                key = _name_key(name)
                if key in seen:
                    continue
                seen.add(key)
                st = stats_map.get(key, {})
                cleaned.append({
                    "name": name[:250],
                    "position": pos,
                    "score": int(st.get("score", (p or {}).get("score", 0) or 0)),
                    "yellow_card": int(st.get("yellow_card", (p or {}).get("yellow_card", 0) or 0)),
                    "red_card": int(st.get("red_card", (p or {}).get("red_card", 0) or 0)),
                    "photo_url": str(st.get("photo_url", (p or {}).get("photo_url", "") or "")).strip()[:250],
                })

            players = cleaned
            current_app.logger.warning("PLAYERS: cleaned real players=%s", len(players))

            if not players:
                msg = "Players LineUp: po odfiltrovaní realizačného tímu nezostal žiadny hráč."
                if _is_ajax():
                    return jsonify({"ok": False, "category": "warning", "message": msg}), 400
                flash(msg, "warning")
                return redirect(url_for("team.update_team", team_id=team_id))

            lineup = TeamLineup.query.filter_by(team_id=team_id).first()
            if lineup:
                TeamLineupSlot.query.filter_by(lineup_id=lineup.id).delete(synchronize_session=False)
                db.session.flush()

            Player.query.filter(Player.team_id == team_id).delete(synchronize_session=False)
            db.session.flush()

            inserted = 0
            for p in players:
                player_obj = Player(
                    name=p["name"],
                    position=int(p.get("position", 0) or 0),
                    team=team_obj.name,
                    score=int(p.get("score", 0) or 0),
                    yellow_card=int(p.get("yellow_card", 0) or 0),
                    red_card=int(p.get("red_card", 0) or 0),
                    team_id=team_id,
                )
                if hasattr(player_obj, "photo_url"):
                    player_obj.photo_url = str(p.get("photo_url", "") or "")[:250]
                db.session.add(player_obj)
                inserted += 1

            db.session.flush()
            ordered_players = sorted(Player.query.filter_by(team_id=team_id).all(), key=_players_sort_key)
            _ensure_lineup(team_id, ordered_players)
            db.session.commit()

            msg = f"Players LineUp: úspešne aktualizované ({inserted} hráčov)."
            if _is_ajax():
                return jsonify({"ok": True, "category": "success", "message": msg})
            flash(msg, "success")
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
            msg = "Players LineUp: nepodarilo sa spracovať hráčov (parse chyba)."
            if _is_ajax():
                return jsonify({"ok": False, "category": "danger", "message": msg}), 400
            flash(msg, "danger")
            return redirect(url_for("team.update_team", team_id=team_id))

    if what == "events":
        events_results_scrap = (request.form.get("events_results_scrap") or getattr(team_obj, "events_results_scrap", None) or "").strip()
        if not events_results_scrap:
            msg = "Matches results: link je prázdny."
            if _is_ajax():
                return jsonify({"ok": False, "category": "warning", "message": msg}), 400
            flash(msg, "warning")
            return redirect(url_for("team.update_team", team_id=team_id))

        try:
            match_cat_id = _get_match_event_category_id()
            Event.query.filter(Event.event_team_id == team_id, Event.event_category_id == match_cat_id).delete(synchronize_session=False)
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
                db.session.add(Event(
                    title=data["title"],
                    start_event=data["start_dt"],
                    end_event=data["end_dt"],
                    address=data["address"],
                    link=data["link"],
                    user_id=current_user.id,
                    event_category_id=match_cat_id,
                    event_team_id=team_id,
                ))
                inserted += 1
            db.session.commit()
            msg = f"Matches results: úspešne aktualizované ({inserted} zápasov)." if inserted else "Matches results: API nenašlo žiadne zápasy."
            if _is_ajax():
                return jsonify({"ok": bool(inserted), "category": "success" if inserted else "warning", "message": msg}), 200 if inserted else 400
            flash(msg, "success" if inserted else "warning")
            return redirect(url_for("team.update_team", team_id=team_id))
        except requests.RequestException:
            db.session.rollback()
            msg = "Matches results: nepodarilo sa načítať API (sieťová chyba)."
            if _is_ajax():
                return jsonify({"ok": False, "category": "danger", "message": msg}), 400
            flash(msg, "danger")
            return redirect(url_for("team.update_team", team_id=team_id))
        except Exception:
            db.session.rollback()
            current_app.logger.exception("EVENTS: Unexpected error")
            msg = "Matches results: nepodarilo sa spracovať zápasy (parse chyba)."
            if _is_ajax():
                return jsonify({"ok": False, "category": "danger", "message": msg}), 400
            flash(msg, "danger")
            return redirect(url_for("team.update_team", team_id=team_id))

    if form.validate_on_submit() and not what:
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
        except SQLAlchemyError:
            db.session.rollback()
            flash("Chyba pri ukladaní údajov tímu.", "danger")
        return redirect(url_for("team.list_teams"))

    return render_template(
        "teams/create_team.html",
        title="Update Team",
        form=form,
        team=team_obj,
        legend="Update Team",
        teamz=RightColumn.main_menu(),
        current_date=datetime.now(timezone.utc),
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


# -----------------------------------------------------------------------------
# Lineup API
# -----------------------------------------------------------------------------

@team_bp.route("/api/team/<int:team_id>/lineup/formation", methods=["POST"])
@csrf.exempt
def save_formation(team_id):
    data = request.get_json(force=True) or {}
    formation = data.get("formation", "4-3-3")

    ordered_players = sorted(Player.query.filter_by(team_id=team_id).all(), key=_players_sort_key)
    lineup = _ensure_lineup(team_id, ordered_players)
    lineup.formation = formation
    db.session.commit()
    return jsonify({"ok": True, "formation": lineup.formation})


@team_bp.route("/api/team/<int:team_id>/lineup/swap", methods=["POST"])
@csrf.exempt
def swap_players(team_id):
    data = request.get_json(force=True) or {}
    sub_id = int(data.get("sub_id", 0) or 0)
    starter_id = int(data.get("starter_id", 0) or 0)

    ordered_players = sorted(Player.query.filter_by(team_id=team_id).all(), key=_players_sort_key)
    lineup = _ensure_lineup(team_id, ordered_players)

    sub_slot = TeamLineupSlot.query.filter_by(lineup_id=lineup.id, player_id=sub_id).first()
    st_slot = TeamLineupSlot.query.filter_by(lineup_id=lineup.id, player_id=starter_id).first()

    if not sub_slot or not st_slot:
        current_app.logger.warning(
            "LINEUP SWAP missing slots team_id=%s lineup_id=%s sub_id=%s starter_id=%s sub_slot=%s st_slot=%s",
            team_id, lineup.id, sub_id, starter_id, bool(sub_slot), bool(st_slot)
        )
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
    data = request.get_json(force=True) or {}
    a_id = int(data.get("a_id", 0) or 0)
    b_id = int(data.get("b_id", 0) or 0)

    ordered_players = sorted(Player.query.filter_by(team_id=team_id).all(), key=_players_sort_key)
    lineup = _ensure_lineup(team_id, ordered_players)

    a = TeamLineupSlot.query.filter_by(lineup_id=lineup.id, player_id=a_id, is_starter=True).first()
    b = TeamLineupSlot.query.filter_by(lineup_id=lineup.id, player_id=b_id, is_starter=True).first()
    if not a or not b:
        current_app.logger.warning(
            "LINEUP SLOT SWAP missing starters team_id=%s lineup_id=%s a_id=%s b_id=%s a=%s b=%s",
            team_id, lineup.id, a_id, b_id, bool(a), bool(b)
        )
        return jsonify({"ok": False, "error": "Both must be starters"}), 400

    a.order_index, b.order_index = b.order_index, a.order_index
    db.session.commit()
    return jsonify({"ok": True})
