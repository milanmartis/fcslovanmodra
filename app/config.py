# app/config.py
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    # -------------------------
    # Core / Security
    # -------------------------
    SECRET_KEY = os.getenv("SECRET_KEY")  # musí byť stabilný v Heroku Config Vars
    SECURITY_PASSWORD_SALT = os.getenv("SECURITY_PASSWORD_SALT")
    SECURITY_PASSWORD_HASH = "bcrypt"

    # nechávam tvoje pôvodné nastavenia
    SECURITY_LOGIN_URL = None
    SECURITY_LOGOUT_URL = None
    SECURITY_REGISTERABLE = False
    SECURITY_SEND_REGISTER_EMAIL = False
    SECURITY_RECOVERABLE = False
    SECURITY_CONFIRMABLE = False
    SECURITY_CHANGEABLE = False

    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=1440)
    # (voliteľné, ale odporúčané)
    SESSION_REFRESH_EACH_REQUEST = True

    # -------------------------
    # Cookies (kritické pre login + socket.io na novej doméne)
    # -------------------------
    # Bezpečné defaulty pre produkciu (Heroku/HTTPS)
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "1") == "1"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")

    # Flask-Login remember cookie (ak používaš remember me)
    REMEMBER_COOKIE_SECURE = os.getenv("REMEMBER_COOKIE_SECURE", "1") == "1"
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = os.getenv("REMEMBER_COOKIE_SAMESITE", "Lax")

    # DOMAIN nech je buď prázdne (odporúčané), alebo ".fcslovanmodra.sk"
    # Ak to nastavíš zle, cookie sa nebude ukladať pre tvoju doménu.
    _cookie_domain = (os.getenv("SESSION_COOKIE_DOMAIN") or "").strip()
    SESSION_COOKIE_DOMAIN = _cookie_domain or None
    REMEMBER_COOKIE_DOMAIN = SESSION_COOKIE_DOMAIN

    SESSION_COOKIE_PATH = "/"
    REMEMBER_COOKIE_PATH = "/"

    # pomáha pri url_for(..., _external=True), aby generoval https linky
    PREFERRED_URL_SCHEME = os.getenv("PREFERRED_URL_SCHEME", "https")

    # -------------------------
    # SQLAlchemy
    # -------------------------
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_EXPIRE_ON_COMMIT = False

    # SQLAlchemy pool (ponechané tvoje pôvodné hodnoty)
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 1800,  # 30 min
        "pool_size": 5,
        "max_overflow": 5,
        "pool_timeout": 30,
    }

    # -------------------------
    # MAIL (Flask-Mail)
    # -------------------------
    @staticmethod
    def env_bool(key: str, default: bool = False) -> bool:
        v = os.getenv(key)
        if v is None:
            return default
        return v.strip().lower() in ("1", "true", "yes", "on")

    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.m1.websupport.sk")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "465"))
    MAIL_USE_SSL = env_bool.__func__("MAIL_USE_SSL", True)
    MAIL_USE_TLS = env_bool.__func__("MAIL_USE_TLS", False)
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = (os.getenv("MAIL_FROM_NAME", ""), os.getenv("MAIL_FROM"))

    MAIL_SUPPRESS_SEND = os.getenv("MAIL_SUPPRESS_SEND", "0") == "1"

    # -------------------------
    # AWS
    # -------------------------
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    AWS_SES_REGION = os.getenv("AWS_SES_REGION")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")

    # -------------------------
    # Stripe
    # -------------------------
    STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY")
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")

    # -------------------------
    # Async DB URL
    # -------------------------
    ASYNC_DATABASE_URL = os.getenv("ASYNC_DATABASE_URL")

    # ======================================================
    # PUSH / FIREBASE (PUBLIC web config pre frontend)
    # ======================================================
    FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")
    FIREBASE_AUTH_DOMAIN = os.getenv("FIREBASE_AUTH_DOMAIN")
    FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")
    FIREBASE_MESSAGING_SENDER_ID = os.getenv("FIREBASE_MESSAGING_SENDER_ID")
    FIREBASE_APP_ID = os.getenv("FIREBASE_APP_ID")
    # APP_TIMEZONE = "Europe/Bratislava"
    APP_TIMEZONE = os.getenv("APP_TIMEZONE", "Europe/London")
    # VAPID (PUBLIC ide do frontend-u, PRIVATE nikdy neposielať do JS)
    VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY")
    VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY")

    # Firebase service account pre firebase-admin (server-side)
    FIREBASE_CERT = os.getenv("FIREBASE_CERT")
    FIREBASE_CERT_JSON = os.getenv("FIREBASE_CERT_JSON")
    FIREBASE_CERT_PATH = os.getenv("FIREBASE_CERT_PATH")
