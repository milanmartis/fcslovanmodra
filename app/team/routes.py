# app/team/routes.py
from datetime import timedelta, datetime
from app.main.routes import RightColumn, Next
from sqlalchemy.orm import joinedload
import re
import requests
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse, quote_plus
from datetime import datetime, timedelta
import json
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

API_MATCH_DETAIL_BASE = "https://sportnet.sme.sk/futbalnet/z/bfz/zapas"

from urllib.parse import quote_plus

from flask import (
    render_template, url_for, flash,
    redirect, request, Blueprint, current_app
)


from app.models import (
    Team, ScoreTable, User, Player, Position, Member, Role,
    Post, PostGallery, Category, EventCategory, teams_members, positions_members,
    Event, EventCategory
)



# from flask_login import login_required, current_user
from app.team.forms import TeamForm

from app import db
# from flask_security import roles_required
from app.main.routes import RightColumn

import pandas as pd
import numpy as np
import requests
import time
import re
from typing import List, Optional, Dict, Tuple
from bs4 import BeautifulSoup
from sqlalchemy.exc import SQLAlchemyError
from flask_login import login_user, current_user, logout_user, login_required
from functools import wraps
from flask import abort
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
team = Blueprint('team', __name__)

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
    """Stiahne HTML s redirectom (rieši 308/301/302), s krátkym retry/backoffom."""
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
            resp = requests.get(
                url, headers=headers, timeout=base_timeout, allow_redirects=True
            )
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


def _extract_match_links_from_team_page(html: str) -> List[str]:
    """
    Z tímovej stránky /vysledky alebo /program vytiahne všetky linky na zápasy.
    """
    soup = BeautifulSoup(html, "lxml")
    links: List[str] = []

    for a in soup.find_all("a", href=True):
        href = a["href"] or ""
        # zápasy majú pattern .../futbalnet/z/.../zapas/<id>/
        if "/futbalnet/z/" in href and "/zapas/" in href:
            links.append(_abs_url(href.strip()))

    # deduplikácia pri zachovaní poradia
    seen = set()
    out: List[str] = []
    for l in links:
        if l in seen:
            continue
        seen.add(l)
        out.append(l)

    print(f"********* MATCH LINKS FOUND: {len(out)}")
    for l in out:
        print("   -", l)
    return out








def _fetch_json(url: str, retries: int = 3, base_timeout: float = 8.0):
    """Stiahne JSON (používa _fetch_html) a vráti dict/list."""
    text = _fetch_html(url, retries=retries, base_timeout=base_timeout)
    try:
        return json.loads(text)
    except Exception as e:
        current_app.logger.exception("JSON parse error for %s: %s", url, e)
        return {}

def _build_api_url_with_paging(base_url: str, offset: int = 0, limit: int = 100) -> str:
    """
    Základný API link doplníme / prepíšeme offset & limit tak,
    aby sme vždy dostali všetky zápasy (30 ich je, limit 100 stačí).
    """
    parsed = urlparse(base_url)
    qs = dict(parse_qsl(parsed.query, keep_blank_values=True))
    qs["offset"] = str(offset)
    qs["limit"] = str(limit)
    new_query = urlencode(qs, doseq=True)
    return urlunparse(parsed._replace(query=new_query))

def _fetch_all_api_matches(base_url: str):
    """
    Zavolá Sportnet API a vráti list všetkých zápasov (pole 'matches').
    """
    url = _build_api_url_with_paging(base_url, offset=0, limit=100)
    data = _fetch_json(url)

    if isinstance(data, dict) and isinstance(data.get("matches"), list):
        matches = data["matches"]
        current_app.logger.info("API matches fetched: %s", len(matches))
        return matches

    if isinstance(data, list):
        current_app.logger.info("API matches fetched (list root): %s", len(data))
        return data

    current_app.logger.warning("API matches: unexpected structure for %s -> %r", url, type(data))
    return []

from datetime import datetime, timedelta
from urllib.parse import quote_plus

