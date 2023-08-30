
from flask import render_template, request, Blueprint
from app.models import Post, PostGallery, Category, Team, Event, ScoreTable
from flask import Blueprint
from app import db
from datetime import date
from flask_security import current_user, roles_accepted 

# from app.users.roles import user_role

main = Blueprint('main', __name__)


@main.route("/tabz")
def tabz():
    
        return render_template('tabz.html', next22=Next.next(), teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())




@main.route("/")
@main.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    # posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=3)
    
    # query = session.query(User, Address).join(Address, User.id == Address.user_id)
    
    posts = db.session.query(Post).join(PostGallery, Post.id == PostGallery.post_id).join(Category, Category.id == Post.category_id).order_by(Post.date_posted.desc()).paginate(page=page, per_page=3)
    
    category = db.session.query(Category).all()
    
  
    return render_template('home.html', title='Main', posts=posts, next22=Next.next(), category=category, teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())


@main.route("/about")
def about():

    return render_template('about.html', title='About', next22=Next.next(), teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())



@main.route("/sponsors")
def sponsors():
    
    return render_template('sponsors.html', title='Sponsors', next22=Next.next(), teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())
# UPDATE your_table SET start_event = '2023-09-05 17:00:00', end_event = '2023-09-05 19:00:00'  WHERE id = 7;

# @main.route("/menu")
class Next:
    def next():
        today = date.today()
        # print('kjj')
        next = Event.query.filter(Event.event_team_id==1).filter(Event.event_category_id==1).filter(Event.start_event>today).order_by(Event.start_event.asc()).first()
        # print(next)
        return next
        


class RightColumn:
    def main_menu():
        menuteam = db.session.query(Team).order_by(Team.id.asc()).all()
        return menuteam

    def next_match():
        next_match = db.session.query(Event.title, Event.start_event).filter(Event.event_team_id==1).order_by(Event.start_event.asc()).first()
        return next_match

    def score_table():
        score_table = ScoreTable.query.all()
        return score_table





