import os

def cdn_url(key: str) -> str:
    base = os.getenv("CDN_BASE_URL", "").rstrip("/")
    if not base:
        return "/" + key.lstrip("/")
    return f"{base}/{key.lstrip('/')}"


def make_clubs_key(filename: str) -> str:
    f = filename.lstrip("/")
    if f.startswith("clubs/"):
        return f
    return f"clubs/{f}"


from datetime import datetime, timezone
from zoneinfo import ZoneInfo

def to_local(dt: datetime, tz_name: str = "Europe/Bratislava") -> datetime | None:
    if not dt:
        return None
    tz = ZoneInfo(tz_name)

    # ✅ ak je dt naive, berieme ho ako LOKÁLNY čas (Bratislava)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=tz)

    return dt.astimezone(tz)

def format_local(dt, fmt="%d.%m.%Y %H:%M", tz_name="Europe/Bratislava"):
    if not dt:
        return ""
    return to_local(dt, tz_name).strftime(fmt)

def to_utc_iso(dt: datetime) -> str:
    """
    Vráti ISO string v UTC s timezone, aby JS Date() nikdy neuhádol zle.
    Výstup: 2026-02-13T12:00:00Z
    """
    if not dt:
        return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    dt = dt.astimezone(timezone.utc)
    return dt.isoformat().replace("+00:00", "Z")