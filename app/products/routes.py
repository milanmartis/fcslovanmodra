# app/products/routes.py

import os
import uuid
from datetime import datetime
from app import csrf
import stripe
from sqlalchemy import text
from werkzeug.utils import secure_filename
from flask import (
    Blueprint, abort, current_app, flash, jsonify,
    redirect, render_template, request, url_for
)
from flask_login import current_user, login_required
from flask_security import roles_required

from app import db
from app.aws_utils import s3_client, s3_presign, s3_extra_args, make_product_key
from app.main.routes import Next, RightColumn
from app.models import (
    Event, Order, Product, ProductCategory, ProductGallery,
    ProductVariant, variant_products
)
from app.products.forms import ProductCategoryForm, ProductForm, PurchaseForm
import re

products = Blueprint("products", __name__)

YOUTUBE_ID_RE = re.compile(
    r"(?:youtu\.be/|youtube\.com/(?:watch\?v=|embed/|shorts/))([A-Za-z0-9_-]{6,})"
)

def extract_youtube_id(url: str) -> str | None:
    if not url:
        return None
    url = url.strip()

    # ak už user vložil priamo ID
    if re.fullmatch(r"[A-Za-z0-9_-]{6,}", url):
        return url

    m = YOUTUBE_ID_RE.search(url)
    return m.group(1) if m else None


# ------------------------------
# Helpers
# ------------------------------
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}

def alowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def _upload_product_image(product_id: int, file_storage) -> str:
    """
    Uploadne file do S3 a vráti nový filename (uložený do DB).
    """
    original = secure_filename(file_storage.filename)
    base, ext = os.path.splitext(original)
    new_filename = f"{uuid.uuid4().hex}_{base}{ext.lower()}"
    key = make_product_key(product_id, new_filename)

    s3_client().upload_fileobj(
        file_storage,
        current_app.config["AWS_S3_BUCKET"],
        key,
        ExtraArgs=s3_extra_args(file_storage),
    )
    return new_filename


def _delete_product_image_from_s3(product_id: int, filename: str) -> None:
    """
    Skúsi vymazať objekt v S3. Ak failne, len zaloguje.
    """
    try:
        s3_client().delete_object(
            Bucket=current_app.config["AWS_S3_BUCKET"],
            Key=make_product_key(product_id, filename),
        )
    except Exception as e:
        current_app.logger.warning("S3 delete failed: %s", e)


# ------------------------------
# PRODUCTS list
# ------------------------------
@products.route("/products", methods=["GET"])
def list_products():
    products_list = (
        db.session.query(Product)
        .filter(Product.is_visible.is_(True))
        .order_by(Product.date_posted.desc())
        .all()
    )

    product_category = ProductCategory.query.all()

    bought_product_ids = set()
    if current_user.is_authenticated:
        user_orders = Order.query.filter_by(user_id=current_user.id, is_paid=True).all()
        bought_product_ids = {o.produc_id for o in user_orders}

    # cover_map: product_id -> presigned url (orderz=0)
    cover_map = {}
    if products_list:
        covers = (
            ProductGallery.query
            .filter(ProductGallery.product_id.in_([p.id for p in products_list]))
            .filter(ProductGallery.orderz == 0)
            .all()
        )
        for c in covers:
            cover_map[c.product_id] = s3_presign(make_product_key(c.product_id, c.image_file2))

    return render_template(
        "products/products.html",
        products=products_list,
        product_category=product_category,
        bought_product_ids=bought_product_ids,
        cover_map=cover_map,
        current_date=datetime.now(),
        next22=Next.next(),
        teamz=RightColumn.main_menu(),
        next_match=RightColumn.next_match(),
        score_table=RightColumn.score_table(),
    )


