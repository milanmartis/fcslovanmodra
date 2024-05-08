from flask import Flask, session, g, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from .config import Config
from flask_security import Security, SQLAlchemyUserDatastore
# from flask_principal import Principal
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from werkzeug.exceptions import NotFound
from sqlalchemy.orm import sessionmaker
import stripe
import base64
import os
from flask_migrate import Migrate
from sqlalchemy.pool import QueuePool


salt = base64.b64encode(os.urandom(32)).decode('utf-8')

# db = SQLAlchemy()
db = SQLAlchemy()

bcrypt = Bcrypt()
# principal = Principal()
login_manager = LoginManager()

mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)

    app.config.from_object(Config)

    from .models import User, Role, roles_users


    db.init_app(app)
    migrate = Migrate(app, db)  # Inicializácia Flask-Migrate

    # principal.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    login_manager.login_view = 'users.login'
    login_manager.login_message_category = 'info'


    from app.users.routes import users
    from app.posts.routes import posts
    from app.products.routes import products
    from app.main.routes import main
    from app.calendar.routes import calendar
    from app.team.routes import team
    from app.errors.handlers import errors
    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(products)
    app.register_blueprint(main)
    app.register_blueprint(calendar)
    app.register_blueprint(team)
    app.register_blueprint(errors)
    from slugify import slugify

    app.jinja_env.filters['slugify'] = slugify

    from .models import User, Role
    
    @app.errorhandler(NotFound)
    def page_not_found(e):
        # Presmerovanie na chybovú stránku, napríklad:
        # return render_template('error.html', error_message="Stránka nenájdená"), 404

        # Alebo presmerovanie na domovskú stránku:
        return redirect(url_for('main.home'))
    
    if app.debug:
        import logging
        logging.basicConfig()
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()
        
    @app.context_processor
    def utility_processor():
        def aws_image_url():
            return f'https://{Config.AWS_S3_BUCKET}.s3.amazonaws.com/'
        return dict(aws_image_url=aws_image_url)




    
    # @app.before_request
    # def before_request():
    #     if not request.is_secure:
    #         url = request.url.replace('http://', 'https://', 1)
    #         code = 301
    #         return redirect(url, code=code)   
    

    from .models import User, Role
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(app, user_datastore)

    return app