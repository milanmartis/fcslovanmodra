# app/config.py
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SECURITY_PASSWORD_SALT = os.getenv("SECURITY_PASSWORD_SALT")
    SECURITY_PASSWORD_HASH = "bcrypt"
    SECURITY_LOGIN_URL = "/fs_login"

    PERMANENT_SESSION_LIFETIME = timedelta(minutes=1440)

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_EXPIRE_ON_COMMIT = False

    # SQLAlchemy pool (nechaj len config hodnoty; engine nevytváraj v import time!)
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": int(os.getenv("SQLALCHEMY_POOL_SIZE", "10")),
        "max_overflow": int(os.getenv("SQLALCHEMY_MAX_OVERFLOW", "20")),
        "pool_timeout": int(os.getenv("SQLALCHEMY_POOL_TIMEOUT", "30")),
        "pool_recycle": int(os.getenv("SQLALCHEMY_POOL_RECYCLE", "300")),
        "pool_pre_ping": True,
    }

    # ---- MAIL (Flask-Mail)
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))  # MUSÍ byť int
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "1") == "1"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "0") == "1"

    # dôležité - aby to neviselo večne
    MAIL_TIMEOUT = int(os.getenv("MAIL_TIMEOUT", "10"))  # sekundy

    MAIL_FROM = os.getenv("MAIL_FROM", "klub@fcsm.sk")
    MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME", "FC Slovan Modra")
    MAIL_DEFAULT_SENDER = (MAIL_FROM_NAME, MAIL_FROM)

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