# ------------------------------
# NEW product (Admin)
# ------------------------------
@products.route("/product/new", methods=["GET", "POST"])
@login_required
@roles_required("Admin")
def new_product():
    form = ProductForm()
    form.category.choices = [(c.id, c.name) for c in ProductCategory.query.all()]

    if form.validate_on_submit():
        try:
            product = Product(
                title=form.title.data,
                content=form.content.data,
                saler=current_user,
                product_category_id=form.category.data,
                price=form.price.data,
                stripe_link=form.stripe_link.data,
                youtube_link=extract_youtube_id(form.youtube_link.data or "") or "",
                old_price=form.old_price.data,
                is_visible=form.is_visible.data,
            )
            db.session.add(product)
            db.session.flush()  # aby sme mali product.id pred uploadom

            # titulka (orderz=0)
            cover = getattr(form, "picture", None).data if hasattr(form, "picture") else None
            if cover and getattr(cover, "filename", ""):
                if not alowed_file(cover.filename):
                    db.session.rollback()
                    flash("Nepodporovaný typ súboru (len jpg/jpeg/png).", "danger")
                    return redirect(url_for("products.new_product"))

                fn = _upload_product_image(product.id, cover)
                db.session.add(ProductGallery(
                    title=product.title or "",
                    image_file2=fn,
                    orderz=0,
                    product_id=product.id,
                ))

            # ďalšie obrázky (orderz=1,2,3…)
            pics_field = getattr(form, "pictures", None)
            if pics_field and pics_field.data:
                order_counter = 1
                for f in pics_field.data:
                    if not f or not getattr(f, "filename", ""):
                        continue
                    if not alowed_file(f.filename):
                        continue

                    fn = _upload_product_image(product.id, f)
                    db.session.add(ProductGallery(
                        title=product.title or "",
                        image_file2=fn,
                        orderz=order_counter,
                        product_id=product.id,
                    ))
                    order_counter += 1

            db.session.commit()
            flash("Your Product has been created!", "success")
            return redirect(url_for("products.list_products"))

        except Exception as e:
            current_app.logger.exception("Error in new_product: %s", e)
            db.session.rollback()
            flash("Chyba pri vytváraní produktu (S3/DB).", "danger")
            return redirect(url_for("products.new_product"))

    return render_template(
        "products/new_product.html",
        title="New Product",
        form=form,
        legend="New Product",
        current_date=datetime.now(),
        next22=Next.next(),
        teamz=RightColumn.main_menu(),
        next_match=RightColumn.next_match(),
        score_table=RightColumn.score_table(),
    )


# ------------------------------
# Product gallery API (S3 presign)
# ------------------------------
@products.route("/products/images/<int:product_id>", methods=["GET"])
def get_images_by_product(product_id):
    images = (
        ProductGallery.query
        .filter_by(product_id=product_id)
        .order_by(ProductGallery.orderz.asc())
        .all()
    )

    out = []
    for img in images:
        out.append({
            "id": img.id,
            "product_id": product_id,
            "title": img.title,
            "orderz": img.orderz,
            "image_url": s3_presign(make_product_key(product_id, img.image_file2)),
        })
    return jsonify(out)


@products.route("/products/images/<int:product_id>/upload", methods=["PUT"])
@roles_required("Admin", "WebAdmin")
def upload_image(product_id):
    product = Product.query.get_or_404(product_id)
    file = request.files.get("image_file2")

    if not file or not getattr(file, "filename", "") or not alowed_file(file.filename):
        return jsonify({"error": "Invalid file"}), 400

    fn = _upload_product_image(product.id, file)

    existing_count = ProductGallery.query.filter_by(product_id=product.id).count()
    new_orderz = existing_count  # 0,1,2...

    db.session.add(ProductGallery(
        title="",
        image_file2=fn,
        orderz=new_orderz,
        product_id=product.id,
    ))
    db.session.commit()

    return jsonify({"message": "Image uploaded successfully"})


@products.route("/products/<int:product_id>/gallery/delete/<int:image_id>", methods=["DELETE"])
@roles_required("Admin", "WebAdmin")
def delete_image(product_id, image_id):
    img = ProductGallery.query.filter_by(id=image_id, product_id=product_id).first_or_404()

    _delete_product_image_from_s3(product_id, img.image_file2)

    db.session.delete(img)
    db.session.commit()
    return jsonify({"message": "Obrázok bol úspešne vymazaný"})


