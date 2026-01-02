import os

def cdn_url(key: str) -> str:
    base = os.getenv("CDN_BASE_URL", "").rstrip("/")
    if not base:
        # ak by si zabudol env premennú, nech to nepadne
        return "/" + key.lstrip("/")
    return f"{base}/{key.lstrip('/')}"