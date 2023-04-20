
from flask import render_template, request, Blueprint
from app.models import Post, PostGallery, Category, Team, Event, ScoreTable
from flask import Blueprint
from app import db
# from app.users.roles import user_role

main = Blueprint('main', __name__)



@main.route("/")
@main.route("/home")
def home():
    # print(user_role())
    page = request.args.get('page', 1, type=int)
    # posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=3)
    posts = Post.query.join(PostGallery, Category).filter(
        Post.id == PostGallery.post_id).filter(Category.id == Post.category_id).filter(PostGallery.orderz<1).order_by(Post.date_posted.desc()).paginate(page=page, per_page=3)
    
    category = Category.query.all()
    
    return render_template('home.html', posts=posts, category=category, teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())


@main.route("/about")
def about():
    return render_template('about.html', title='About', teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())



@main.route("/sponsors")
def sponsors():
    return render_template('sponsors.html', title='Sponsors', teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())


# @main.route("/menu")
class RightColumn:
    def main_menu():
        menuteam = Team.query.all()
        return menuteam

    def next_match():
        next_match = db.session.query(Event).filter(Event.event_team_id==1).order_by(Event.start_event.asc()).first()
        print(next_match)
        return next_match

    def score_table():
        score_table = ScoreTable.query.all()
        return score_table