@products.route("/products/<int:product_id>/gallery/update_order", methods=["POST"])
@roles_required("Admin", "WebAdmin")
def update_image_order(product_id):
    data = request.json or []
    ids = [it.get("image_id") for it in data if it.get("image_id")]

    if not ids:
        return jsonify({"message": "No data"}), 400

    images = {
        g.id: g
        for g in ProductGallery.query.filter(ProductGallery.id.in_(ids)).all()
    }

    for item in data:
        g = images.get(item.get("image_id"))
        if g and g.product_id == product_id:
            g.orderz = int(item.get("orderz", g.orderz))

    db.session.commit()
    return jsonify({"message": "Image order updated successfully"})


# ------------------------------
# Variants
# ------------------------------
@products.route("/product/add_product_variant", methods=["POST"])
def add_product_variant():
    name = request.json["name"]

    type_id = db.session.execute(
        text("SELECT id FROM type_product_variant WHERE name = :n"),
        {"n": "default"}
    ).scalar()

    if not type_id:
        type_id = db.session.execute(
            text("""
                INSERT INTO type_product_variant (name, operation)
                VALUES (:n, :op)
                RETURNING id
            """),
            {"n": "default", "op": "select"}
        ).scalar()

    new_variant = ProductVariant(name=name, type=type_id)
    db.session.add(new_variant)
    db.session.commit()

    return jsonify({"message": "Product variant added successfully"})


@products.route("/product/get_product_variants")
def get_product_variants():
    product_variants = ProductVariant.query.all()
    variants = [{"id": v.id, "name": v.name} for v in product_variants]
    return jsonify({"variants": variants})


@products.route("/product/add_variant_product", methods=["POST"])
@csrf.exempt
def add_variant_product():
    product_id = request.json["product_id"]
    product_variant_id = request.json["product_variant_id"]
    variant_text = request.json["variant_text"]
    variant_image = request.json.get("variant_image", "")

    ins = variant_products.insert().values(
        product_id=product_id,
        variant_id=product_variant_id,
        variant_text=variant_text,
        variant_image=variant_image,
    )
    db.session.execute(ins)
    db.session.commit()
    return jsonify({"message": "Variant product added successfully"})


@products.route("/product/delete/variants/<int:product_id>/<int:variant_id>/<string:variant_text>", methods=["DELETE"])
def delete_variants_product(product_id, variant_id, variant_text):
    try:
        res = db.session.execute(
            variant_products.delete()
            .where(variant_products.c.product_id == product_id)
            .where(variant_products.c.variant_id == variant_id)
            .where(variant_products.c.variant_text == variant_text)
        )
        db.session.commit()
        if res.rowcount and res.rowcount > 0:
            return jsonify({"message": "VariantProdukt bol úspešne vymazaný"})
        return jsonify({"error": "VariantProdukt neexistuje"}), 404
    except Exception as e:
        return jsonify({"error": "Chyba pri vymazávaní VariantProdukt", "details": str(e)}), 500


@products.route("/product/delete/variant/<int:variant_id>", methods=["DELETE"])
def delete_variant_product(variant_id):
    try:
        used = db.session.query(variant_products).filter(variant_products.c.variant_id == variant_id).all()
        if used:
            return jsonify({"message": "ProduktVariant nie je mozne vymazat"})
        variant_obj = ProductVariant.query.get_or_404(variant_id)
        db.session.delete(variant_obj)
        db.session.commit()
        return jsonify({"message": "ProduktVariant bol úspešne vymazaný"})
    except Exception as e:
        return jsonify({"error": "Chyba pri vymazávaní ProduktVariant", "details": str(e)}), 500


@products.route("/product/get_variant_products/<int:product_id>")
def get_variant_products(product_id):
    rows = db.session.query(
        variant_products.c.product_id,
        variant_products.c.variant_id,
        variant_products.c.variant_text,
        variant_products.c.variant_image,
        ProductVariant.name
    ).join(
        ProductVariant, variant_products.c.variant_id == ProductVariant.id
    ).filter(
        variant_products.c.product_id == product_id
    ).all()

    return jsonify({
        "variant_products": [
            {
                "variant_name": r.name,
                "product_id": r.product_id,
                "variant_id": r.variant_id,
                "variant_text": r.variant_text,
                "variant_image": r.variant_image,
            } for r in rows
        ]
    })


