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
    """
    Podporované formáty:
    - JSON string (service account json) v env
    - cesta k súboru .json v env
    """
    val = _strip_quotes(val)

    # ak vyzerá ako cesta k existujúcemu súboru
    if os.path.exists(val):
        return credentials.Certificate(val)

    # inak predpokladaj JSON string
    # často býva uložené ako single-line s escaped \n, takže to necháme tak
    try:
        data = json.loads(val)
    except json.JSONDecodeError:
        # ešte jeden pokus: ak je JSON double-escaped, skúsime odescape
        try:
            data = json.loads(val.encode("utf-8").decode("unicode_escape"))
        except Exception as e:
            raise ValueError("FIREBASE_CERT is neither a valid path nor valid JSON") from e

    return credentials.Certificate(data)


def init_firebase():
    """
    Inicializuje firebase-admin app pre posielanie push notifikácií.
    Firebase je voliteľný: keď nie je cert, vráti None (aplikácia beží ďalej).
    """

    global _firebase_app
    if _firebase_app:
        return _firebase_app

    # ✅ podporujeme tvoje názvy z .env
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
        # nech push nezhodí appku – len vypíš dôvod
        print("Firebase init failed:", e)
        return None
