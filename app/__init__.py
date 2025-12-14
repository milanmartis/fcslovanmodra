from flask import Flask, session, g, render_template, redirect, url_for, request, current_app
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
from flask import current_app
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

# Kľúčové: SQLAlchemy engine options – heartbeat na spojeniach, recyklácia poolu
DEFAULT_ENGINE_OPTIONS = {
    "pool_pre_ping": True,     # pri každom požiadavku skontroluje, či DB spojenie žije
    "pool_recycle": 300,       # uzavrie idle spojenia po 5 min, zabráni „stale connections“
    "poolclass": QueuePool,    # štandardný pool
    "pool_size": int(os.getenv("SQL_POOL_SIZE", "5")),
    "max_overflow": int(os.getenv("SQL_MAX_OVERFLOW", "10")),
}

salt = base64.b64encode(os.urandom(32)).decode('utf-8')

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()
# socketio = SocketIO(cors_allowed_origins="*")


def create_app(config_class=None):
    """
    App factory – bezpečné pripojenie k DB, S3 helpery, Flask-Security, bluepr./filtre.
    """
    # Import konfigurácie
    if config_class is None:
        from .config import Config as _DefaultConfig
        config_class = _DefaultConfig

    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(days=365)
    
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

    

    # Vstreknúť engine options, ak nie sú definované v configu
    app.config.setdefault("SQLALCHEMY_ENGINE_OPTIONS", DEFAULT_ENGINE_OPTIONS)
 
   
    def safe_slug(value):
        try:
            return _slugify(str(value or ""))
        except Exception:
            return ""

    app.jinja_env.filters['safe_slug'] = safe_slug
    
    db.init_app(app)
    Migrate(app, db)  # Flask-Migrate
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    socketio.init_app(app)
    login_manager.login_view = 'users.login'
    login_manager.login_message_category = 'info'
    
    from .models import User, Role, roles_users, Sponsor
    from app.aws_utils import make_sponsor_key, s3_presign
    # Flask-Security
        # Flask-Security
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(app, user_datastore)  # necháme register_blueprint default (True)

    # --- Robustný user_loader: aplikácia nespadne, keď DB vypadne --------------
    @login_manager.user_loader
    def load_user(user_id):
        try:
            # Flask-Security rovnako volá user_datastore, ale tu si strážime výnimky
            return user_datastore.find_user(id=user_id)
        except OperationalError:
            # DB nedostupná → nechaj užívateľa ako anonymného, nevyhadzuj 500
            db.session.remove()
            return None
        


    # --- Blueprints ------------------------------------------------------------
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
    
    # --- Jinja filtre ----------------------------------------------------------
    from slugify import slugify
    app.jinja_env.filters['slugify'] = slugify

    # --- Logging SQL (len v debug) --------------------------------------------
    if app.debug:
        import logging
        logging.basicConfig()
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    # --- Session cleanup -------------------------------------------------------
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        # uvoľni session po každej požiadavke
        db.session.remove()

    # --- Service Worker (aby nepádal pri výpadku DB) --------------------------
    # SW súbor musí byť dostupný ako public asset a bez loginu.
    @app.route("/service-worker.js")
    def service_worker():
        # musí existovať v static/service-worker.js
        return current_app.send_static_file("service-worker.js")

    # --- 404 → domovská stránka (bez redirect slučky pri DB výpadku) ----------
    @app.errorhandler(NotFound)
    def page_not_found(e):
        # Tu nechávam redirect na 'main.home' podľa tvojho pôvodného zámeru.
        # Keďže user_loader je safe a /home neháže výnimku pri DB výpadku,
        # nekonečná slučka nehrozí.
        return redirect(url_for('main.home'))

    # --- Jinja pomocníci pre S3 (safe) ----------------------------------------
    # import boto3
    # from botocore.config import Config as BotoConfig
    # _S3_CLIENT = {"client": None, "bucket": (app.config.get("AWS_S3_BUCKET") or "").strip()}

    # def _s3_build_client():
    #     ak = (app.config.get("AWS_ACCESS_KEY_ID") or "").strip()
    #     sk = (app.config.get("AWS_SECRET_ACCESS_KEY") or "").strip()
    #     bucket = _S3_CLIENT["bucket"]

    #     if not bucket or not ak or not sk:
    #         return None

    #     try:
    #         # 1) zisti región bucketu
    #         probe = boto3.client("s3", aws_access_key_id=ak, aws_secret_access_key=sk)
    #         loc = probe.get_bucket_location(Bucket=bucket)
    #         region = loc.get("LocationConstraint") or "us-east-1"

    #         # 2) klient v správnom regióne
    #         return boto3.client(
    #             "s3",
    #             region_name=region,
    #             aws_access_key_id=ak,
    #             aws_secret_access_key=sk,
    #             config=BotoConfig(signature_version="s3v4"),
    #         )
    #     except Exception:
    #         # nech App nepadá kvôli S3
    #         return None

    # def _s3():
    #     if _S3_CLIENT["client"] is None:
    #         _S3_CLIENT["client"] = _s3_build_client()
    #     return _S3_CLIENT["client"]

    @app.after_request
    def add_csp_headers(response):
        response.headers["Content-Security-Policy-Report-Only"] = (
            "default-src 'self'; "
            "base-uri 'self'; "
            "object-src 'none'; "
            "frame-src 'self' https://www.youtube.com https://www.youtube-nocookie.com; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https:; "
            "style-src 'self' 'unsafe-inline' https:; "
            "img-src 'self' data: https:; "
            "font-src 'self' data: https:; "
            "connect-src 'self' https:; "
        )
        return response


    @app.context_processor
    def sidebar_context():
        # PARTNERI
        partners_q = (
            Sponsor.query
            # .filter_by(kind="partner")
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

    # ✅ Jinja helpers for AWS/S3 (aws_image_url + s3_presign) - ALWAYS available
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

    # @app.context_processor
    # def utility_processor():
    #     def aws_image_url():
    #         # základ pre verejné assety; pre súkromné použi s3_presign
    #         bucket = _S3_CLIENT["bucket"]
    #         return f'https://{bucket}.s3.amazonaws.com/' if bucket else ''

    #     def s3_presign(key: str, expires: int = 3600) -> str:
    #         c = _s3()
    #         bucket = _S3_CLIENT["bucket"]
    #         if not c or not bucket or not key:
    #             return ''  # bezpečné prázdno namiesto výnimky
    #         try:
    #             return c.generate_presigned_url(
    #                 "get_object",
    #                 Params={"Bucket": bucket, "Key": key},
    #                 ExpiresIn=expires,
    #             )
    #         except Exception:
    #             return ''

    #     return dict(aws_image_url=aws_image_url, s3_presign=s3_presign)

    return app