# ------------------------------
# Stripe custom payment session
# ------------------------------
@products.route("/product/create-custom-payment-session", methods=["POST"])
@login_required
def create_custom_payment_session():
    data = request.get_json()

    product_id = int(data["ideProduct"])
    quantity = int(data.get("quantity", 1))
    product_variants = data.get("variantProductsList22", "")

    # načítaj produkt z DB (NEBER cenu z klienta)
    product = Product.query.get_or_404(product_id)

    stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

    if not product.stripe_link or not product.stripe_link.startswith("price_"):
        return jsonify(error="Produkt nemá nastavené Stripe Price ID (price_...)."), 400

    try:
        sess = stripe.checkout.Session.create(
            mode="payment",
            payment_method_types=["card"],
            line_items=[{
                "price": product.stripe_link,   # <-- toto je tvoje price_...
                "quantity": quantity,
            }],
            customer_email=current_user.email,
            success_url=current_app.url_for("products.success_products", _external=True) + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=current_app.url_for("products.cancel_products", _external=True),
            metadata={
                "user_id": current_user.id,
                "product_id": product.id,
                "product_name": product.title,
                "product_variants": product_variants,
                "quantity": quantity,
            },
        )
        return jsonify({"id": sess.id})
    except Exception as e:
        current_app.logger.exception("Stripe error: %s", e)
        return jsonify(error=str(e)), 500


# ------------------------------
# Product detail
# ------------------------------
@products.route("/product/<int:product_id>")
def product(product_id):
    # bezpečne
    product_obj = Product.query.filter(Product.is_visible.is_(True), Product.id == product_id).first_or_404()

    check_user = None
    if current_user.is_authenticated:
        check_user = Order.query.filter(
            Order.user_id == current_user.id,
            Order.produc_id == product_id
        ).first()

    # stripe session (nechávam tvoju logiku, len aby to nepadalo)
    stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
    checkout_session = None
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "eur",
                    "unit_amount": 2000,
                    "product_data": {"name": "Váš vlastný produkt", "description": "Popis vášho produktu"},
                },
                "quantity": 1,
            }],
            metadata={"user_id": current_user.id if current_user.is_authenticated else None, "product_id": product_obj.id},
            customer_email=current_user.email if current_user.is_authenticated else None,
            mode="payment",
            success_url=current_app.url_for("products.success_products", _external=True) + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=current_app.url_for("products.cancel_products", _external=True),
        )
    except Exception as e:
        current_app.logger.warning("Stripe session create failed: %s", e)

    calendar = Event.query.all()
    page = request.args.get("page", 1, type=int)

    # bočný výpis produktov (ako si mal)
    products_side = (
        db.session.query(Product)
        .join(ProductGallery, Product.id == ProductGallery.product_id)
        .join(ProductCategory, ProductCategory.id == Product.product_category_id)
        .filter(ProductGallery.orderz < 1)
        .order_by(Product.date_posted.desc())
        .paginate(page=page, per_page=3)
    )

    galleries = ProductGallery.query.filter_by(product_id=product_id).order_by(ProductGallery.orderz.asc()).all()
    category = ProductCategory.query.all()

    # prístup podľa tvojej logiky
    if (check_user is not None) or (current_user.is_authenticated and current_user.id == 1):
        return render_template(
            "products/product.html",
            checkout_session_id=(checkout_session["id"] if checkout_session else ""),
            checkout_public_key=current_app.config.get("STRIPE_PUBLIC_KEY", ""),
            check_user=check_user,
            page=page,
            products=products_side,
            calendar=calendar,
            title=product_obj.title,
            product=product_obj,
            galleries=galleries,
            category=category,
            current_date=datetime.now(),
            next22=Next.next(),
            teamz=RightColumn.main_menu(),
            next_match=RightColumn.next_match(),
            score_table=RightColumn.score_table(),
        )

    return redirect(url_for("products.list_products"))


