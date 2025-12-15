import os
import json
import firebase_admin
from firebase_admin import credentials

_firebase_app = None


def _strip_quotes(s: str) -> str:
    s = s.strip()
    if (s.startswith("'") and s.endswith("'")) or (s.startswith('"') and s.endswith('"')):
        return s[1:-1].strip()
    return s


def _load_cert_value(val: str):
    val = _strip_quotes(val)

    if os.path.exists(val):
        return credentials.Certificate(val)

    try:
        data = json.loads(val)
    except json.JSONDecodeError:
        try:
            data = json.loads(val.encode("utf-8").decode("unicode_escape"))
        except Exception as e:
            raise ValueError("FIREBASE_CERT is neither a valid path nor valid JSON") from e

    return credentials.Certificate(data)


def init_firebase():
    global _firebase_app
    if _firebase_app:
        return _firebase_app

    # ak už existuje default app (napr. pri reload)
    try:
        _firebase_app = firebase_admin.get_app()
        return _firebase_app
    except Exception:
        pass

    cert_env = (
        os.environ.get("FIREBASE_CERT")
        or os.environ.get("FIREBASE_CERT_JSON")
        or os.environ.get("FIREBASE_CERT_PATH")
        or os.environ.get("FIREBASE_CERT_JSON_PATH")
    )

    if not cert_env:
        return None

    try:
        cred = _load_cert_value(cert_env)
        _firebase_app = firebase_admin.initialize_app(cred)
        return _firebase_app
    except Exception as e:
        print("Firebase init failed:", e)
        return None