def _event_data_from_api_match(item: dict) -> dict | None:
    """
    Z jedného JSON zápasu z API spraví dict pre Event.

    Očakávaná štruktúra (typicky je takto, mierne odchýlky prežijeme):
    {
      "_id": "686e8d4135a9a4cf021ccf76",
      "startDate": "2026-04-25T15:00:00Z",
      "endDate": "2026-04-25T17:00:00Z",      # môže chýbať
      "matchState": "ODOHRATY" / "NAPLANOVANY",
      "homeTeam": {"name": "FC Slovan Modra", "score": 2},
      "awayTeam": {"name": "PŠC Pezinok", "score": 1},
      "competition": {"name": "Majstrovstvá regiónu - IV. liga BFZ"},
      "round": {"name": "22"},
      "venue": {"name": "Štadión FC Slovan Modra", "address": "Kalinčiakova, 900 01 Modra"}
    }
    """
    try:
        match_id = item.get("_id") or item.get("id") or item.get("matchId")
        if not match_id:
            return None

        # tímy
        home = item.get("homeTeam") or {}
        away = item.get("awayTeam") or {}

        home_name = (home.get("name") or "").strip()
        away_name = (away.get("name") or "").strip()

        if not home_name or not away_name:
            return None

        # stav zápasu + prípadné skóre
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
            # pre program a istotu – bez výsledku
            title = f"{home_name} - {away_name}"

        # dátum/čas
        start_str = item.get("startDate") or item.get("dateFrom") or item.get("date_from")
        if not start_str:
            return None

        # ISO '2026-04-25T15:00:00Z' / '...000Z' → odsekneme 'Z' a prípadné mikrosekundy
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

        # compétition (liga + kolo) – len fallback, ak by nebol štadión
        comp = item.get("competition") or {}
        rnd = item.get("round") or {}
        comp_name = (comp.get("name") or "").strip()
        rnd_name = (rnd.get("name") or "").strip()
        league_round = comp_name
        if rnd_name:
            league_round = f"{comp_name} {rnd_name}. kolo".strip()

        # STADION / ADRESA → z API, nie z HTML
        venue = item.get("venue") or {}
        stadium_name = (venue.get("name") or "").strip()
        venue_addr = (venue.get("address") or "").strip()

        # podľa zadania: Event.address = názov štadióna
        # ak by nebol, fallback na adresu a potom na league_round
        if stadium_name:
            event_address = stadium_name
        elif venue_addr:
            event_address = venue_addr
        elif league_round:
            event_address = league_round
        else:
            event_address = "Neznámy štadión"

        # Google Maps URL z event_address
        gm_url = f"https://www.google.com/maps/dir/?api=1&destination={quote_plus(event_address)}"

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









def _normalize_match_url(url: str) -> str:
    """Odstráni query string a trailing slash, aby sme vedeli deduplikovať URL."""
    if not url:
        return ""
    base = url.split("?", 1)[0]
    return base.rstrip("/")

def _extract_match_links_from_team_page(html: str) -> List[str]:
    """
    Z jednej stránky tímu (vysledky/program) vytiahne linky na zápasy:
    /futbalnet/z/.../zapas/<ID>/
    """
    soup = BeautifulSoup(html, "lxml")
    links: List[str] = []

    for a in soup.find_all("a", href=True):
        href = a.get("href") or ""
        if "/zapas/" not in href:
            continue
        full = _abs_url(href)
        if full not in links:
            links.append(full)

    print("********* MATCH LINKS EXTRACTED:", len(links))
    return links



