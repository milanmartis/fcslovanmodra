
from flask import render_template, request, Blueprint
from app.models import Post, PostGallery, Category, Team
from flask import Blueprint
from app import db

main = Blueprint('main', __name__)



@main.route("/")
@main.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    # posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=3)
    posts = Post.query.join(PostGallery, Category).filter(
        Post.id == PostGallery.post_id).filter(Category.id == Post.category_id).filter(PostGallery.orderz<1).order_by(Post.date_posted.desc()).paginate(page=page, per_page=3)
    
    category = Category.query.all()
    
    return render_template('home.html', posts=posts, category=category)


@main.route("/about")
def about():
    return render_template('about.html', title='About', teamz=main_menu())


# @main.route("/menu")
def main_menu():
    menuteam = Team.query.all()
    if menuteam:
        return menuteam
    else:
        return ''




