# app/config.py
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SECURITY_PASSWORD_SALT = os.getenv("SECURITY_PASSWORD_SALT")
    SECURITY_PASSWORD_HASH = "bcrypt"
    SECURITY_LOGIN_URL = None
    SECURITY_LOGOUT_URL = None
    SECURITY_REGISTERABLE = False
    SECURITY_SEND_REGISTER_EMAIL = False
    SECURITY_RECOVERABLE = False
    SECURITY_CONFIRMABLE = False
    SECURITY_CHANGEABLE = False

    PERMANENT_SESSION_LIFETIME = timedelta(minutes=1440)

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_EXPIRE_ON_COMMIT = False
    # SQLAlchemy pool (nechaj len config hodnoty; engine nevytváraj v import time!)
    SQSQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 1800,     # napr. 30 min
        "pool_size": 5,
        "max_overflow": 10,
        "pool_timeout": 30,
    }

    # ---- MAIL (Flask-Mail)
    def env_bool(key: str, default: bool = False) -> bool:
        v = os.getenv(key)
        if v is None:
            return default
        return v.strip().lower() in ("1", "true", "yes", "on")

    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.m1.websupport.sk")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "465"))
    MAIL_USE_SSL = env_bool("MAIL_USE_SSL", True)
    MAIL_USE_TLS = env_bool("MAIL_USE_TLS", False)
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = (os.getenv("MAIL_FROM_NAME", ""), os.getenv("MAIL_FROM"))

    # (voliteľné) debug
    MAIL_SUPPRESS_SEND = os.getenv("MAIL_SUPPRESS_SEND", "0") == "1"

    # ---- AWS (ak používaš inde)
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    AWS_SES_REGION = os.getenv("AWS_SES_REGION")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")

    STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY")
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")

    ASYNC_DATABASE_URL = os.getenv("ASYNC_DATABASE_URL")

    # ======================================================
    # PUSH / FIREBASE (PUBLIC web config pre frontend)
    # Toto sú "verejné" hodnoty – môžu ísť do JS cez endpoint.
    # Nájdeš ich vo Firebase Console -> Project settings -> Web app config.
    # ======================================================
    FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")
    FIREBASE_AUTH_DOMAIN = os.getenv("FIREBASE_AUTH_DOMAIN")
    FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")
    FIREBASE_MESSAGING_SENDER_ID = os.getenv("FIREBASE_MESSAGING_SENDER_ID")
    FIREBASE_APP_ID = os.getenv("FIREBASE_APP_ID")

    # VAPID (PUBLIC ide do frontend-u, PRIVATE nikdy neposielať do JS)
    VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY")
    VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY")

    # Firebase service account pre firebase-admin (server-side)
    # Ty máš v .env: FIREBASE_CERT=...
    FIREBASE_CERT = os.getenv("FIREBASE_CERT")
    # (kompat) ak by si používal staré názvy:
    FIREBASE_CERT_JSON = os.getenv("FIREBASE_CERT_JSON")
    FIREBASE_CERT_PATH = os.getenv("FIREBASE_CERT_PATH")
