import os
import re
import uuid
from datetime import datetime
import mimetypes
from sqlalchemy.orm import subqueryload, joinedload
from app import csrf
from slugify import slugify
import boto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import NoCredentialsError
from flask import (
    Blueprint, abort, current_app, flash, jsonify,
    redirect, render_template, request, url_for
)
# from flask_login import current_user, login_required
# from flask_security import roles_required
from sqlalchemy.orm import joinedload
from werkzeug.utils import secure_filename

from app import db
from app.config import Config
from app.main.routes import Next, RightColumn
from app.models import Category, Post, PostGallery
from app.posts.forms import PostForm, CategoryForm
from flask_login import login_user, current_user, logout_user, login_required
from functools import wraps

def roles_required(*roles):
    def deco(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if not current_user.has_role(*roles):
                abort(403)
            return fn(*args, **kwargs)
        return wrapper
    return deco

posts = Blueprint('posts', __name__)

# ---------- AWS S3 klient (autodetekcia regiónu + s3v4 podpis) ----------

AWS_ACCESS_KEY_ID     = (Config.AWS_ACCESS_KEY_ID or "").strip()
AWS_SECRET_ACCESS_KEY = (Config.AWS_SECRET_ACCESS_KEY or "").strip()
BUCKET_NAME           = (Config.AWS_S3_BUCKET or "").strip()

_BUCKET_RE = re.compile(r'^[a-zA-Z0-9.\-_]{1,255}$')
if not _BUCKET_RE.match(BUCKET_NAME):
    raise RuntimeError(f"Invalid S3 bucket name: {repr(BUCKET_NAME)}")

_S3 = None
_S3_REGION = None

import mimetypes

def s3_extra_args(file):
    content_type, _ = mimetypes.guess_type(getattr(file, "filename", "") or "")

    if not content_type:
        fn = (getattr(file, "filename", "") or "").lower()
        if fn.endswith(".mp4"):
            content_type = "video/mp4"
        elif fn.endswith(".webp"):
            content_type = "image/webp"
        elif fn.endswith(".png"):
            content_type = "image/png"
        elif fn.endswith(".gif"):
            content_type = "image/gif"
        else:
            content_type = "image/jpeg"

    return {
        "ContentType": content_type,
        "CacheControl": "public, max-age=31536000, immutable",
    }
    
def s3_client():
    """Vráti inicializovaný boto3 s3 client v reálnom regióne bucketu."""
    global _S3, _S3_REGION
    if _S3:
        return _S3
    probe = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )
    loc = probe.get_bucket_location(Bucket=BUCKET_NAME)
    _S3_REGION = loc.get("LocationConstraint") or "us-east-1"
    _S3 = boto3.client(
        "s3",
        region_name=_S3_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        config=BotoConfig(signature_version="s3v4"),
    )
    return _S3

def s3_public_url(key: str) -> str:
    region = _S3_REGION or "us-east-1"
    return f"https://{BUCKET_NAME}.s3.{region}.amazonaws.com/{key}"


def s3_presign(key: str, expires: int = 3600) -> str:
    return s3_client().generate_presigned_url(
        "get_object",
        Params={"Bucket": BUCKET_NAME, "Key": key},
        
        ExpiresIn=expires,
    )


# ---------- Helpers ----------

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp', 'mp4'}

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def make_gallery_key(post_id: int, filename: str) -> str:
    return f'posts/{post_id}/gallery/{filename}'


# ---------- POSTS ----------

@posts.route("/posts", methods=['GET'])
def list_posts():
    page = request.args.get('page', 1, type=int)

    posts_paginated = (
        db.session.query(Post)
        .options(joinedload(Post.gallery))
        .join(PostGallery, Post.id == PostGallery.post_id)
        .join(Category, Category.id == Post.category_id)
        .filter(PostGallery.orderz < 1)           # len titulné
        .order_by(Post.date_posted.desc())
        .paginate(page=page, per_page=3)
    )

    category = Category.query.all()

    return render_template(
        'home.html',
        posts=posts_paginated,
        category=category,
        current_date=datetime.now(),
        next22=Next.next(),
        teamz=RightColumn.main_menu(),
        next_match=RightColumn.next_match(),
        score_table=RightColumn.score_table()
    )