def _parse_match_detail(html: str) -> Optional[Dict]:
    """
    Z detailu zápasu vytiahne:
      - home, away
      - start_dt, end_dt
      - score_text (napr. '2:1', prázdne pre program)
      - competition (text zo <title> - liga + kolo)
      - stadium_name (napr. 'Štadión FC Slovan Modra')

    POZOR: presná ulica typu 'Kalinčiakova, 900 01 Modra' v HTML z requests
    spravidla NIE JE, takže ako adresu používame názov štadióna.
    """
    soup = BeautifulSoup(html, "lxml")
    full_text = soup.get_text(" ", strip=True)

    # --- tímy (2 prvé reálne kluby z /futbalnet/k/...) ---
    teams: List[str] = []
    SKIP_TEAM_LABELS = {
        "kluby", "klub",
        "súťaže", "sutaze",
        "zápasy", "zapasy",
        "tabuľky", "tabulky",
        "program", "výsledky", "vysledky"
    }

    for a in soup.find_all("a", href=True):
        href = a.get("href") or ""
        if "/futbalnet/k/" not in href:
            continue

        name = a.get_text(strip=True)
        if not name or len(name) < 2:
            continue

        if name.strip().lower() in SKIP_TEAM_LABELS:
            continue

        if name not in teams:
            teams.append(name)

        if len(teams) >= 2:
            break

    if len(teams) < 2:
        print("********* MATCH DETAIL: neviem nájsť 2 tímy, našiel som:", teams)
        return None

    home, away = teams[0], teams[1]
    title = f"{home} - {away}"

    # --- dátum + čas: '15.11.2025, 13:30' ---
    m = re.search(r"(\d{1,2}\.\d{1,2}\.\d{4}),\s*(\d{1,2}:\d{2})", full_text)
    if not m:
        print("********* MATCH DETAIL: nenašiel som dátum/čas")
        return None

    dt_str = f"{m.group(1)}, {m.group(2)}"
    try:
        start_dt = datetime.strptime(dt_str, "%d.%m.%Y, %H:%M")
    except ValueError as e:
        print("********* MATCH DETAIL: datetime parse error", e)
        return None

    end_dt = start_dt + timedelta(hours=2)

    # --- skóre: hľadáme X:Y, ale ignorujeme čas zápasu (napr. 15:00) ---
    score_text = ""
    time_part = m.group(2)  # napr. "15:00"
    try:
        time_hh, time_mm = [int(x) for x in time_part.split(":")]
    except Exception:
        time_hh, time_mm = None, None

    all_pairs = re.findall(r"\b(\d{1,2}):(\d{1,2})\b", full_text)
    for g, h in all_pairs:
        try:
            g_i = int(g)
            h_i = int(h)
        except ValueError:
            continue

        # ignoruj čas zápasu
        if time_hh is not None and time_mm is not None:
            if g_i == time_hh and h_i == time_mm:
                continue

        if g_i > 30 or h_i > 30:
            continue

        score_text = f"{g_i}:{h_i}"
        break

    # --- competition (liga + kolo) z <title> ---
    competition = ""
    if soup.title and soup.title.get_text():
        parts = soup.title.get_text().split("|")
        if len(parts) >= 2:
            competition = parts[1].strip()
    if not competition:
        competition = title

    # --- Názov štadióna: z blokov 'Štadión ... Názov ... Hosťovský sektor' ---
    stadium_name = ""
    m_stad = re.search(r"Názov\s+(.+?)\s+Hosťovský sektor", full_text)
    if m_stad:
        stadium_name = m_stad.group(1).strip()

    if not stadium_name:
        # fallback: aspoň 'Štadión FC Slovan Modra' z textu
        m_stad2 = re.search(r"Štadión\s+([^0-9|]+)", full_text)
        if m_stad2:
            stadium_name = ("Štadión " + m_stad2.group(1)).strip()

    print(f"********* MATCH DETAIL STADIUM: {stadium_name}")

    return {
        "title": title,
        "home": home,
        "away": away,
        "start_dt": start_dt,
        "end_dt": end_dt,
        "score_text": score_text,
        "competition": competition,
        "stadium_name": stadium_name,
    }




def _get_match_event_category_id() -> int:
    """
    Nájde ID kategórie 'Zápas' (tvoja DB ju má ako 'Zßpas').
    """
    cat = EventCategory.query.filter(EventCategory.name.ilike("Z%pas")).first()
    if cat:
        return int(cat.id)
    return 1  # fallback, ak vieš, že 1 je Zápas




def _fetch_all_api_items(base_url: str) -> list[dict]:
    """
    Z API URL typu:
      https://sutaze.api.sportnet.online/api/v2/futbalnet/matches?playerAppSpace=...&teamId=...
    natiahne všetky zápasy.

    API vracia JSON dict, nie list, takže:
      - skúsime nájsť pole 'matches'
      - ak tam nie je, zoberieme prvý list, ktorý vyzerá ako list zápasov (dicty).
    """
    # doplníme offset/limit, ale stačí jedna stránka (limit 100 je viac než dosť)
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

    # 1) ak je to list -> rovno list
    if isinstance(data, list):
        print("********* API root is list, len:", len(data))
        return data

    # 2) ak je to dict -> skús 'matches', potom 'items', 'data', '_embedded'
    if isinstance(data, dict):
        # priama kľúče
        for key in ("matches", "items", "data", "results"):
            if isinstance(data.get(key), list):
                print(f"********* API dict[{key}] len:", len(data[key]))
                return data[key]

        # _embedded štýl
        embedded = data.get("_embedded") or data.get("embedded")
        if isinstance(embedded, dict):
            for key in ("matches", "items", "data", "results"):
                if isinstance(embedded.get(key), list):
                    print(f"********* API _embedded[{key}] len:", len(embedded[key]))
                    return embedded[key]

        # fallback – prvé pole, ktoré je list dictov
        for v in data.values():
            if isinstance(v, list) and v and isinstance(v[0], dict):
                print("********* API fallback list len:", len(v))
                return v

    print("********* API: unexpected structure, type:", type(data))
    return []