# ------------------------------
# Category products
# ------------------------------
@products.route("/products/category/<int:category>")
def category_products(category):
    page = request.args.get("page", 1, type=int)
    category_obj = ProductCategory.query.filter_by(id=category).first_or_404()

    products_paginated = (
        Product.query
        .join(ProductCategory)
        .filter(ProductCategory.id == category_obj.id)
        .order_by(Product.date_posted.desc())
        .paginate(page=page, per_page=5)
    )

    return render_template(
        "products/category_products.html",
        products=products_paginated,
        category=category_obj,
        current_date=datetime.now(),
        next22=Next.next(),
        teamz=RightColumn.main_menu(),
        next_match=RightColumn.next_match(),
        score_table=RightColumn.score_table(),
    )


# ------------------------------
# Update product (Admin/WebAdmin) - S3 only
# ------------------------------
@products.route("/product/<int:product_id>/update", methods=["GET", "POST"])
@login_required
@roles_required("Admin", "WebAdmin")
def update_product(product_id):
    product_obj = Product.query.get_or_404(product_id)

    if product_obj.saler != current_user:
        abort(403)

    form = ProductForm()
    form.category.choices = [(c.id, c.name) for c in ProductCategory.query.all()]

    if form.validate_on_submit():
        try:
            product_obj.title = form.title.data
            product_obj.content = form.content.data
            product_obj.youtube_link = extract_youtube_id(form.youtube_link.data or "") or ""
            product_obj.stripe_link = form.stripe_link.data
            product_obj.product_category_id = form.category.data
            product_obj.price = form.price.data
            product_obj.old_price = form.old_price.data
            product_obj.is_visible = form.is_visible.data

            # titulka (orderz=0)
            cover = getattr(form, "picture", None).data if hasattr(form, "picture") else None
            if cover and getattr(cover, "filename", ""):
                if not alowed_file(cover.filename):
                    flash("Nepodporovaný typ súboru (len jpg/jpeg/png).", "danger")
                    return redirect(url_for("products.update_product", product_id=product_obj.id))

                fn = _upload_product_image(product_obj.id, cover)

                g0 = ProductGallery.query.filter_by(product_id=product_obj.id, orderz=0).first()
                if not g0:
                    db.session.add(ProductGallery(
                        title=product_obj.title or "",
                        image_file2=fn,
                        orderz=0,
                        product_id=product_obj.id,
                    ))
                else:
                    _delete_product_image_from_s3(product_obj.id, g0.image_file2)
                    g0.title = product_obj.title or ""
                    g0.image_file2 = fn

            # ďalšie obrázky (pridaj na koniec)
            pics_field = getattr(form, "pictures", None)
            if pics_field and pics_field.data:
                existing = ProductGallery.query.filter_by(product_id=product_obj.id).count()
                order_counter = existing
                for f in pics_field.data:
                    if not f or not getattr(f, "filename", ""):
                        continue
                    if not alowed_file(f.filename):
                        continue

                    fn = _upload_product_image(product_obj.id, f)
                    db.session.add(ProductGallery(
                        title=product_obj.title or "",
                        image_file2=fn,
                        orderz=order_counter,
                        product_id=product_obj.id,
                    ))
                    order_counter += 1

            db.session.commit()
            flash("Your Product has been updated!", "success")
            return redirect(url_for("products.product", product_id=product_obj.id))

        except Exception as e:
            current_app.logger.exception("Error in update_product: %s", e)
            db.session.rollback()
            flash("Chyba pri update produktu (S3/DB).", "danger")
            return redirect(url_for("products.update_product", product_id=product_obj.id))

    elif request.method == "GET":
        form.title.data = product_obj.title
        form.content.data = product_obj.content
        form.category.data = product_obj.product_category_id
        form.price.data = product_obj.price
        form.stripe_link.data = product_obj.stripe_link
        form.youtube_link.data = product_obj.youtube_link
        form.old_price.data = product_obj.old_price
        form.is_visible.data = product_obj.is_visible

    return render_template(
        "products/create_product.html",
        title="Update Product",
        product=product_obj,
        form=form,
        product_id=product_id,
        legend="Update Product",
        current_date=datetime.now(),
        next22=Next.next(),
        teamz=RightColumn.main_menu(),
        next_match=RightColumn.next_match(),
        score_table=RightColumn.score_table(),
    )


