from datetime import datetime
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
from flask import current_app
from app import db, login_manager
# from flask_security import RoleMixin
from flask_login import UserMixin

from sqlalchemy.sql import func
from datetime import datetime


roles_members = db.Table('roles_members',
                         db.Column('member_id', db.Integer(),
                                   db.ForeignKey('member.id')),
                         db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

teams_members = db.Table('teams_members',
                         db.Column('member_id', db.Integer(),
                                   db.ForeignKey('member.id')),
                         db.Column('team_id', db.Integer(), db.ForeignKey('team.id')))

positions_members = db.Table('positions_members',
                             db.Column('member_id', db.Integer(),
                                       db.ForeignKey('member.id')),
                             db.Column('position_id', db.Integer(), db.ForeignKey('position.id')))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False,
                           default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    products = db.relationship('Product', backref='saler', lazy=True)

    def get_reset_token(self):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=func.now())
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey(
        'category.id'), nullable=False)
    gallery = db.relationship('PostGallery', backref='gallz', lazy=True)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}', '{self.gallery.image_file2}')"


class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=func.now())
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_visible = db.Column(db.Boolean(), default=True)
    price = db.Column(db.DECIMAL(precision=10, scale=2), nullable=False)
    old_price = db.Column(db.DECIMAL(precision=10, scale=2), nullable=False)
    product_category_id = db.Column(db.Integer, db.ForeignKey(
        'product_category.id'), nullable=False)
    product_gallery = db.relationship('ProductGallery', backref='gallpr', lazy=True)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}', '{self.product_gallery.image_file2}')"


class ProductCategory(db.Model):
    __tablename__ = 'product_category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)

class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)


class PostGallery(db.Model):
    __tablename__ = 'post_gallery'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    image_file2 = db.Column(db.String(30), nullable=False)
    # image_order = db.Column(db.Integer, unique=True, nullable=False)
    orderz = db.Column(db.Integer)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)


class ProductGallery(db.Model):
    __tablename__ = 'product_gallery'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    image_file2 = db.Column(db.String(30), nullable=False)
    # image_order = db.Column(db.Integer, unique=True, nullable=False)
    orderz = db.Column(db.Integer)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)


class Events(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    start_event = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    end_event = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(180), unique=True)


class Team(db.Model):
    __tablename__ = 'team'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    score_scrap = db.Column(db.String(250), nullable=False)
    player_list_scrap = db.Column(db.String(250), nullable=False)


class Position(db.Model):
    __tablename__ = 'position'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(180), unique=True)


class Member(db.Model):
    __tablename__ = 'member'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    phone = db.Column(db.String(250), nullable=False)
    address = db.Column(db.String(250), nullable=False)
    psc = db.Column(db.String(250), nullable=False)
    city = db.Column(db.String(250), nullable=False)
    # eban = db.Column(db.String(250), nullable=False)
    image_file = db.Column(db.String(20), nullable=False,
                           default='default.png')

    weight = db.Column(db.Integer)
    height = db.Column(db.Integer)
    position = db.relationship('Position', secondary=positions_members, lazy='subquery',
                               backref=db.backref('positioned', lazy=True))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    roles = db.relationship('Role', secondary=roles_members, lazy='subquery',
                            backref=db.backref('roled', lazy=True))
    teams = db.relationship('Team', secondary=teams_members, lazy='subquery',
                            backref=db.backref('teamed', lazy=True))
