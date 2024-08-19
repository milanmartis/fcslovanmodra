import boto3
import uuid
from app.config import Config
from botocore.exceptions import NoCredentialsError
import logging

from flask import (render_template, url_for, flash, jsonify,
                   redirect, request, abort, Blueprint, current_app, render_template)
from flask_login import current_user, login_required
from flask_security import roles_required

from app import db
from app.models import Post, Category, PostGallery
from app.posts.forms import PostForm, CategoryForm
from app.main.routes import RightColumn
from app.main.routes import Next
from flask import Blueprint
from werkzeug.utils import secure_filename
import secrets
from PIL import Image
from datetime import datetime
from dateutil import parser

import os
from sqlalchemy.orm import joinedload


posts = Blueprint('posts', __name__)

s3 = boto3.client(
    's3', region_name='eu-north-1',
    aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY
)
BUCKET_NAME = Config.AWS_S3_BUCKET
ALLOWED_EXTENSIONS = {'jpg', 'png'}
bucket_name = BUCKET_NAME

################  POSTS  #################

@posts.route("/posts", methods=['GET'])
def list_posts():
    page = request.args.get('page', 1, type=int)
    
    posts = db.session.query(Post).options(joinedload(Post.gallery)).join(PostGallery, Post.id == PostGallery.post_id).join(Category, Category.id == Post.category_id).filter(PostGallery.orderz < 1).order_by(Post.date_posted.desc()).paginate(page=page, per_page=3)
    
    category = Category.query.all()
    
    return render_template('home.html', posts=posts, category=category, current_date=datetime.now(), next22=Next.next(), teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@posts.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    form.category.choices = [(category.id, category.name) for category in Category.query.all()]
    if form.validate_on_submit():
        try:
            post = Post(title=form.title.data, content=form.content.data, date_posted=form.date_posted.data, author=current_user, category_id=form.category.data)
            db.session.add(post)
            db.session.commit()

            file = form.picture.data
            if file and allowed_file(file.filename):
                file_filename = secure_filename(file.filename)
                bucket_name = "fcsm-files"
                new_directory_name = 'posts/' + str(post.id) + '/gallery/'
                new_filename = uuid.uuid4().hex + '_' + file_filename
                s3_key = new_directory_name + new_filename
                s3.upload_fileobj(file, bucket_name, s3_key)
                picture = PostGallery(title=form.title.data, image_file2=new_filename, orderz=0, post_id=post.id)
                db.session.add(picture)
                db.session.commit()

            pictures = []
            for file in form.pictures.data:
                file_filename = secure_filename(file.filename)
                new_filename = uuid.uuid4().hex + '_' + file_filename
                s3_key = new_directory_name + new_filename
                s3.upload_fileobj(file, bucket_name, s3_key)
                picture = PostGallery(title=form.title.data, image_file2=new_filename, orderz=1, post_id=post.id)
                db.session.add(picture)
                pictures.append(new_filename)

            db.session.commit()
            flash('Your post has been created!', 'success')
            return redirect(url_for('main.home'))
        except Exception as e:
            db.session.rollback()
            flash('Chyba pri vytváraní príspevku. Skúste to znova.', 'danger')
        finally:
            db.session.remove()
    return render_template('posts/create_post.html', title='New Post',
                           form=form, legend='New Post', current_date=datetime.now(), next22=Next.next(), teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())


@posts.route("/post/<int:post_id>")
def post(post_id):
    title_image = PostGallery.query.filter(PostGallery.post_id == post_id).order_by(PostGallery.orderz.asc()).first()
    post = db.session.query(Post).options(joinedload(Post.gallery), joinedload(Post.author)).filter(Post.id == post_id).first()
    galleries = PostGallery.query.filter(PostGallery.post_id == post_id).order_by(PostGallery.orderz.asc()).all()
    category = Category.query.all()
    
    if post:
        title = post.title
    else:
        title = ''
    
    return render_template('posts/post.html', title_image=title_image, title=title, post=post, galleries=galleries, category=category, current_date=datetime.now(), next22=Next.next(), teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())


@posts.route("/posts/category/<int:category>")
@login_required
@roles_required('Admin', 'WebAdmin')
def category_posts(category):
    page = request.args.get('page', 1, type=int)
    category = Category.query.filter_by(id=category).first()
    posts = Post.query.filter(Post.category_id == category.id).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('posts/category_posts.html', posts=posts, category=category, current_date=datetime.now(), next22=Next.next(), teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())

def get_s3_image_url(orderz, post_id, image_file):
    folder = 'gallery/' if orderz == 0 else 'gallery/'
    return f'https://{Config.AWS_S3_BUCKET}.s3.amazonaws.com/posts/{post_id}/{folder}{image_file}'

@posts.route('/posts/images/<int:post_id>', methods=['GET'])
def get_images_by_post(post_id):
    images = PostGallery.query.filter_by(post_id=post_id).order_by(PostGallery.orderz.asc()).all()

    image_list = []
    for image in images:
        image_data = {
            'id': image.id,
            'title': image.title,
            'orderz': image.orderz,
            'image_url': get_s3_image_url(image.orderz, post_id, image.image_file2)
        }
        image_list.append(image_data)

    return jsonify(image_list)

@posts.route('/posts/images/<int:post_id>/upload', methods=['PUT'])
def upload_image(post_id):
    post = Post.query.get(post_id)
    new_directory_name2 = 'posts/' + str(post_id) + '/gallery/'

    file = request.files['image_file2']

    if file:
        file_filename = secure_filename(file.filename)
        file_basename, file_extension = os.path.splitext(file_filename)
        new_filename = uuid.uuid4().hex + '_' + file_basename + file_extension
        s3_key = new_directory_name2 + new_filename
        s3.upload_fileobj(file, Config.AWS_S3_BUCKET, s3_key)
        existing_images_count = PostGallery.query.filter_by(post_id=post.id).count()
        new_orderz = existing_images_count if existing_images_count == 0 else existing_images_count + 1

        picture = PostGallery(title='', image_file2=new_filename, orderz=new_orderz, post_id=post.id)
        db.session.add(picture)
        db.session.commit()

        return jsonify({"message": "Image uploaded successfully"})

    return jsonify({"error": "Failed to upload image"}), 500

@posts.route('/posts/<post_id>/gallery/delete/<image_id>', methods=['DELETE'])
@roles_required('Admin', 'WebAdmin')
def delete_image(post_id, image_id):
    try:
        image = PostGallery.query.filter_by(id=image_id).first()
        s3.delete_object(Bucket=Config.AWS_S3_BUCKET, Key=f"posts/{post_id}/gallery/{image.image_file2}")
        db.session.delete(image)
        db.session.commit()
        
        return jsonify({"message": "Obrázok bol úspešne vymazaný"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@posts.route('/posts/<int:post_id>/gallery/update_order', methods=['POST'])
def update_image_order(post_id):
    data = request.json
    for image in data:
        new_order_image = PostGallery.query.get(image['image_id'])
        new_order_image.orderz = image['orderz']
    
    db.session.commit()

    return jsonify({"message": "Image order updated successfully"})

@posts.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
@roles_required('Admin', 'WebAdmin')
def update_post(post_id):
    try:
        post = Post.query.get(post_id)
        image = PostGallery.query.filter(PostGallery.post_id == post_id).filter(PostGallery.orderz == 0).first()
        image_url = get_s3_image_url('', post_id, image.image_file2) if image else ''
        if post.author != current_user:
            abort(403)
        form = PostForm()
        form.category.choices = [(category.id, category.name) for category in Category.query.all()]
        if form.validate_on_submit():
            post.title = form.title.data
            post.content = form.content.data
            post.date_posted = form.date_posted.data
            post.category_id = form.category.data
            db.session.commit()
            
            flash('Your post has been updated!', 'success')
            return redirect(url_for('posts.post', post_id=post.id))
        
        elif request.method == 'GET':
            form.title.data = post.title
            form.content.data = post.content
            form.date_posted.data = post.date_posted
            form.category.data = post.category_id
        return render_template('posts/update_post.html', title='Update Post',
                            image=image, image_url=image_url, post=post, form=form, post_id=post_id, legend='Update Post', current_date=datetime.now(), next22=Next.next(), teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())
    except Exception as e:
        db.session.rollback()
        flash('Chyba pri aktualizácii príspevku. Skúste to znova.', 'danger')
    finally:
        db.session.remove()

@posts.route('/post/files/<int:post_id>/upload', methods=['POST'])
def upload_file(post_id):
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        new_directory_name2 = 'posts/' + str(post_id) + '/'
        new_filename = uuid.uuid4().hex + '_' + filename.rsplit('.', 1)[0] + '.' + filename.rsplit('.', 1)[1].lower()
        s3_key = new_directory_name2 + new_filename
        s3.upload_fileobj(file, BUCKET_NAME, s3_key)

    post = Post.query.get_or_404(post_id)
    postgal = PostGallery.query.filter(PostGallery.post_id == post_id).first()
    if not postgal:
        postgal = PostGallery(title=post.title, image_file2=filename, orderz=0, post_id=post_id)
        db.session.add(postgal)
        db.session.commit()
        
    else:
        postgal.image_file2 = filename
        db.session.commit()
        
        return jsonify(message="File uploaded successfully", image_file2=filename)
    return jsonify(message="Upload failed"), 400

@posts.route('/post/files/<int:post_id>/delete_file', methods=['POST'])
def delete_file(post_id):
    post = PostGallery.query.filter(PostGallery.post_id == post_id).first()
    if post.image_file2:
        s3.delete_object(Bucket=BUCKET_NAME, Key=post.image_file2)
        db.session.delete(post)
        db.session.commit()
        return jsonify(message="File deleted successfully", file_path=None)
    return jsonify(message="No file to delete"), 400

@posts.route("/post/<int:post_id>/delete", methods=['POST', 'GET'])
@login_required
@roles_required('Admin', 'WebAdmin')
def delete_post(post_id):
    try:
        postgall = PostGallery.query.filter_by(post_id=post_id).all()
        for gal in postgall:
            pg = PostGallery.query.get(gal.id)
            db.session.delete(pg)

        post = Post.query.get_or_404(post_id)
        if post.author != current_user:
            abort(403)
        db.session.delete(post)
        db.session.commit()
        flash('Your post has been deleted!', 'success')
        return redirect(url_for('main.home'))
    except Exception as e:
        db.session.rollback()
        flash('Chyba pri mazaní príspevku. Skúste to znova.', 'danger')
    finally:
        db.session.remove()

################  CATEGORIES  #################

@posts.route("/categories")
@login_required
@roles_required('Admin', 'WebAdmin')
def list_categories():
    page = request.args.get('page', 1, type=int)
    categories = Category.query.order_by(Category.id.desc()).paginate(page=page, per_page=5)
    return render_template('posts/list_categories.html', categories=categories, current_date=datetime.now(), next22=Next.next(), teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())

@posts.route("/category/new", methods=['GET', 'POST'])
@login_required
@roles_required('Admin', 'WebAdmin')
def new_category():
    form = CategoryForm()
    if form.validate_on_submit():
        try:
            category = Category(name=form.name.data)
            db.session.add(category)
            db.session.commit()
            flash('Your category has been created!', 'success')
            return redirect(url_for('posts.list_categories'))
        except Exception as e:
            db.session.rollback()
            flash('Chyba pri vytváraní kategórie. Skúste to znova.', 'danger')
        finally:
            db.session.remove()
    return render_template('posts/create_category.html', title='New Post Category',
                           form=form, legend='New Post Category', current_date=datetime.now(), next22=Next.next(), teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())

@posts.route("/category/<int:category_id>")
def category(category_id):
    category = Category.query.get(category_id)
    return render_template('posts/category.html', name=category.name, category=category, current_date=datetime.now(), next22=Next.next(), teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())

@posts.route("/category/<int:category_id>/update", methods=['GET', 'POST'])
@login_required
@roles_required('Admin', 'WebAdmin')
def update_category(category_id):
    try:
        category = Category.query.get_or_404(category_id)
        form = CategoryForm()
        if form.validate_on_submit():
            category.name = form.name.data
            db.session.commit()
            flash('A category has been updated!', 'success')
            return redirect(url_for('posts.list_categories', category_id=category.id))
        elif request.method == 'GET':
            form.name.data = category.name
        return render_template('posts/create_category.html', title='Update Category',
                            form=form, legend='Update Category', current_date=datetime.now(), next22=Next.next(), teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())
    except Exception as e:
        db.session.rollback()
        flash('Chyba pri aktualizácii kategórie. Skúste to znova.', 'danger')
    finally:
        db.session.remove()

@posts.route("/category/<int:category_id>/delete", methods=['POST'])
@login_required
@roles_required('Admin', 'WebAdmin')
def delete_category(category_id):
    try:
        category = Category.query.get(category_id)
        db.session.delete(category)
        db.session.commit()
        flash('A category has been deleted!', 'success')
        return redirect(url_for('posts.list_categories'))
    except Exception as e:
        db.session.rollback()
        flash('Chyba pri mazaní kategórie. Skúste to znova.', 'danger')
    finally:
        db.session.remove()
