from flask import Flask, session, g, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from app.config import Config
from flask_security import Security, SQLAlchemyUserDatastore
from flask_principal import Principal

import stripe
import base64
import os


salt = base64.b64encode(os.urandom(32)).decode('utf-8')

# from flask_bootstrap import Bootstrap

# bootstrap = Bootstrap()
# class SQLAlchemy(_BaseSQLAlchemy):
#     def apply_pool_defaults(self, app, options):
#         super(SQLAlchemy, self).apply_pool_defaults(self, app, options)
#         options["pool_pre_ping"] = True
       
db = SQLAlchemy()

bcrypt = Bcrypt()
principal = Principal()
security = Security()
login_manager = LoginManager()

mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    
    # app._static_folder = 'static'
    app.config.from_object(Config)

    from .models import User, Role, roles_users
    # @login_manager.user_loader
    #
    # def load_user(user_id):
    #     return User.query.get(int(user_id))
    # security = Security()
    # user_datastore = SQLAlchemyUserDatastore(db, User, Role, roles_users)
    # security.init_app(app, user_datastore)
    # app.security = Security(user_datastore)

    
    db.init_app(app)
    principal.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    
    login_manager.login_view = 'users.login'
    login_manager.login_message_category = 'info'
    
    # bootstrap.init_app(app)

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

    # @app.before_request
    # def initialize_identity():
    #     if not hasattr(g, 'identity'):
    #         g.identity = None
    # from app.models import User, Role
    from .models import User, Role

    @login_manager.user_loader
    def load_user(user_id):
        print(user_id)
        return User.query.get(int(user_id))
    
    
    # user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    # security = Security(app, user_datastore)

# Inicializácia Flask-Security
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    # security = Security(app, user_datastore)
    # security.init_app(app, user_datastore)

    app.security = Security(user_datastore)
    # errors.errorhandler(404)
    # def page_not_found(e):
    #     return redirect(url_for('error.error_404'))
        
        # # your processing here
        # return render_template('errors/404.html', title='Error', next22=Next.next(), teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())
        
    return app


    # app.security = Security(user_datastore)
    # return app

