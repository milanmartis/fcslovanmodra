
from flask import render_template, request, Blueprint
from app.models import Post, PostGallery, Category, Team, Event, ScoreTable
from flask import Blueprint
from app import db
from datetime import datetime, date 
from flask_security import current_user, roles_required
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey

from sqlalchemy.sql import func, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship


# from app.users.roles import user_role

main = Blueprint('main', __name__)

Base = declarative_base()

@main.route("/tabz")
def tabz():
    
        return render_template('tabz.html', current_date=datetime.now(), next22=Next.next(), teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())




@main.route("/")
@main.route("/home")
# @roles_required('Admin')
def home():
    print(current_user.is_authenticated)
    page = request.args.get('page', 1, type=int)
    # posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=3)
    
    # query = session.query(User, Address).join(Address, User.id == Address.user_id)
    
    posts = db.session.query(Post).join(PostGallery, Post.id == PostGallery.post_id).join(Category, Category.id == Post.category_id)\
    .filter(PostGallery.orderz<1).order_by(Post.date_posted.desc()).paginate(page=page, per_page=3)
    category = db.session.query(Category).all()
    # title_image = PostGallery.query.order_by(PostGallery.orderz.asc()).first()
    

  
    return render_template('home.html', title='', posts=posts, current_date=datetime.now(), next22=Next.next(), category=category, teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())


@main.route("/oklube")
def about():

    return render_template('about.html', title='About', current_date=datetime.now(), next22=Next.next(), teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())

@main.route("/dokumenty")
def dokumenty():

    return render_template('dokumenty.html', title='Dokumenty', current_date=datetime.now(), next22=Next.next(), teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())



@main.route("/sponsors")
def sponsors():
    
    return render_template('sponsors.html', title='Sponsors', current_date=datetime.now(), next22=Next.next(), teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())
# UPDATE your_table SET start_event = '2023-09-05 17:00:00', end_event = '2023-09-05 19:00:00'  WHERE id = 7;

# @main.route("/menu")
class Next:
    def next():
        today = func.now()  # Nastavenie aktuálneho dátumu a času
        engine = db.get_engine()
        Session = sessionmaker(bind=engine)
        session = Session()

        # Získanie 5 tímov zoradených podľa ID
        teams = session.query(Team.id, Team.name).order_by(Team.id.asc()).limit(6).all()
        
        next_events = []
        for team_id, team_name in teams:
            # Poddotaz na nájdenie najbližšieho eventu pre každý tím
            subquery = (session.query(
                    Event.event_team_id,
                    func.min(Event.start_event).label('min_start')
                )
                .filter(Event.start_event >= today)
                .filter(Event.event_team_id != 4) \
                .filter(Event.event_category_id == 1)
                .filter(Event.event_team_id == team_id)
                .group_by(Event.event_team_id)
                .subquery())

            # Hlavný dotaz pre získanie detailov o evente
            event = (session.query(Event)
                    .join(subquery, and_(
                        Event.event_team_id == subquery.c.event_team_id,
                        Event.start_event == subquery.c.min_start))
                    .order_by(Event.start_event.asc())
                    .first())

            if event:
                next_events.append(event)
            else:
                next_events.append(f"Bez údajov pre tím {team_name}")
        

        return next_events
        

class RightColumn:
    

    def main_menu():
        menuteam = db.session.query(Team).order_by(Team.id.asc()).all()
        return menuteam

    def next_match():
        today = datetime.today()
        next_match = db.session.query(Event.title, Event.start_event).filter(Event.start_event>=today).filter(Event.event_category_id==1).order_by(Event.start_event.asc()).all()
        return next_match

    def score_table():
        score_table = ScoreTable.query.all()
        return score_table