# ------------------------------
# Delete product (also delete S3)
# ------------------------------
@products.route("/product/<int:product_id>/delete", methods=["POST"])
@login_required
@roles_required("Admin", "WebAdmin")
def delete_product(product_id):
    product_obj = Product.query.get_or_404(product_id)

    if product_obj.saler != current_user:
        abort(403)

    galleries = ProductGallery.query.filter_by(product_id=product_id).all()
    for g in galleries:
        if g.image_file2:
            _delete_product_image_from_s3(product_id, g.image_file2)
        db.session.delete(g)

    db.session.delete(product_obj)
    db.session.commit()

    flash("Your Product has been deleted!", "success")
    return redirect(url_for("products.list_products"))


# ------------------------------
# Categories CRUD
# ------------------------------
@products.route("/product-categories")
def list_categories():
    page = request.args.get("page", 1, type=int)
    categories = ProductCategory.query.order_by(ProductCategory.id.desc()).paginate(page=page, per_page=5)
    return render_template(
        "products/list_categories.html",
        categories=categories,
        current_date=datetime.now(),
        next22=Next.next(),
        teamz=RightColumn.main_menu(),
        next_match=RightColumn.next_match(),
        score_table=RightColumn.score_table(),
    )


@products.route("/product-category/new", methods=["GET", "POST"])
@login_required
@roles_required("Admin", "WebAdmin")
def new_category():
    form = ProductCategoryForm()
    if form.validate_on_submit():
        category = ProductCategory(name=form.name.data)
        db.session.add(category)
        db.session.commit()
        flash("New category has been created!", "success")
        return redirect(url_for("products.list_categories"))
    
    
    yt = form.youtube_link.data or ""
    if yt.strip():
        vid = extract_youtube_id(yt)
        if not vid:
            flash("Neplatný YouTube link. Vlož watch/youtu.be/shorts link alebo Video ID.", "danger")
        return redirect(url_for("products.new_product"))

    return render_template(
        "products/create_category.html",
        title="New Product Category",
        form=form,
        legend="New Product Category",
        current_date=datetime.now(),
        next22=Next.next(),
        teamz=RightColumn.main_menu(),
        next_match=RightColumn.next_match(),
        score_table=RightColumn.score_table(),
    )


@products.route("/category/<int:product_category_id>/update", methods=["GET", "POST"])
@login_required
@roles_required("Admin", "WebAdmin")
def update_category(product_category_id):
    category_obj = ProductCategory.query.get_or_404(product_category_id)
    form = ProductCategoryForm()
    if form.validate_on_submit():
        category_obj.name = form.name.data
        db.session.commit()
        flash("A product category has been updated!", "success")
        return redirect(url_for("products.list_categories"))

    elif request.method == "GET":
        form.name.data = category_obj.name

    return render_template(
        "products/create_category.html",
        title="Update Product Category",
        form=form,
        legend="Update Product Category",
        current_date=datetime.now(),
        next22=Next.next(),
        teamz=RightColumn.main_menu(),
        next_match=RightColumn.next_match(),
        score_table=RightColumn.score_table(),
    )


@products.route("/product-category/<int:product_category_id>/delete", methods=["POST"])
@login_required
@roles_required("Admin", "WebAdmin")
def delete_category(product_category_id):
    category_obj = ProductCategory.query.get_or_404(product_category_id)
    db.session.delete(category_obj)
    db.session.commit()
    flash("A product category has been deleted!", "success")
    return redirect(url_for("products.list_categories"))


# ------------------------------
# Success / Cancel pages
# ------------------------------
@products.route("/products/success", methods=["GET"])
@login_required
def success_products():
    return render_template(
        "products/success.html",
        current_date=datetime.now(),
        next22=Next.next(),
        teamz=RightColumn.main_menu(),
        next_match=RightColumn.next_match(),
        score_table=RightColumn.score_table(),
    )


@products.route("/products/cancel", methods=["GET"])
@login_required
def cancel_products():
    return render_template(
        "products/cancel.html",
        current_date=datetime.now(),
        next22=Next.next(),
        teamz=RightColumn.main_menu(),
        next_match=RightColumn.next_match(),
        score_table=RightColumn.score_table(),
    )
