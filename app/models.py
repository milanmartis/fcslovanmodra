from datetime import datetime
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
from flask import current_app
from app import db, login_manager
from flask_security import RoleMixin, UserMixin
from sqlalchemy.sql import func
import uuid

# =========================
# Association / M2M tables
# =========================

talk_room_members = db.Table(
    "talk_room_members",
    db.Column("room_id", db.Integer, db.ForeignKey("talk_room.id"), primary_key=True),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("is_admin", db.Boolean, nullable=False, server_default="false"),
    db.Column("joined_at", db.DateTime(timezone=True), server_default=func.now()),
)


variant_products = db.Table(
    'variant_products',
    db.Column('product_id', db.Integer(), db.ForeignKey('product.id')),
    db.Column('variant_id', db.Integer(), db.ForeignKey('product_variant.id')),
    db.Column('variant_text', db.String(100), nullable=False),
    db.Column('variant_image', db.Text, nullable=True),
)

roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id')),
)

teams_members = db.Table(
    'teams_members',
    db.Column('member_id', db.Integer(), db.ForeignKey('member.id')),
    db.Column('team_id', db.Integer(), db.ForeignKey('team.id')),
)

positions_members = db.Table(
    'positions_members',
    db.Column('member_id', db.Integer(), db.ForeignKey('member.id')),
    db.Column('position_id', db.Integer(), db.ForeignKey('position.id')),
)

product_variant_product = db.Table(
    'product_variant_product',
    db.Column('product_variant_id', db.Integer(), db.ForeignKey('product_variant.id')),
    db.Column('product_id', db.Integer(), db.ForeignKey('product.id')),
)



class Club(db.Model):
    __tablename__ = "club"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    subdomain = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Club {self.id} {self.subdomain}>"


# ===============
# User management
# ===============
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    confirm = db.Column(db.Boolean(), default=False)
    active = db.Column(db.Boolean, default=True)
    confirmed_at = db.Column(db.DateTime())
    fs_uniquifier = db.Column(db.String(64), unique=True)
    

    posts = db.relationship('Post', backref='author', lazy='select')
    products = db.relationship('Product', backref='saler', lazy='select')

    roles = db.relationship(
        'Role',
        secondary='roles_users',
        lazy='subquery',
        backref=db.backref('users', lazy='dynamic'),
    )

    def has_roles(self, *args):
        return set(args).issubset({role.name for role in self.roles})

    # Flask-Login očakáva string
    def get_id(self):
        return str(self.id)

    def get_reset_token(self):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})

    def get_confirm_token(self):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except Exception:
            return None
        return User.query.get(int(user_id))

    @staticmethod
    def verify_confirm_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except Exception:
            return None
        return User.query.get(int(user_id))

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}', '{self.roles}')"





class TalkRoom(db.Model):
    __tablename__ = "talk_room"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)

    # ak je room viazaný na Team (U19/U17…), bude vyplnené
    team_id = db.Column(db.Integer, db.ForeignKey("team.id"), nullable=True)

    # kto room vytvoril
    created_by_user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    members = db.relationship(
        "User",
        secondary=talk_room_members,
        lazy="subquery",
        backref=db.backref("talk_rooms", lazy="dynamic"),
    )

    def __repr__(self):
        return f"<TalkRoom {self.id} {self.name}>"



class TalkMessage(db.Model):
    __tablename__ = "talk_message"

    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey("talk_room.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    room = db.relationship("TalkRoom", backref=db.backref("messages", lazy="dynamic", cascade="all, delete-orphan"))
    author = db.relationship("User")

    def __repr__(self):
        return f"<TalkMessage {self.id} room={self.room_id} user={self.user_id}>"


class WebPushSubscription(db.Model):
    __tablename__ = "webpush_subscription"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)

    # Apple/Chrome endpoint (na iOS typicky https://web.push.apple.com/...)
    endpoint = db.Column(db.Text, nullable=False, unique=True)

    # VAPID keys z PushManager.subscribe() -> subscription.keys
    p256dh = db.Column(db.String(256), nullable=False)
    auth = db.Column(db.String(128), nullable=False)

    # voliteľné: user-agent / device popis pre debug
    device = db.Column(db.String(200), nullable=True)
    platform = db.Column(db.String(50), nullable=True)  # napr. "ios_webpush", "webpush"

    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    last_seen_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = db.relationship("User")

    def __repr__(self):
        return f"<WebPushSubscription {self.id} user={self.user_id}>"



class PushToken(db.Model):
    __tablename__ = "push_token"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)

    # FCM registration token (z browsera / mobilu)
    token = db.Column(db.String(512), nullable=False, unique=True)

    platform = db.Column(db.String(50), nullable=True)   # "web", "ios", "android"
    device = db.Column(db.String(200), nullable=True)    # napr. user-agent skrátene
    last_seen_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = db.relationship("User")
# =====
# Blog
# =====






class Post(db.Model):
    __tablename__ = 'post'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime(timezone=True), nullable=False, default=func.now())
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

    # PÔVODNÝ názov si necháme kvôli spätnej kompatibilite:
    gallery = db.relationship('PostGallery', backref='post', lazy='select', cascade="all, delete-orphan")

    # Preferovaný alias pre šablóny a eager loading:
    @property
    def galleries(self):
        return self.gallery

    # Pomocná vlastnosť – nájde cover (orderz == 0), inak prvý
    def cover(self):
        if not self.gallery:
            return None
        cov = next((g for g in self.gallery if g.orderz == 0 or g.orderz == '0'), None)
        return cov or (self.gallery[0] if self.gallery else None)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


