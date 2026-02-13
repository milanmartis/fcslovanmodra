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

    # ak je dt naive, berieme ho ako UTC (lebo ty tak ukladáš do DB)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt.astimezone(tz)