@posts.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    form.category.choices = [(c.id, c.name) for c in Category.query.all()]

    if form.validate_on_submit():
        try:
            # 1) vytvor Post (napojenie cez relationship 'author', nie author_id)
            base_slug = slugify(form.title.data)
            slug = base_slug
            i = 1

            while Post.query.filter_by(slug=slug).first():
                slug = f"{base_slug}-{i}"
                i += 1

            post = Post(
                title=form.title.data,
                slug=slug,
                content=form.content.data,
                date_posted=form.date_posted.data,
                author=current_user,
                category_id=form.category.data
            )
            db.session.add(post)
            db.session.flush()   # potrebujeme post.id pred uploadom

            # 2) titulná fotka (orderz=0)
            file = getattr(form, 'picture', None).data if hasattr(form, 'picture') else None
            if file and getattr(file, 'filename', '') and allowed_file(file.filename):
                original = secure_filename(file.filename)
                base, ext = os.path.splitext(original)
                new_filename = f'{uuid.uuid4().hex}_{base}{ext.lower()}'
                s3_key = make_gallery_key(post.id, new_filename)
                s3_client().upload_fileobj(
                    file,
                    BUCKET_NAME,
                    s3_key,
                    ExtraArgs=s3_extra_args(file),

                )

                db.session.add(PostGallery(
                    title=form.title.data or '',
                    image_file2=new_filename,
                    orderz=0,
                    post_id=post.id
                ))

            # 3) ďalšie fotky (orderz 1,2,3…)
            pictures_field = getattr(form, 'pictures', None)
            if pictures_field and pictures_field.data:
                existing = PostGallery.query.filter_by(post_id=post.id).count()
                order_counter = existing if existing > 0 else 1  # ak titulka existuje, ďalšie od 1
                for f in pictures_field.data:
                    if not f or not getattr(f, 'filename', '') or not allowed_file(f.filename):
                        continue
                    original = secure_filename(f.filename)
                    base, ext = os.path.splitext(original)
                    new_filename = f'{uuid.uuid4().hex}_{base}{ext.lower()}'
                    s3_key = make_gallery_key(post.id, new_filename)
                    s3_client().upload_fileobj(
                        f,
                        BUCKET_NAME,
                        s3_key,
                        ExtraArgs=s3_extra_args(f),

                    )
                    db.session.add(PostGallery(
                        title=form.title.data or '',
                        image_file2=new_filename,
                        orderz=order_counter,
                        post_id=post.id
                    ))
                    order_counter += 1

            db.session.commit()
            flash('Your post has been created!', 'success')
            return redirect(url_for('main.home'))

        except Exception as e:
            current_app.logger.exception("Error in new_post: %s", e)
            db.session.rollback()
            flash('Chyba pri vytváraní príspevku. Skontroluj S3 bucket, región a kľúče.', 'danger')
            return redirect(url_for('posts.new_post'))

    return render_template(
        'posts/create_post.html',
        title='New Post',
        form=form,
        legend='New Post',
        current_date=datetime.now(),
        next22=Next.next(),
        teamz=RightColumn.main_menu(),
        next_match=RightColumn.next_match(),
        score_table=RightColumn.score_table()
    )