class PostGallery(db.Model):
    __tablename__ = 'post_gallery'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    image_file2 = db.Column(db.String(250), nullable=False)
    orderz = db.Column(db.Integer)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)


class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)


# =========
# Products
# =========
class Product(db.Model):
    __tablename__ = 'product'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    stripe_link = db.Column(db.String(100), nullable=False)
    youtube_link = db.Column(db.String(300), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=func.now())
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_visible = db.Column(db.Boolean(), default=True)
    price = db.Column(db.DECIMAL(precision=10, scale=2), nullable=False)
    old_price = db.Column(db.DECIMAL(precision=10, scale=2), nullable=False)
    product_category_id = db.Column(db.Integer, db.ForeignKey('product_category.id'), nullable=False)

    product_gallery = db.relationship('ProductGallery', backref='product', lazy='select', cascade="all, delete-orphan")

    # prepojenie na varianty cez variant_products
    variant = db.relationship(
        'ProductVariant',
        secondary='variant_products',
        lazy='subquery',
        backref=db.backref('products', lazy='dynamic'),
    )

    def __repr__(self):
        return f"Product('{self.title}', '{self.date_posted}', '{self.product_category_id}')"


class ProductGallery(db.Model):
    __tablename__ = 'product_gallery'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    image_file2 = db.Column(db.String(250), nullable=False)
    orderz = db.Column(db.Integer)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)


class ProductVariant(db.Model):
    __tablename__ = 'product_variant'
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    type = db.Column(db.Integer, db.ForeignKey('type_product_variant.id'), nullable=False)


class ProductCategory(db.Model):
    __tablename__ = 'product_category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)


# =======
# Events
# =======
class Event(db.Model):
    __tablename__ = 'event'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    start_event = db.Column(db.DateTime(timezone=True))
    end_event = db.Column(db.DateTime(timezone=True))
    address = db.Column(db.String(250), nullable=False)
    link = db.Column(db.String(550), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_category_id = db.Column(db.Integer, db.ForeignKey('event_category.id'), nullable=False)
    event_team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)


class EventCategory(db.Model):
    __tablename__ = 'event_category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)


# =====
# RBAC
# =====
class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(180), unique=True)
    description = db.Column(db.Text)


# ========
# Teams etc
# ========
class Team(db.Model):
    __tablename__ = 'team'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    main_league = db.Column(db.String(300), nullable=False)
    score_scrap = db.Column(db.String(250), nullable=False)
    player_list_scrap = db.Column(db.String(250), nullable=False)
    
    events_results_scrap = db.Column(db.String(550))  
    events_program_scrap = db.Column(db.String(550)) 


class Position(db.Model):
    __tablename__ = 'position'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(180), unique=True)


class Player(db.Model):
    __tablename__ = 'player'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    position = db.Column(db.Integer)
    team = db.Column(db.String(250), nullable=False)
    score = db.Column(db.Integer)
    yellow_card = db.Column(db.Integer)
    red_card = db.Column(db.Integer)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    photo_url = db.Column(db.String(600))



class Member(db.Model):
    __tablename__ = 'member'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    phone = db.Column(db.String(250), nullable=False)
    address = db.Column(db.String(250), nullable=False)
    psc = db.Column(db.String(250), nullable=False)
    city = db.Column(db.String(250), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.png')

    weight = db.Column(db.Integer)
    height = db.Column(db.Integer)

    position = db.relationship(
        'Position',
        secondary=positions_members,
        lazy='subquery',
        backref=db.backref('members', lazy='dynamic'),
    )

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    teams = db.relationship(
        'Team',
        secondary=teams_members,
        lazy='subquery',
        backref=db.backref('members', lazy='dynamic'),
    )

    def __repr__(self):
        return f"Member('{self.name}', '{self.phone}', '{self.address}', '{self.psc}', '{self.city}')"


class ScoreTable(db.Model):
    __tablename__ = 'score_table'
    id = db.Column(db.Integer, primary_key=True)
    club = db.Column(db.String(250), nullable=False)
    logo = db.Column(db.Text, nullable=True)
    games = db.Column(db.Integer)
    wins = db.Column(db.Integer)
    draws = db.Column(db.Integer)
    loses = db.Column(db.Integer)
    score = db.Column(db.String(20), nullable=False)
    points = db.Column(db.Integer)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)


class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    produc_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer)
    amount = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_paid = db.Column(db.Boolean(), default=False)
    order_date = db.Column(db.DateTime, nullable=False, default=func.now())
    variants = db.Column(db.String(200), nullable=False)
    storno = db.Column(db.Boolean(), default=False)


class TypeProductVariant(db.Model):
    __tablename__ = 'type_product_variant'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    operation = db.Column(db.String(450), nullable=False)


class Sponsor(db.Model):
    __tablename__ = "sponsors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=True)
    describe = db.Column(db.Text, nullable=True)
    url = db.Column(db.String(255), nullable=True)
    kind = db.Column(db.String(20), nullable=False)      # 'main' alebo 'partner'
    image_file = db.Column(db.String(255), nullable=False)
    orderz = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)