from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from app.config import Config
from flask_security import Security, SQLAlchemyUserDatastore
from datetime import timedelta
import stripe
from flask_sqlalchemy import SQLAlchemy as _BaseSQLAlchemy
# load users, roles for a session
from dotenv import load_dotenv


from flask_bootstrap import Bootstrap

# bootstrap = Bootstrap()
# class SQLAlchemy(_BaseSQLAlchemy):
#     def apply_pool_defaults(self, app, options):
#         super(SQLAlchemy, self).apply_pool_defaults(self, app, options)
#         options["pool_pre_ping"] = True
# load_dotenv()
       
db = SQLAlchemy()

bcrypt = Bcrypt()
# principal = Principal()

   

mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    
    login_manager = LoginManager(app)
    login_manager.login_view = 'users.login'
    login_manager.login_message_category = 'info'

    # app._static_folder = 'static'
    app.config.from_object(Config)
    app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=60)
    app.config['SECRET_KEY'] =  '5791628bb0b13ce0c676dfde280ba245Dret70Nm1255Ui452eeOp125Bnryexx7895'
    app.config['SECURITY_PASSWORD_SALT'] =  'w87tyw9e8fy8fy0wefy0a'
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    stripe.api_key = app.config['STRIPE_SECRET_KEY']
    from app.models import User, Role, roles_users
    # @login_manager.user_loader
    # def load_user(user_id):
    #     return User.query.get(int(user_id))
    # security = Security()
    # user_datastore = SQLAlchemyUserDatastore(db, User, Role, roles_users)
    # security.init_app(app, user_datastore)
    # app.security = Security(user_datastore)

    db.init_app(app)
    # principal.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    
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


    # from app.models import User, Role

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    
    # from app.models import User, Role
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    app.security = Security(app, user_datastore)
    
    return app
    # app.security = Security(user_datastore)
    # return app