@posts.route("/post/<int:post_id>")
def post(post_id):
    post_obj = (
        db.session.query(Post)
        .options(joinedload(Post.gallery), joinedload(Post.author))
        .filter(Post.id == post_id)
        .first()
    )
    if not post_obj:
        abort(404)

    # ===== Views +1 (pre Najčítanejšie) =====
    db.session.query(Post).filter(Post.id == post_id).update({
        Post.views: Post.views + 1
    })
    db.session.commit()
    db.session.refresh(post_obj)

    # ===== Titulný obrázok + galéria (tvoj kód) =====
    title_image = (
        PostGallery.query
        .filter_by(post_id=post_id)
        .order_by(PostGallery.orderz.asc())
        .first()
    )

    galleries = (
        PostGallery.query
        .filter_by(post_id=post_id)
        .order_by(PostGallery.orderz.asc())
        .all()
    )

    title_image_url = None
    if title_image:
        title_image_url = s3_public_url(
            make_gallery_key(post_id, title_image.image_file2)
        )

    galleries_with_urls = []
    for g in galleries:
        ext = (os.path.splitext(g.image_file2 or "")[1] or "").lower()
        media_type = "video" if ext == ".mp4" else "image"

        galleries_with_urls.append({
            "id": g.id,
            "title": g.title,
            "orderz": g.orderz,
            "media_type": media_type,
            "url": s3_public_url(make_gallery_key(post_id, g.image_file2)),
            "image_file2": g.image_file2,
        })

    category = Category.query.all()

    # =====================================================
    # 🔥 NAJČÍTANEJŠIE – PRE TVOJ EXISTUJÚCI BLOK
    # =====================================================
    most_read = (
        Post.query
        .filter(Post.id != post_id)
        .order_by(Post.views.desc(), Post.date_posted.desc())
        .limit(6)
        .all()
    )

    # ===== Cover obrázky pre Najčítanejšie =====
    most_read_ids = [p.id for p in most_read]
    most_read_covers = {}

    if most_read_ids:
        cover_rows = (
            PostGallery.query
            .filter(PostGallery.post_id.in_(most_read_ids))
            .order_by(PostGallery.post_id.asc(), PostGallery.orderz.asc())
            .all()
        )

        # prvý obrázok podľa orderz = titulný
        for g in cover_rows:
            if g.post_id not in most_read_covers and g.image_file2:
                most_read_covers[g.post_id] = s3_public_url(
                    make_gallery_key(g.post_id, g.image_file2)
                )

    # (voliteľné – pripravené do budúcna)
    latest_posts = (
        Post.query
        .filter(Post.id != post_id)
        .order_by(Post.date_posted.desc())
        .limit(6)
        .all()
    )

    return render_template(
        "posts/post.html",
        title_image=title_image,
        title_image_url=title_image_url,
        title=post_obj.title,
        post=post_obj,
        galleries=galleries_with_urls,
        category=category,

        # 👇 PRESNE TOTO TVOJA ŠABLÓNA POTREBUJE
        most_read=most_read,
        most_read_covers=most_read_covers,
        latest_posts=latest_posts,  # zatiaľ nepoužívaš, ale je ready

        current_date=datetime.now(),
        next22=Next.next(),
        teamz=RightColumn.main_menu(),
        next_match=RightColumn.next_match(),
        score_table=RightColumn.score_table()
    )


@posts.route("/posts/category/<int:category>")
# @login_required
# @roles_required('Admin', 'WebAdmin')
def category_posts(category):
    page = request.args.get('page', 1, type=int)
    category_obj = Category.query.filter_by(id=category).first_or_404()
    posts_paginated = (
        Post.query
        .options(subqueryload(Post.gallery))  # <--- pridaj
        .filter(Post.category_id == category_obj.id)
        .order_by(Post.date_posted.desc())
        .paginate(page=page, per_page=5)
    )
    return render_template(
        'posts/category_posts.html',
        posts=posts_paginated,
        category=category_obj,
        current_date=datetime.now(),
        next22=Next.next(),
        teamz=RightColumn.main_menu(),
        next_match=RightColumn.next_match(),
        score_table=RightColumn.score_table()
    )


# ---------- Galéria API ----------

@posts.route('/posts/images/<int:post_id>', methods=['GET'])
@csrf.exempt
def get_images_by_post(post_id):
    images = (
        PostGallery.query
        .filter_by(post_id=post_id)
        .order_by(PostGallery.orderz.asc())
        .all()
    )

    # Vraciame pre-signed URL priamo v JSON (frontend to môže rovno použiť)
    image_list = []
    for img in images:
        key = make_gallery_key(post_id, img.image_file2)
        ext = (os.path.splitext(img.image_file2 or "")[1] or "").lower()
        media_type = "video" if ext == ".mp4" else "image"
        image_list.append({
              "id": img.id,
              "title": img.title,
              "orderz": img.orderz,
              "media_type": media_type,
              "url": s3_public_url(key),     # ✅ neutrálny názov
              "filename": img.image_file2
        })

    return jsonify(image_list)


@posts.route('/posts/images/<int:post_id>/upload', methods=['PUT'])
@csrf.exempt
def upload_image(post_id):
    post = Post.query.get_or_404(post_id)
    file = request.files.get('image_file2')

    if not file or not getattr(file, 'filename', '') or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file"}), 400

    original = secure_filename(file.filename)
    base, ext = os.path.splitext(original)
    new_filename = f'{uuid.uuid4().hex}_{base}{ext.lower()}'
    s3_key = make_gallery_key(post_id, new_filename)
    s3_client().upload_fileobj(
        file,
        BUCKET_NAME,
        s3_key,
        ExtraArgs=s3_extra_args(file)

    )

    existing_count = PostGallery.query.filter_by(post_id=post.id).count()
    new_orderz = existing_count  # 0,1,2,...

    db.session.add(PostGallery(
        title='',
        image_file2=new_filename,
        orderz=new_orderz,
        post_id=post.id
    ))
    db.session.commit()

    return jsonify({"message": "Image uploaded successfully"})


