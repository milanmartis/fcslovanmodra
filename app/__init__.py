from flask import Flask, session, g, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from .config import Config
from flask_security import Security, SQLAlchemyUserDatastore
# from flask_principal import Principal

import stripe
import base64
import os


salt = base64.b64encode(os.urandom(32)).decode('utf-8')

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

    @login_manager.user_loader
    def load_user(user_id):
        print(user_id)
        return User.query.get(int(user_id))

    from .models import User, Role
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(app, user_datastore)

    return app
