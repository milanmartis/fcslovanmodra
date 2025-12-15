from flask import Flask, session, g, render_template, redirect, url_for, request, current_app, Response
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_socketio import SocketIO
from flask_migrate import Migrate
from slugify import slugify as _slugify
from datetime import timedelta
from datetime import datetime
from flask_security import Security, SQLAlchemyUserDatastore
from werkzeug.exceptions import NotFound
from sqlalchemy.exc import OperationalError
from sqlalchemy.pool import QueuePool
from app.aws_utils import s3_presign as aws_s3_presign
import boto3
from botocore.config import Config as BotoConfig
import stripe
import base64
import os
from app.firebase_client import init_firebase

from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv

load_dotenv()
init_firebase()

# ---- Rozšírená a bezpečnejšia inicializácia ---------------------------------

DEFAULT_ENGINE_OPTIONS = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
    "poolclass": QueuePool,
    "pool_size": int(os.getenv("SQL_POOL_SIZE", "5")),
    "max_overflow": int(os.getenv("SQL_MAX_OVERFLOW", "10")),
}

salt = base64.b64encode(os.urandom(32)).decode('utf-8')

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()
socketio = SocketIO(cors_allowed_origins="*")


def create_app(config_class=None):
    """
    App factory – bezpečné pripojenie k DB, S3 helpery, Flask-Security, bluepr./filtre.
    """
    if config_class is None:
        from .config import Config as _DefaultConfig
        config_class = _DefaultConfig

    app = Flask(__name__)
    app.config.from_object(config_class)

    # cache pre static súbory nechaj, ale SW/manifest budeme servovať no-store
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(days=365)

    app.config.setdefault("SQLALCHEMY_ENGINE_OPTIONS", DEFAULT_ENGINE_OPTIONS)

    def safe_slug(value):
        try:
            return _slugify(str(value or ""))
        except Exception:
            return ""

    app.jinja_env.filters['safe_slug'] = safe_slug

    db.init_app(app)
    Migrate(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    socketio.init_app(app)

    login_manager.login_view = 'users.login'
    login_manager.login_message_category = 'info'

    from .models import User, Role, roles_users, Sponsor
    from app.aws_utils import make_sponsor_key, s3_presign

    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(app, user_datastore)

    # --- Robustný user_loader -------------------------------------------------
    @login_manager.user_loader
    def load_user(user_id):
        try:
            return user_datastore.find_user(id=user_id)
        except OperationalError:
            db.session.remove()
            return None

    # -------------------------------------------------------------------------
    # PWA / SERVICE WORKER (MUSÍ BYŤ 200 OK, ŽIADNY REDIRECT, ŽIADNY LOGIN)
    # -------------------------------------------------------------------------

    @app.get("/service-worker.js")
    def service_worker_js():
        """
        Tvoj hlavný offline SW.
        Pozor: ak tento SW je ten, ktorý kontroluje stránku,
        tak push subscribe/push eventy pôjdu SEM, nie do iného SW.
        """
        try:
            path = os.path.join(app.static_folder, "service-worker.js")
            if not os.path.exists(path):
                return Response("/* service-worker.js not found */", status=404, mimetype="application/javascript")

            with open(path, "rb") as f:
                data = f.read()

            resp = Response(data, mimetype="application/javascript; charset=utf-8")
            resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            resp.headers["Pragma"] = "no-cache"
            resp.headers["Expires"] = "0"
            resp.headers["Service-Worker-Allowed"] = "/"
            return resp
        except Exception as e:
            return Response(f"/* SW error: {e} */", status=500, mimetype="application/javascript")

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

    # ✅ ROOT push SW (FCM + WebPush) – aby scope bol "/" a nebil sa s /talker/
    # Musí byť dostupné bez login a bez redirectu.
    @app.get("/firebase-messaging-sw.js")
    def firebase_messaging_sw_root():
        """
        Toto routuje na funkciu firebase_messaging_sw z app.talker.routes.
        Dôležité: musí to byť ROOT route, inak iOS/Push scope robí bordel.
        """
        try:
            # v app/talker/routes.py musí existovať: def firebase_messaging_sw(): ...
            from app.talker.routes import firebase_messaging_sw  # noqa
            resp = firebase_messaging_sw()

            # pre istotu vynútime no-store aj tu (ak by to vo view chýbalo)
            resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            resp.headers["Pragma"] = "no-cache"
            resp.headers["Expires"] = "0"
            resp.headers["Service-Worker-Allowed"] = "/"
            return resp
        except Exception as e:
            return Response(f"/* firebase-messaging-sw.js error: {e} */", status=500, mimetype="application/javascript")

    # --- Blueprints -----------------------------------------------------------
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

    # --- Jinja filtre ---------------------------------------------------------
    from slugify import slugify
    app.jinja_env.filters['slugify'] = slugify

    # --- Logging SQL (len v debug) -------------------------------------------
    if app.debug:
        import logging
        logging.basicConfig()
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    # --- Session cleanup ------------------------------------------------------
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    # -------------------------------------------------------------------------
    # 404 → domovská stránka
    # POZOR: Nesmie to presmerovať service-worker.js / manifest / push SW atď.
    # -------------------------------------------------------------------------
    @app.errorhandler(NotFound)
    def page_not_found(e):
        p = request.path

        # PWA súbory nikdy nepresmeruj na HTML
        if p in ("/manifest.webmanifest", "/service-worker.js", "/firebase-messaging-sw.js", "/favicon.ico"):
            return Response("", status=404)

        # statické súbory tiež nepresmeruj
        if p.startswith("/static/"):
            return Response("", status=404)

        return redirect(url_for("main.home"))

    # -------------------------------------------------------------------------
    # ✅ CSP (Report-Only) – POVOLIŤ Firebase/FCM + gstatic + Stripe frame
    # -------------------------------------------------------------------------
    @app.after_request
    def add_csp_headers(response):
        response.headers["Content-Security-Policy-Report-Only"] = (
            "default-src 'self'; "
            "base-uri 'self'; "
            "object-src 'none'; "
            "frame-src 'self' https://www.youtube.com https://www.youtube-nocookie.com https://js.stripe.com; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' "
            "https: "
            "https://www.gstatic.com "
            "https://www.googleapis.com "
            "https://js.stripe.com; "
            "style-src 'self' 'unsafe-inline' https:; "
            "img-src 'self' data: https:; "
            "font-src 'self' data: https:; "
            "connect-src 'self' https: "
            "https://www.googleapis.com "
            "https://*.googleapis.com; "
        )
        return response

    # -------------------------------------------------------------------------
    # Sidebar context
    # -------------------------------------------------------------------------
    @app.context_processor
    def sidebar_context():
        partners_q = (
            Sponsor.query
            .order_by(Sponsor.orderz.asc())
            .all()
        )

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

    # ✅ Jinja helpers for AWS/S3 (aws_image_url + s3_presign)
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

        def s3_presign(key: str, expires: int = 3600) -> str:
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

        return dict(aws_image_url=aws_image_url, s3_presign=s3_presign)

    return app
