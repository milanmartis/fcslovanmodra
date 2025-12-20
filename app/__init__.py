from flask import Flask, redirect, url_for, request, Response
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_socketio import SocketIO
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from slugify import slugify as _slugify
from datetime import timedelta, datetime
from werkzeug.exceptions import NotFound
from sqlalchemy.exc import OperationalError


from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv
import base64
import os
import boto3
from botocore.config import Config as BotoConfig
# ✅ nevolaj init_firebase() pri importe modulu (môže to robiť side-effecty)
# zober si ho až v create_app, keď je app pripravená
# from app.firebase_client import init_firebase

load_dotenv()

DEFAULT_ENGINE_OPTIONS = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
    "poolclass": QueuePool,
    "pool_size": int(os.getenv("SQL_POOL_SIZE", "5")),
    "max_overflow": int(os.getenv("SQL_MAX_OVERFLOW", "10")),
}

salt = base64.b64encode(os.urandom(32)).decode("utf-8")

db = SQLAlchemy()
bcrypt = Bcrypt()
# login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()
socketio = SocketIO(cors_allowed_origins="*")


def create_app(config_class=None):
    if config_class is None:
        from .config import Config as _DefaultConfig
        config_class = _DefaultConfig

    app = Flask(__name__)
    app.config.from_object(config_class)

    # cache pre static súbory ok, ale SW/manifest budeme no-store
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = timedelta(days=365)
    app.config.setdefault("SQLALCHEMY_ENGINE_OPTIONS", DEFAULT_ENGINE_OPTIONS)

    # # ✅ Firebase init až tu (nie pri importe)
    # try:
    #     init_firebase()
    # except Exception:
    #     pass

    def safe_slug(value):
        try:
            return _slugify(str(value or ""))
        except Exception:
            return ""

    app.jinja_env.filters["safe_slug"] = safe_slug

    db.init_app(app)
    Migrate(app, db)
    bcrypt.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    socketio.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "users.login"  # tvoj endpoint
    login_manager.login_message = "Please log in to access this page."
    login_manager.init_app(app)

    # models + security až po init db
    from .models import User, Role, roles_users, Sponsor

    @login_manager.user_loader
    def load_user(user_id: str):
        try:
            u = db.session.get(User, int(user_id))
            if u is not None:
                db.session.add(u)  # reattach, ak by bol detached
            return u
        except Exception:
            return None

    # ------------------------------------------------------------
    # ✅ ROOT /firebase-messaging-sw.js – mapuje sa na talker.routes
    # ------------------------------------------------------------
    @app.get("/firebase-messaging-sw.js")
    def firebase_messaging_sw_root():
        """
        Jediný service worker, ktorý má mať scope "/".
        iOS push je extrémne citlivý na to, keď existujú 2 rôzne SW pre root scope.
        """
        from app.talker.routes import firebase_messaging_sw  # lazy import (bez circular importu)
        resp = firebase_messaging_sw()

        # ✅ poistka: vždy správny content-type + no-store (aby iOS neťahal starý SW)
        try:
            resp.headers.setdefault("Content-Type", "application/javascript; charset=utf-8")
            resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            resp.headers["Pragma"] = "no-cache"
            resp.headers["Expires"] = "0"
            resp.headers.setdefault("Service-Worker-Allowed", "/")
        except Exception:
            # keby firebase_messaging_sw() vrátil niečo iné než Response
            pass

        return resp

    # ------------------------------------------------------------
    # ❌ /service-worker.js NEPOUŽÍVAJ ako druhý SW (konflikt s push SW)
    # ------------------------------------------------------------
    @app.get("/service-worker.js")
    def service_worker_js():
        """
        DEPRECATED:
        Ak máš niekde starý JS, ktorý registeruje '/service-worker.js',
        tak to na iOS/Chrome vie rozbiť push, lebo root scope obsadí iný SW.
        Vrátime 410, aby sa klient odlepil od starej registrácie.
        """
        return Response(
            "/* DEPRECATED – use /firebase-messaging-sw.js */",
            status=410,
            mimetype="application/javascript; charset=utf-8",
            headers={
                "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
                "Pragma": "no-cache",
                "Expires": "0",
                "Service-Worker-Allowed": "/",
            },
        )

    @app.get("/manifest.webmanifest")
    def manifest_webmanifest():
        path = os.path.join(app.static_folder, "manifest.webmanifest")
        if not os.path.exists(path):
            return Response("{}", status=404, mimetype="application/manifest+json")

        with open(path, "rb") as f:
            data = f.read()

        resp = Response(data, mimetype="application/manifest+json; charset=utf-8")
        resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        resp.headers["Pragma"] = "no-cache"
        resp.headers["Expires"] = "0"
        return resp

    # --- Blueprints ---
    from app.users.routes import users
    from app.posts.routes import posts
    from app.sponsors.routes import sponsors_bp
    from app.products.routes import products
    from app.main.routes import main, Next, RightColumn
    from app.calendar.routes import calendar
    from app.team.routes import team
    from app.errors.handlers import errors
    from app.talker.routes import talker
    from app.talker_admin.routes import talker_admin

    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(products)
    app.register_blueprint(main)
    app.register_blueprint(calendar)
    app.register_blueprint(team)
    app.register_blueprint(errors)
    app.register_blueprint(sponsors_bp)
    app.register_blueprint(talker)
    app.register_blueprint(talker_admin)

    from slugify import slugify
    app.jinja_env.filters["slugify"] = slugify

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    @app.errorhandler(NotFound)
    def page_not_found(e):
        p = request.path
        if p in ("/manifest.webmanifest", "/service-worker.js", "/firebase-messaging-sw.js", "/favicon.ico"):
            return Response("", status=404)
        if p.startswith("/static/"):
            return Response("", status=404)
        return redirect(url_for("main.home"))

    @app.after_request
    def add_csp_headers(response):
        response.headers["Content-Security-Policy-Report-Only"] = (
            "default-src 'self'; "
            "base-uri 'self'; "
            "object-src 'none'; "

            # Stripe/YouTube iframes
            "frame-src 'self' https://www.youtube.com https://www.youtube-nocookie.com https://js.stripe.com https://hooks.stripe.com; "

            # Stripe JS
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https: https://www.gstatic.com https://www.googleapis.com https://js.stripe.com; "

            "style-src 'self' 'unsafe-inline' https:; "
            "img-src 'self' data: https:; "
            "font-src 'self' data: https:; "

            # ✅ TU je fix: Stripe connect endpoints (m.stripe.com/6 + stripe.com + api.stripe.com + m.stripe.network)
            "connect-src 'self' https: "
            "https://fcm.googleapis.com "
            "https://firebaseinstallations.googleapis.com "
            "https://firebase.googleapis.com "
            "https://www.googleapis.com https://*.googleapis.com "
            "https://api.stripe.com https://stripe.com https://m.stripe.com https://m.stripe.network; "
        )
        return response

    # ---- Sidebar context + S3 helpers (ponechávam tvoju logiku) ----
    from app.aws_utils import make_sponsor_key, s3_presign

    @app.context_processor
    def sidebar_context():
        partners_q = Sponsor.query.order_by(Sponsor.orderz.asc()).all()
        partners = []
        for s in partners_q:
            key = make_sponsor_key(s.image_file)
            partners.append({
                "id": s.id,
                "name": s.name or "",
                "url": s.url or "",
                "image_url": s3_presign(key),
            })
        return dict(
            partners=partners,
            current_date=datetime.now(),
            next22=Next.next(),
            teamz=RightColumn.main_menu(),
            next_match=RightColumn.next_match(),
            score_table=RightColumn.score_table(),
            hide_sidebar_tables=False,
        )

    _S3_CACHE = {"client": None, "bucket": (app.config.get("AWS_S3_BUCKET") or "").strip()}

    def _build_s3_client():
        ak = (app.config.get("AWS_ACCESS_KEY_ID") or "").strip()
        sk = (app.config.get("AWS_SECRET_ACCESS_KEY") or "").strip()
        bucket = _S3_CACHE["bucket"]
        if not bucket or not ak or not sk:
            return None
        try:
            probe = boto3.client("s3", aws_access_key_id=ak, aws_secret_access_key=sk)
            loc = probe.get_bucket_location(Bucket=bucket)
            region = loc.get("LocationConstraint") or "us-east-1"
            return boto3.client(
                "s3",
                region_name=region,
                aws_access_key_id=ak,
                aws_secret_access_key=sk,
                config=BotoConfig(signature_version="s3v4"),
            )
        except Exception:
            return None

    def _s3():
        if _S3_CACHE["client"] is None:
            _S3_CACHE["client"] = _build_s3_client()
        return _S3_CACHE["client"]

    @app.context_processor
    def aws_helpers():
        def aws_image_url():
            bucket = _S3_CACHE["bucket"]
            return f"https://{bucket}.s3.amazonaws.com/" if bucket else ""

        def s3_presign_local(key: str, expires: int = 3600) -> str:
            c = _s3()
            bucket = _S3_CACHE["bucket"]
            if not c or not bucket or not key:
                return ""
            try:
                return c.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": bucket, "Key": key},
                    ExpiresIn=expires,
                )
            except Exception:
                return ""

        return dict(aws_image_url=aws_image_url, s3_presign=s3_presign_local)

    return app
