from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from app.config import Config
from flask_security import Security, SQLAlchemyUserDatastore


# load users, roles for a session


# from flask_bootstrap import Bootstrap

# bootstrap = Bootstrap()

db = SQLAlchemy()
bcrypt = Bcrypt()

   
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    

    db.init_app(app)
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

    from app.models import User, Role
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    app.security = Security(app, user_datastore)
    
    return app

