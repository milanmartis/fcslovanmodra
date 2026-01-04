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