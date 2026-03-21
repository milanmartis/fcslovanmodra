import os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo


APP_TZ = os.getenv("APP_TIMEZONE", "Europe/Bratislava")


def app_tz() -> ZoneInfo:
    return ZoneInfo(APP_TZ)


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def now_local() -> datetime:
    return now_utc().astimezone(app_tz())


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


def to_local(dt: datetime, tz_name: str = APP_TZ) -> datetime | None:
    if not dt:
        return None

    tz = ZoneInfo(tz_name)

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=tz)
    else:
        dt = dt.astimezone(tz)

    return dt


def format_local(dt, fmt="%d.%m.%Y %H:%M", tz_name=APP_TZ):
    if not dt:
        return ""
    return to_local(dt, tz_name).strftime(fmt)


def to_utc_iso(dt: datetime) -> str:
    if not dt:
        return ""

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)

    return dt.isoformat().replace("+00:00", "Z")