@posts.route('/posts/<int:post_id>/gallery/delete/<int:image_id>', methods=['DELETE'])
@csrf.exempt
@roles_required('Admin', 'WebAdmin')
def delete_image(post_id, image_id):
    image = PostGallery.query.filter_by(id=image_id, post_id=post_id).first_or_404()
    try:
        s3_client().delete_object(Bucket=BUCKET_NAME, Key=make_gallery_key(post_id, image.image_file2))
    except Exception as e:
        current_app.logger.warning("S3 delete failed: %s", e)

    db.session.delete(image)
    db.session.commit()
    return jsonify({"message": "Obrázok bol úspešne vymazaný"})


@posts.route('/posts/<int:post_id>/gallery/update_order', methods=['POST'])
@csrf.exempt
def update_image_order(post_id):
    data = request.json or []
    # očakáva zoznam dictov: {"image_id": X, "orderz": Y}
    ids = [it.get('image_id') for it in data if 'image_id' in it]
    if not ids:
        return jsonify({"message": "No data"}), 400

    images = {img.id: img for img in PostGallery.query.filter(PostGallery.id.in_(ids)).all()}

    for item in data:
        img = images.get(item.get('image_id'))
        if img and img.post_id == post_id:
            img.orderz = int(item.get('orderz', img.orderz))

    db.session.commit()
    return jsonify({"message": "Image order updated successfully"})


# ---------- Update / Upload file (single) ----------

from app.posts.utils import upload_post_file_to_s3  # <-- NOVÉ


# ---------- Update / Upload file (single) ----------

@posts.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
@roles_required('Admin', 'WebAdmin')
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    image = (
        PostGallery.query
        .filter_by(post_id=post_id, orderz=0)
        .first()
    )
    image_url = s3_public_url(make_gallery_key(post_id, image.image_file2)) if image else ''

    if post.author != current_user:
        abort(403)

    form = PostForm()
    form.category.choices = [(c.id, c.name) for c in Category.query.all()]

    if form.validate_on_submit():
        try:
            post.title = form.title.data
            post.content = form.content.data
            post.date_posted = form.date_posted.data
            post.category_id = form.category.data
            db.session.commit()
            flash('Your post has been updated!', 'success')
            return redirect(url_for('posts.post', post_id=post.id))
        except Exception as e:
            current_app.logger.exception("Error in update_post: %s", e)
            db.session.rollback()
            flash('Chyba pri aktualizácii príspevku. Skúste to znova.', 'danger')
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
        form.date_posted.data = post.date_posted
        form.category.data = post.category_id

    return render_template(
        'posts/update_post.html',
        title='Update Post',
        image=image,
        image_url=image_url,  # pre-signed URL na náhľad
        post=post,
        form=form,
        post_id=post_id,
        legend='Update Post',
        current_date=datetime.now(),
        next22=Next.next(),
        teamz=RightColumn.main_menu(),
        next_match=RightColumn.next_match(),
        score_table=RightColumn.score_table()
    )


@posts.route('/post/files/<int:post_id>/upload', methods=['POST'])
def upload_file(post_id):
    file = request.files.get('file')
    if not file or not getattr(file, 'filename', ''):
        flash('No file selected')
        return redirect(request.url)

    if not allowed_file(file.filename):
        flash('File type not allowed')
        return redirect(request.url)

    # Upload do S3 (obrázky zmenší + webp, iné nechá pôvodne)
    new_filename, s3_key = upload_post_file_to_s3(
        file=file,
        post_id=post_id,
        bucket_name=BUCKET_NAME,
        make_gallery_key=make_gallery_key,
        s3_client=s3_client,
        s3_extra_args=s3_extra_args,
        max_size=(1600, 1600),   # <- nastav si (napr. 1200,1200 pre cover)
        quality=82
    )

    post = Post.query.get_or_404(post_id)
    postgal = PostGallery.query.filter_by(post_id=post_id, orderz=0).first()
    if not postgal:
        postgal = PostGallery(
            title=post.title or '',
            image_file2=new_filename,
            orderz=0,
            post_id=post_id
        )
        db.session.add(postgal)
    else:
        postgal.image_file2 = new_filename

    db.session.commit()

    return jsonify(message="File uploaded successfully", image_file2=new_filename)