def _event_data_from_api_match(item: dict) -> dict | None:
    """
    Z jedného JSON zápasu z API spraví dict pre Event.

    Berie:
      - _id / id / matchId ako match_id
      - startDate (alebo dateFrom...) ako začiatok
      - endDate (alebo dateTo...) ako koniec (inak +2h)
      - homeTeam.name, awayTeam.name (+score pri ODOHRATY)
      - venue.name ako názov štadióna (address do Event.address)
      - Google Maps URL z názvu štadióna
    """
    try:
        match_id = item.get("_id") or item.get("id") or item.get("matchId")
        if not match_id:
            return None

        # tímy
        home = item.get("homeTeam") or {}
        away = item.get("awayTeam") or {}
        home_name = (home.get("name") or "").strip()
        away_name = (away.get("name") or "").strip()
        if not home_name or not away_name:
            return None

        # stav / skóre
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
            # pri programe a neodohratých zápasoch len 'Domáci - Hostia'
            title = f"{home_name} - {away_name}"

        # dátum / čas
        start_str = (
            item.get("startDate")
            or item.get("dateFrom")
            or item.get("date_from")
        )
        if not start_str:
            return None

        # ISO '2026-04-25T15:00:00Z' / '2026-04-25T15:00:00.000Z'
        dt_str = start_str.replace("Z", "")
        try:
            start_dt = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            start_dt = datetime.strptime(dt_str.split(".")[0], "%Y-%m-%dT%H:%M:%S")

        end_str = (
            item.get("endDate")
            or item.get("dateTo")
            or item.get("date_to")
        )
        if end_str:
            dt_to = end_str.replace("Z", "")
            try:
                end_dt = datetime.strptime(dt_to, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                end_dt = datetime.strptime(dt_to.split(".")[0], "%Y-%m-%dT%H:%M:%S")
        else:
            end_dt = start_dt + timedelta(hours=2)

        # súťaž / kolo – už len fallback, ak by nebol štadión
        comp = item.get("competition") or {}
        rnd = item.get("round") or {}
        comp_name = (comp.get("name") or "").strip()
        rnd_name = (rnd.get("name") or "").strip()
        league_round = comp_name
        if rnd_name:
            league_round = f"{comp_name} {rnd_name}. kolo".strip()

        # STADION → z API
        venue = item.get("venue") or {}
        stadium_name = (venue.get("name") or "").strip()
        venue_addr = (venue.get("address") or "").strip()

               # do Event.address chceme text "Navigácia na domáci štadión"
        event_address = "Navigácia na štadión"

        # do link chceme Google Maps URL s "Štadión {home_name}"
        destination_str = f"Štadión {home_name}"
        gm_url = (
            "https://www.google.com/maps/dir/?api=1&destination="
            + quote_plus(destination_str)
        )

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









def _safe_int_val(v) -> int:
    try:
        s = str(v).strip()
        if not s:
            return 0
        # skús "32:13" => nečítať ako int
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
    """Heuristika: či séria vyzerá ako text s písmenami aspoň v 'threshold' pomere."""
    s = series.astype(str).str.strip()
    ratio = s.str.contains(r"[A-Za-zÁ-ž]", regex=True).mean()
    return bool(ratio > threshold)

def _fix_club_column(work: pd.DataFrame) -> pd.DataFrame:
    """
    Opraví prípad, keď sa do 'Klub' dostalo poradie (1,2,3,...) namiesto názvu.
    Loguje rozhodnutie a ukáže vzorku hodnôt.
    """
    if "Klub" not in work.columns:
        print("********* _fix_club_column: 'Klub' column NOT present.")
        return work

    vals = work["Klub"].astype(str).str.strip()
    sample = vals.head(5).tolist()
    looks_numeric = pd.to_numeric(vals, errors="coerce").notna().mean() > 0.6
    print(f"********* _fix_club_column: initial sample={sample} | rows={len(vals)} | mostly_numeric={looks_numeric}")

    if looks_numeric:
        # Skús nájsť podľa synonym
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

    # Globálne odstráň prefix poradia, ak tam zostal
    work["Klub"] = work["Klub"].astype(str).str.replace(r"^\s*\d+\s*", "", regex=True).str.strip()
    print(f"********* _fix_club_column: final sample={work['Klub'].head(5).tolist()}")
    return work

# --------- DOM parser pre Sportnet tabuľku (logo + názov + čísla) ---------

def _parse_score_table_dom(html: str) -> List[Dict]:
    """
    Parsuje <tbody><tr> zo Sportnetu, kde je:
      td[0] -> poradie + logo (img[src], img[alt]=názov)
      td[1] -> <a> NÁZOV KLUBU
      td[2:] -> čísla v poradí: Z, V, R, P, Skóre, B (ďalšie stĺpce ignorujeme)
    Vráti list dictov: {club, logo, Z, V, R, P, Skóre, B}
    """
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

            # logo + alt (názov býva aj na <a>)
            logo_url = ""
            club_from_img = ""
            img = tr.find("img")
            if img:
                logo_url = _abs_url(img.get("src", "").strip())
                club_from_img = (img.get("alt", "") or "").strip()

            # názov klubu z druhého stĺpca – text <a>
            club_from_link = ""
            a = tds[1].find("a")
            if a:
                club_from_link = a.get_text(strip=True)

            club = club_from_link or club_from_img
            if not club:
                # fallback: ak nič, skús text v druhom td
                club = tds[1].get_text(strip=True)

            # čísla – čítame konzervatívne: Z,V,R,P,Skóre,B
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
            print(f"********* SCORE DOM ROW: club='{row['club']}' | logo='{row['logo']}' | Z={row['Z']} V={row['V']} R={row['R']} P={row['P']} Skóre='{row['Skóre']}' B={row['B']}")
            rows.append(row)

    print(f"********* SCORE DOM: total parsed rows={len(rows)}")
    return rows

# --------- Pozície: textové štítky ---------

POS_ORDER = ["Brankári", "Obrancovia", "Záložníci", "Útočníci"]
POS_MAP_LOWER = {
    "brankári": "Brankári", "brankari": "Brankári",
    "obrancovia": "Obrancovia",
    "záložníci": "Záložníci", "zaloznici": "Záložníci",
    "útočníci": "Útočníci", "utocnici": "Útočníci",
}

def _normalize_pos_label(s: str) -> str:
    s = (s or "").strip().lower()
    return POS_MAP_LOWER.get(s, "")

def _pos_text_to_id(pos_text: str) -> int:
    """Zmapuje 'Brankári' → ID z tabuľky Position. Najprv lookup, potom fallback 1–4."""
    if not pos_text:
        return 0
    pos = Position.query.filter(Position.name.ilike(pos_text)).first()
    if pos:
        return int(pos.id)
    hard = {"Brankári": 1, "Obrancovia": 2, "Záložníci": 3, "Útočníci": 4}
    return hard.get(pos_text, 0)

def _select_best_img(div) -> str:
    """Z karty hráča vyber posledný <img alt=...>, ktorý býva ostrý (nie blur)."""
    imgs = div.select("img[alt]")
    if not imgs:
        return ""
    return _abs_url(imgs[-1].get("src") or "")

def _parse_roster_positions_and_photos(html: str) -> List[Dict]:
    """
    Vráti list: {name, position_text, photo_url}
    Číta sekcie podľa reálnej HTML štruktúry zo Sportnetu.
    """
    soup = BeautifulSoup(html, "lxml")
    players = []

    sections = soup.select("div.sc-a213866a-0.eikUBD")
    print("********* ROSTER SECTIONS FOUND:", len(sections), "| PLAYERS: 0")

    for sec in sections:
        header = sec.select_one("p.sc-a213866a-2.iriiTg")
        pos_text = _normalize_pos_label(header.get_text(strip=True) if header else "")
        if not pos_text:
            continue

        group_items = sec.select("div.sc-35c36cf-0.hdTPsE")
        for item in group_items:
            a = item.select_one("a.sc-944ea29c-0")
            if not a:
                continue
            name = a.get_text(strip=True)
            if not name:
                continue
            photo = _select_best_img(item)
            players.append({"name": name, "position_text": pos_text, "photo_url": photo})
            print(f"********* ROSTER ITEM: {name} | {pos_text} | {photo}")

    print("********* ROSTER BASED POSITIONS:", len(players), "| PHOTOS:", sum(1 for x in players if x.get('photo_url')))
    return players

def _parse_player_stats_page(html: str) -> List[Dict]:
    """
    Vyparsuje stránku /statistika-hracov: meno + (góly, ŽK, ČK).
    Vráti list dictov: {name, score, yellow, red, position_text?}
    """
    soup = BeautifulSoup(html, "lxml")
    result: List[Dict] = []
    for a in soup.find_all("a"):
        href = a.get("href") or ""
        if "/clen/" not in href:
            continue
        name = a.get_text(strip=True)
        if not name or len(name) < 2:
            continue
        numbers = []
        node = a.parent
        hops = 0
        while node and hops < 8 and len(numbers) < 3:
            text = " ".join(node.stripped_strings).replace(name, "")
            nums = re.findall(r"\b\d+\b", text)
            for n in nums:
                if len(numbers) < 3:
                    numbers.append(int(n))
            node = node.find_next_sibling()
            hops += 1
        score = numbers[0] if len(numbers) > 0 else 0
        yellow = numbers[1] if len(numbers) > 1 else 0
        red = numbers[2] if len(numbers) > 2 else 0
        result.append({
            "name": name,
            "score": score,
            "yellow": yellow,
            "red": red,
            "position_text": "",
        })
    # deduplikácia
    uniq, seen = [], set()
    for p in result:
        if p["name"] in seen:
            continue
        seen.add(p["name"])
        uniq.append(p)
    print("********* STATS PAGE PLAYERS:", len(uniq))
    return uniq

# ------------------------- Routes -------------------------
@team.route("/info")
def team_youth():
    return render_template('teams/youth.html', 
                           current_date=datetime.now(), 
                           next22=Next.next(), 
                           teamz=RightColumn.main_menu(), 
                           next_match=RightColumn.next_match(), 
                           score_table=RightColumn.score_table())


@team.route("/teams")
def list_teams():
    teams = Team.query.order_by(Team.id.asc()).all()
    return render_template(
        'teams/list_teams.html',
        teams=teams,
        current_date=datetime.now(),
        next22=Next.next(),  
        teamz=RightColumn.main_menu(),
        next_match=RightColumn.next_match(),
        score_table=RightColumn.score_table()
    )

@team.route("/teams/new", methods=['GET', 'POST'])
@login_required
@roles_required('Admin', 'WebAdmin')
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
        flash('A New Team has been created!', 'success')
        return redirect(url_for('team.list_teams'))
    return render_template(
        'teams/create_team.html',
        title='New Team',
        form=form,
        legend='New Team',
        teamz=RightColumn.main_menu(),
        next_match=RightColumn.next_match(),
        score_table=RightColumn.score_table()
    )

@team.route("/team/<team_name>")
def team_name(team_name):
    trener = (
        Member.query
        .join(Member.position)                 # prvý join
        .join(Member.teams)                    # druhý join
        .join(User, Member.user_id == User.id) # join na User
        .join(Role, User.roles)                # join na Role cez User.roles
        .filter(Role.name.in_(["Tréner", "Asistent trénera"]))
        .options(
            joinedload(Member.position),
            joinedload(Member.teams),
        )
        .distinct()                            # kvôli M:N väzbám
        .all()
    )
    members = Player.query.filter(Team.id == Player.team_id)\
        .filter(Team.name.like(team_name)).all()
    team_obj = Team.query.filter(Team.name.like(team_name)).first()
    return render_template(
        'teams/team.html',
        team=team_obj,
        members=members,
        trener=trener,
        teamz=RightColumn.main_menu(),
        current_date=datetime.now(),
        next22=Next.next(),  
        next_match=RightColumn.next_match(),
        score_table=RightColumn.score_table()
    )

@team.route("/teams/<int:team_id>/update", methods=['GET', 'POST'])
@login_required
@roles_required('Admin', 'WebAdmin')
def update_team(team_id):
    team_obj = Team.query.get_or_404(team_id)
    form = TeamForm()
    what = request.form.get("what") 

    # ----------- Spracovanie tabuľky výsledkov (score_scrap) -----------
    score_scrap = request.form.get("score_scrap")
    if what == 'score' and team_obj.score_scrap and score_scrap:
        ScoreTable.query.filter(ScoreTable.team_id == team_id).delete()
        html = ""
        try:
            html = _fetch_html(score_scrap)

            # 1) Skús najprv DOM parser (vie vytiahnuť logo + názov)
            dom_rows = _parse_score_table_dom(html)
            inserted = 0

            if dom_rows:
                print("********* SCORE: using DOM parser output")
                for row in dom_rows:
                    klub_val = str(row.get("club", "")).strip()
                    klub_logo = str(row.get("logo", "")).strip()
                    z_val = int(row.get("Z", 0))
                    v_val = int(row.get("V", 0))
                    r_val = int(row.get("R", 0))
                    p_val = int(row.get("P", 0))
                    skore_val = str(row.get("Skóre", "")).strip()
                    b_val = int(row.get("B", 0))

                    # LOG – ukážeme aj logo
                    print(f"********* SCORE INSERT ROW (DOM): Klub='{klub_val}' | Logo='{row.get('logo','')}' | Z={z_val} V={v_val} R={r_val} P={p_val} Skóre='{skore_val}' B={b_val}")

                    rec = ScoreTable(
                        club=klub_val,
                        logo=klub_logo,
                        games=z_val,
                        wins=v_val,
                        draws=r_val,
                        loses=p_val,
                        score=skore_val,
                        points=b_val,
                        team_id=team_id
                    )
                    db.session.add(rec)
                    inserted += 1

                db.session.commit()
                current_app.logger.info("ScoreTable inserted rows (DOM): %s", inserted)
                flash(f"Tabuľka výsledkov aktualizovaná ({inserted} záznamov).", "success")

            else:
                # 2) Fallback – pôvodný pd.read_html prístup
                print("********* SCORE: DOM parser empty, falling back to read_html")
                tables = _best_read_html_tables(html)
                if not tables:
                    flash("Na stránke nebola nájdená žiadna tabuľka výsledkov.", "warning")
                    return redirect(url_for("team.list_teams"))

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
                    print(f"********* SCORE: raw df columns={list(df.columns)} | rows={len(df)}")
                    lower_map = {c.lower(): c for c in df.columns}
                    needed = {}
                    for k, nice in expected.items():
                        if k in lower_map:
                            needed[nice] = lower_map[k]

                    minimal = {"Klub", "Z", "V", "R", "P", "B"}
                    if not minimal.issubset(set(needed.keys())):
                        if not minimal.issubset(set(df.columns)):
                            print("********* SCORE: skipping df - minimal set not present")
                            continue
                        use_cols = list(minimal | {"Skóre"})
                        use_cols = [c for c in use_cols if c in df.columns]
                        work = df[use_cols].copy()
                        print(f"********* SCORE: fallback select columns={list(work.columns)}")
                    else:
                        rename_map = {needed[nice]: nice for nice in needed.keys()}
                        work = df.rename(columns=rename_map)
                        order = ["Klub", "Z", "V", "R", "P", "Skóre", "B"]
                        work = work[[c for c in order if c in work.columns]].copy()
                        print(f"********* SCORE: renamed/order columns={list(work.columns)}")

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
                    print(f"********* SCORE: work columns after fix={list(work.columns)} | rows={len(work)}")
                    print(f"********* SCORE: Klub head -> {work['Klub'].head(10).tolist()}")

                    for _, row in work.iterrows():
                        klub_val = str(row.get("Klub", "")).strip()
                        klub_logo = str(row.get("logo", "")).strip()
                        z_val = int(row.get("Z", 0))
                        v_val = int(row.get("V", 0))
                        r_val = int(row.get("R", 0))
                        p_val = int(row.get("P", 0))
                        skore_val = str(row.get("Skóre", "")).strip()
                        b_val = int(row.get("B", 0))

                        print(f"********* SCORE INSERT ROW: Klub='{klub_val}' | Z={z_val} V={v_val} R={r_val} P={p_val} Skóre='{skore_val}' B={b_val}")

                        rec = ScoreTable(
                            club=klub_val,
                            logo=klub_logo,
                            games=z_val,
                            wins=v_val,
                            draws=r_val,
                            loses=p_val,
                            score=skore_val,
                            points=b_val,
                            team_id=team_id
                        )
                        db.session.add(rec)
                        inserted += 1

                try:
                    db.session.commit()
                except SQLAlchemyError as e:
                    db.session.rollback()
                    current_app.logger.exception("DB commit error (ScoreTable): %s", e)
                    flash("Chyba pri ukladaní tabuľky výsledkov do DB.", "danger")
                    return redirect(url_for("team.list_teams"))

                current_app.logger.info("ScoreTable inserted rows: %s", inserted)
                flash(f"Tabuľka výsledkov aktualizovaná ({inserted} záznamov).", "success")

        except requests.RequestException as e:
            current_app.logger.exception("HTTP/Network chyba score_scrap: %s", e)
            flash("Nepodarilo sa načítať tabuľku (sieťová chyba).", "danger")
            return redirect(url_for("team.list_teams"))
        except Exception as e:
            current_app.logger.exception("Chyba pri parsovaní score_scrap: %s", e)
            current_app.logger.debug("HTML preview: %s", _html_preview_for_log(html))
            flash("Nepodarilo sa spracovať tabuľku výsledkov.", "danger")
            return redirect(url_for("team.list_teams"))

        # ----------- Spracovanie zápasov z API (events_results_scrap) -----------
    what = request.form.get("what")
    events_results_scrap = request.form.get("events_results_scrap") or getattr(team_obj, "events_results_scrap", None)

    # Používame iba jeden API link (Matches results). Program už netreba.
    if what == "events" and events_results_scrap:
        current_app.logger.info("********* EVENTS API FROM: %s", events_results_scrap)

        match_cat_id = _get_match_event_category_id()

        # vymaž staré zápasy tohto tímu v kategórii Zápas
        Event.query.filter(
            Event.event_team_id == team_id,
            Event.event_category_id == match_cat_id
        ).delete()

        try:
            # 1) načítaj všetky zápasy z API
            all_items = _fetch_all_api_items(events_results_scrap)
            current_app.logger.info("********* EVENTS API ITEMS: %s", len(all_items))

            seen_keys = set()
            inserted = 0

            for item in all_items:
                data = _event_data_from_api_match(item)
                if not data:
                    continue

                key = (data["match_id"], data["start_dt"])
                if key in seen_keys:
                    current_app.logger.info("********* DUP MATCH, SKIP: %s", key)
                    continue
                seen_keys.add(key)

                current_app.logger.info(
                    "********* EVENT BUILD: %s | ADDR: %s | LINK: %s",
                    data["title"], data["address"], data["link"]
                )

                ev = Event(
                    title=data["title"],
                    start_event=data["start_dt"],
                    end_event=data["end_dt"],
                    address=data["address"],        # názov štadióna
                    link=data["link"],              # Google Maps URL
                    user_id=current_user.id,        # alebo tvoj systémový user
                    event_category_id=match_cat_id, # Zápas
                    event_team_id=team_id
                )
                db.session.add(ev)
                inserted += 1

            try:
                db.session.commit()
            except SQLAlchemyError as e:
                db.session.rollback()
                current_app.logger.exception("DB commit error (Events): %s", e)
                flash("Chyba pri ukladaní zápasov do kalendára.", "danger")
                return redirect(url_for("team.list_teams"))

            current_app.logger.info("Events inserted rows (API): %s", inserted)
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







    # ----------- Update meta údajov tímu -----------
     # uloženie meta údajov tímu len pri hlavnom "Save" tlačidle
    if form.validate_on_submit() and not what:
        team_obj.name = form.name.data
        team_obj.main_league = form.main_league.data
        team_obj.score_scrap = form.score_scrap.data
        team_obj.player_list_scrap = form.player_list_scrap.data
        team_obj.events_results_scrap = form.events_results_scrap.data
        team_obj.events_program_scrap = form.events_program_scrap.data
        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.exception("DB commit error (Team meta): %s", e)
            flash("Chyba pri ukladaní údajov tímu.", "danger")
            return redirect(url_for('team.list_teams'))
        flash('A Team has been updated!', 'success')
        return redirect(url_for('team.list_teams', team_id=team_obj.id))
    elif request.method == 'GET':
        form.name.data = team_obj.name
        form.main_league.data = team_obj.main_league
        form.score_scrap.data = team_obj.score_scrap
        form.player_list_scrap.data = team_obj.player_list_scrap
        form.events_results_scrap.data = team_obj.events_results_scrap
        form.events_program_scrap.data = team_obj.events_program_scrap

    return render_template(
        'teams/create_team.html',
        title='Update Team',
        form=form,
        team=team_obj,
        legend='Update Team',
        teamz=RightColumn.main_menu(),
        current_date=datetime.now(),
        next22=Next.next(),  
        next_match=RightColumn.next_match(),
        score_table=RightColumn.score_table()
    )

@team.route("/teams/<int:team_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_team(team_id):
    team_obj = Team.query.get_or_404(team_id)
    ifemptyteam = db.session.query(teams_members).filter(teams_members.c.team_id == team_id).all()
    if ifemptyteam:
        flash('A Team is not empty!', 'danger')
    else:
        try:
            db.session.delete(team_obj)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.exception("DB delete error (Team): %s", e)
            flash('Chyba pri mazaní tímu.', 'danger')
            return redirect(url_for('team.list_teams'))
        flash('A Team has been deleted!', 'success')
    return redirect(url_for('team.list_teams'))
