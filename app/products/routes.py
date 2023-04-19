from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint, current_app)
from flask_login import current_user, login_required
from app import db
from app.models import Product, ProductGallery, ProductCategory
from app.products.forms import ProductForm,  ProductCategoryForm
from flask import Blueprint
from werkzeug.utils import secure_filename
import secrets
from PIL import Image
from app.products.utils import save_picture
from app.main.routes import RightColumn

import os

products = Blueprint('products', __name__)


################  PRODUCTS  #################





@products.route("/products", methods=['GET'])
def list_products():
    page = request.args.get('page', 1, type=int)
    products = Product.query.join(ProductGallery, ProductCategory).filter(
        Product.id == ProductGallery.product_id).filter(ProductCategory.id == Product.product_category_id).filter(ProductGallery.orderz<1).order_by(Product.date_posted.desc()).paginate(page=page, per_page=3)

    product_category = ProductCategory.query.all()
    
    return render_template('products/products.html', products=products, product_category=product_category, teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())





@products.route("/product/new", methods=['GET', 'POST'])
@login_required
def new_product():
    form = ProductForm()

    form.category.choices = [(category.id, category.name) for category in ProductCategory.query.all()]
    if form.validate_on_submit():
        product =  Product(title=form.title.data, content=form.content.data, saler=current_user, product_category_id=form.category.data, price=form.price.data, old_price=form.old_price.data, is_visible=form.is_visible.data)
        db.session.add(product)
        db.session.commit()
        path_image = os.path.join(str(current_app.root_path)+'/static/products/'+str(product.id)+'/gallery/')
        try:
            os.makedirs(path_image)
        except OSError as error:
            print(error) 

        # for file in form.pictures.data:
        file = form.picture.data
        file_filename = secure_filename(file.filename)
        form.picture.data.save(os.path.join(current_app.root_path+'/static/products/'+str(product.id), file_filename))
        pictures = []
        filez = 0

        for file in form.pictures.data:
            print(file.filename)
            with open(os.path.realpath(current_app.root_path+'/static/products/'+str(product.id)+'/gallery/'+str(file.filename)), 'wb') as f:
                    f.write(file.read())

            pictures = ProductGallery(title=form.title.data, image_file2=file.filename, orderz=1, product_id=product.id)
            db.session.add(pictures)

        picture = ProductGallery(title=form.title.data, image_file2=file_filename, orderz=0, product_id=product.id)
        db.session.add(picture)
        db.session.commit()
        flash('Your Product has been created!', 'success')
        return redirect(url_for('products.list_products'))
    return render_template('products/create_product.html', title='New Product',
                           form=form, legend='New Product', teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())


@products.route("/product/<int:product_id>")
def product(product_id):
    page = request.args.get('page', 1, type=int)

    products = Product.query.join(ProductGallery, ProductCategory).filter(
        Product.id == ProductGallery.product_id).filter(ProductCategory.id == Product.product_category_id).filter(ProductGallery.orderz<1).order_by(Product.date_posted.desc()).paginate(page=page, per_page=3)

    product = Product.query.join(ProductGallery).filter(
        Product.id == ProductGallery.product_id).filter(ProductGallery.orderz<1).filter(Product.id==product_id).first()
    galleries = ProductGallery.query.filter(ProductGallery.product_id==product_id).all()
    category = ProductCategory.query.all()
    
    
    
    
    return render_template('products/product.html', page=page, products=products, title=product.title, product=product, galleries=galleries, category=category, teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())


@products.route("/products/category/<int:category>")
def category_products(category):
    print(category)
    page = request.args.get('page', 1, type=int)
    category = ProductCategory.query.filter_by(id=category).first_or_404()
    products = Product.query\
        .join(ProductCategory)\
        .filter(ProductCategory.id==category.id)\
        .order_by(Product.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('products/category_products.html', products=products, category=category, teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())





@products.route("/product/<int:product_id>/update", methods=['GET', 'POST'])
@login_required
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    if product.saler != current_user:
        abort(403)
    form = ProductForm()
    form.category.choices = [(category.id, category.name) for category in ProductCategory.query.all()]
    if form.validate_on_submit():
        product.title = form.title.data
        product.content = form.content.data
        product.product_category_id = form.category.data

        if form.picture.data:
            file = form.picture.data
            file_filename = secure_filename(file.filename)
            form.picture.data.save(os.path.join(current_app.root_path+'/static/products/'+str(product_id), file_filename))

       
            productgall = ProductGallery.query.filter(ProductGallery.orderz==0).filter(ProductGallery.product_id==product_id).first()
            productgall.title=form.title.data
            productgall.image_file2=file_filename




        db.session.commit()
        flash('Your Product has been updated!', 'success')
        return redirect(url_for('products.product', product_id=product.id))
    elif request.method == 'GET':
        form.title.data = product.title
        form.content.data = product.content
        form.category.data = product.product_category_id
        form.price.data = product.price
        form.old_price.data = product.old_price
        form.is_visible.data = product.is_visible
    return render_template('products/create_product.html', title='Update Product',
                           form=form, product_id=product_id, legend='Update Product', teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())


@products.route("/product/<int:product_id>/delete", methods=['POST','GET'])
@login_required
def delete_product(product_id):

    productgall = ProductGallery.query.filter_by(product_id=product_id).all()
    for gal in productgall:
        pg = ProductGallery.query.get(gal.id)
        db.session.delete(pg)

    product = Product.query.get_or_404(product_id)
    if product.saler != current_user:
        abort(403)
    db.session.delete(product)
    db.session.commit()
    flash('Your Product has been deleted!', 'success')
    return redirect(url_for('products.list_products'))




################  CATEGORIES  #################

@products.route("/product-categories")
def list_categories():
    page = request.args.get('page', 1, type=int)
    categories = ProductCategory.query.order_by(ProductCategory.id.desc()).paginate(page=page, per_page=5)
    return render_template('products/list_categories.html', categories=categories, teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())


@products.route("/product-category/new", methods=['GET', 'POST'])
@login_required
def new_category():
    form = ProductCategoryForm()
    if form.validate_on_submit():
        category = ProductCategory(name=form.name.data)
        db.session.add(category)
        db.session.commit()
        flash('New category has been created!', 'success')
        return redirect(url_for('products.list_categories'))
    return render_template('products/create_category.html', title='New Product Category',
                           form=form, legend='New Product Category', teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())


@products.route("/product-category/<int:product_category_id>")
def category(product_category_id):
    category = Product.query.get_or_404(product_category_id)
    return render_template('products/category.html', name=category.name, category=category, teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())


@products.route("/category/<int:product_category_id>/update", methods=['GET', 'POST'])
@login_required
def update_category(product_category_id):
    category = ProductCategory.query.get_or_404(product_category_id)
    # if post.author != current_user:
    #     abort(403)
    form = ProductCategoryForm()
    if form.validate_on_submit():
        category.name = form.name.data
        db.session.commit()
        flash('A product category has been updated!', 'success')
        return redirect(url_for('products.list_categories', product_category_id=category.id))
    elif request.method == 'GET':
        form.name.data = category.name
    return render_template('products/create_category.html', title='Update Product Category',
                           form=form, legend='Update Product Category', teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())


@products.route("/product-category/<int:product_category_id>/delete", methods=['POST'])
@login_required
def delete_category(product_category_id):
    category = Product.query.get_or_404(product_category_id)
    # if post.author != current_user:
    #     abort(403)
    db.session.delete(category)
    db.session.commit()
    flash('A product category has been deleted!', 'success')
    return redirect(url_for('products.list_categories'))