@posts.route('/post/files/<int:post_id>/delete_file', methods=['POST'])
def delete_file(post_id):
    postgal = PostGallery.query.filter_by(post_id=post_id, orderz=0).first_or_404()
    if postgal.image_file2:
        try:
            s3_client().delete_object(Bucket=BUCKET_NAME, Key=make_gallery_key(post_id, postgal.image_file2))
        except Exception as e:
            current_app.logger.warning("S3 delete failed: %s", e)

        db.session.delete(postgal)
        db.session.commit()
        return jsonify(message="File deleted successfully", file_path=None)

    return jsonify(message="No file to delete"), 400


@posts.route("/post/<int:post_id>/delete", methods=['POST', 'GET'])
@csrf.exempt
@login_required
@roles_required('Admin', 'WebAdmin')
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)

    galleries = PostGallery.query.filter_by(post_id=post_id).all()
    for g in galleries:
        try:
            s3_client().delete_object(Bucket=BUCKET_NAME, Key=make_gallery_key(post_id, g.image_file2))
        except Exception as e:
            current_app.logger.warning("S3 delete failed: %s", e)
        db.session.delete(g)

    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('main.home'))


# ---------- CATEGORIES ----------

@posts.route("/categories")
@login_required
@roles_required('Admin', 'WebAdmin')
def list_categories():
    page = request.args.get('page', 1, type=int)
    categories = Category.query.order_by(Category.id.desc()).paginate(page=page, per_page=5)
    return render_template(
        'posts/list_categories.html',
        categories=categories,
        current_date=datetime.now(),
        next22=Next.next(),
        teamz=RightColumn.main_menu(),
        next_match=RightColumn.next_match(),
        score_table=RightColumn.score_table()
    )


@posts.route("/category/<int:category_id>")
def category(category_id):
    category_obj = Category.query.get_or_404(category_id)
    return render_template(
        'posts/category.html',
        name=category_obj.name,
        category=category_obj,
        current_date=datetime.now(),
        next22=Next.next(),
        teamz=RightColumn.main_menu(),
        next_match=RightColumn.next_match(),
        score_table=RightColumn.score_table()
    )


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
            current_app.logger.exception("Error in new_category: %s", e)
            db.session.rollback()
            flash('Chyba pri vytváraní kategórie. Skúste to znova.', 'danger')

    return render_template(
        'posts/create_category.html',
        title='New Post Category',
        form=form,
        legend='New Post Category',
        current_date=datetime.now(),
        next22=Next.next(),
        teamz=RightColumn.main_menu(),
        next_match=RightColumn.next_match(),
        score_table=RightColumn.score_table()
    )

@posts.route("/category/<int:category_id>/update", methods=['GET', 'POST'])
@login_required
@roles_required('Admin', 'WebAdmin')
def update_category(category_id):
    category_obj = Category.query.get_or_404(category_id)
    form = CategoryForm()
    if form.validate_on_submit():
        try:
            category_obj.name = form.name.data
            db.session.commit()
            flash('A category has been updated!', 'success')
            return redirect(url_for('posts.list_categories'))
        except Exception as e:
            current_app.logger.exception("Error in update_category: %s", e)
            db.session.rollback()
            flash('Chyba pri aktualizácii kategórie. Skúste to znova.', 'danger')
    elif request.method == 'GET':
        form.name.data = category_obj.name

    return render_template(
        'posts/create_category.html',
        title='Update Category',
        form=form,
        legend='Update Category',
        current_date=datetime.now(),
        next22=Next.next(),
        teamz=RightColumn.main_menu(),
        next_match=RightColumn.next_match(),
        score_table=RightColumn.score_table()
    )


@posts.route("/category/<int:category_id>/delete", methods=['POST'])
@login_required
@roles_required('Admin', 'WebAdmin')
def delete_category(category_id):
    category_obj = Category.query.get_or_404(category_id)
    try:
        db.session.delete(category_obj)
        db.session.commit()
        flash('A category has been deleted!', 'success')
        return redirect(url_for('posts.list_categories'))
    except Exception as e:
        current_app.logger.exception("Error in delete_category: %s", e)
        db.session.rollback()
        flash('Chyba pri mazaní kategórie. Skúste to znova.', 'danger')
        return redirect(url_for('posts.list_categories'))
