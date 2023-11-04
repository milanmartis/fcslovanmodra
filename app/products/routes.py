import boto3
import uuid
from sqlalchemy import text

from app.config import Config
from flask import (render_template, url_for, flash,
                   redirect, request, session, abort, Blueprint, current_app, jsonify)
from flask_login import current_user, login_required
from app import db
from app.models import Product, User, Event, Order, ProductGallery, ProductCategory, ProductVariant, Member, variant_products
from app.products.forms import ProductForm,  ProductCategoryForm, PurchaseForm
from app.products.utils import save_picture
from app.main.routes import RightColumn
from app.main.routes import Next
from flask import Blueprint
from werkzeug.utils import secure_filename
import secrets
from PIL import Image
from flask_security import roles_required, roles_accepted
from datetime import datetime


import os
import stripe
from stripe.error import AuthenticationError

products = Blueprint('products', __name__)

s3 = boto3.client(
    's3', region_name='eu-north-1',
    aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY
)
BUCKET_NAME = Config.AWS_S3_BUCKET
ALLOWED_EXTENSIONS = {'jpg','jpeg', 'png'}
bucket_name = BUCKET_NAME

def alowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    
################  PRODUCTS  #################



# @products.route('/products/checkout', methods=['GET', 'POST'])
# def create_checkout_session():
    
    
#     try:
#         session = stripe.checkout.Session.create(
#             payment_method_types=['card'],
#             line_items=[
#                 {
#                     # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
#                     'price': 'price_1MzeHIKr9xveA3fniVgMojgb',
#                     # 'price': 'price_1MtVALKr9xveA3fnrBasXpqH',
#                     'quantity': 1,
#                 },
#             ],
#             mode='payment',
#             success_url=current_app.url_for('products.success_products', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
#             cancel_url=current_app.url_for('products.cancel_products', _external=True),
#         )
#     except Exception as e:
#         return str(e)

#     return render_template(
#         'products/checkout.html', 
#         checkout_session_id=session['id'],
#         checkout_publick_key=current_app.config['STRIPE_PUBLIC_KEY']
#         )





@products.route("/products/success", methods=['POST', 'GET'])
@login_required
def success_products():
    try:
        if stripe.checkout.Session.list():
            sessions = stripe.checkout.Session.list()
            print(sessions.data[00]) # tree view
            if sessions.data[00].metadata.user_id:
                data = {'username': sessions.data[00].metadata.user_id}
                order = Order(produc_id=sessions.data[00].metadata.product_id, quantity=sessions.data[00].metadata.quantity, amount=sessions.data[00].metadata.amount, user_id=current_user.id, is_paid=True, variants=sessions.data[00].metadata.product_variants)
                db.session.add(order)
                db.session.commit()
            member = Member.query.get(current_user.id)

            return render_template('products/success.html', member=member, produc_id=sessions.data[00].metadata.product_id, quantity=sessions.data[00].metadata.quantity, amount=sessions.data[00].metadata.amount, user_id=current_user.id, is_paid=True, product_name=sessions.data[00].metadata.product_name, variants=sessions.data[00].metadata.product_variants, data=data, current_date=datetime.now(), next22=Next.next(), teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())
        else:
            return redirect(url_for('main.home'))
    except AuthenticationError as e:
        # Zachytíme chybu AuthenticationError a môžeme spracovať návratovú hodnotu alebo vykonať ďalšie akcie.
        return render_template('errors/404.html',current_date=datetime.now(), next22=Next.next(), teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table()), 404



@products.route("/products/cancel", methods=['POST', 'GET'])
@login_required
def cancel_products():

    return render_template('products/cancel.html', current_date=datetime.now(), next22=Next.next(), teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())






@products.route("/products", methods=['GET'])
@login_required
def list_products():
    page = request.args.get('page', 1, type=int)
    products = db.session.query(Product).outerjoin(ProductCategory, ProductCategory.id == Product.product_category_id)\
    .outerjoin(ProductGallery, Product.id == ProductGallery.product_id)\
    .filter(Product.is_visible==True)\
    .order_by(Product.date_posted.desc())\
    .all()
    
    products2 = db.session.query(Product).join(ProductGallery, Product.id == ProductGallery.product_id).join(ProductCategory,\
            ProductCategory.id == Product.product_category_id).filter(Product.is_visible==True)\
    .order_by(Product.date_posted.desc()).all()

    product_category = ProductCategory.query.all()
    
    
    
    
    check_user = Order.query.filter(Order.user_id==current_user.id).filter(Product.id==Order.produc_id).first()
    
    return render_template(
        'products/products.html', 
        page=page,
        products=products, 
        products2=products2, 
        product_category=product_category, 
        current_date=datetime.now(), next22=Next.next(), 
        teamz=RightColumn.main_menu(), 
        next_match=RightColumn.next_match(), 
        score_table=RightColumn.score_table(),
        check_user=check_user
        )





@products.route("/product/new", methods=['GET', 'POST'])
@login_required
@roles_required('Admin')
def new_product():
    form = ProductForm()

    form.category.choices = [(category.id, category.name) for category in ProductCategory.query.all()]
    if form.validate_on_submit():
        product =  Product(title=form.title.data, content=form.content.data, saler=current_user, product_category_id=form.category.data, price=form.price.data, stripe_link=form.stripe_link.data, youtube_link=form.youtube_link.data, old_price=form.old_price.data, is_visible=form.is_visible.data)
        db.session.add(product)
        db.session.commit()
        # path_image = os.path.join(str(current_app.root_path)+'/static/products/'+str(product.id)+'/gallery/')
        # try:
        #     os.makedirs(path_image)
        # except OSError as error:
        #     print(error) 
            

        try:
            file = form.picture.data
            file_filename = secure_filename(file.filename)
            if not alowed_file(file.filename):
                return "FILE NOT ALLOWED!"
            bucket_name = "fcsm-files"
            new_directory_name = 'products/'+str(product.id)+'/gallery/'
            new_directory_name2 = 'products/'+str(product.id)+'/gallery/'
            s3.put_object(Bucket=bucket_name, Key=new_directory_name)

            
            # new_filename = uuid.uuid4().hex + '_'+ file_filename.rsplit('.', 1)[0] +'.' + file_filename.rsplit('.', 1)[1].lower()
            file_filename = secure_filename(file.filename)
            file_basename, file_extension = os.path.splitext(file_filename)
            new_filename = uuid.uuid4().hex + '_' + file_basename + file_extension
            s3_key = new_directory_name2 + new_filename
            # s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
            
            s3.upload_fileobj(file, bucket_name, s3_key)
            
            # form.picture.data.save(os.path.join(current_app.root_path+'/static/posts/'+str(post.id), file_filename))
            picture = ProductGallery(title=form.title.data, image_file2=new_filename, orderz=0, product_id=product.id)
            db.session.add(picture)

        
        except:
            pass
                
        pictures = []

        for file in form.pictures.data:
            # Get the filename
            file_filename = secure_filename(file.filename)
            file_basename, file_extension = os.path.splitext(file_filename)
            new_filename = uuid.uuid4().hex + '_' + file_basename + file_extension
            s3_key = new_directory_name + new_filename
            # s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
            
            s3.upload_fileobj(file, bucket_name, s3_key)
            
            
            # Create a new PostGallery object with the unique filename
            picture = ProductGallery(title=form.title.data, image_file2=new_filename, orderz=1, product_id=product.id)
            db.session.add(picture)
            
            # Add the unique filename to the pictures list
            pictures.append(new_filename)

        # Commit the changes to the database
        db.session.commit()
        flash('Your Product has been created!', 'success')
        return redirect(url_for('products.list_products'))
    return render_template('products/new_product.html', title='New Product',
                           form=form, legend='New Product', current_date=datetime.now(), next22=Next.next(), teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())

# @products.route('/product/get_product_variants')
# def get_product_variants():
#     product_variants = ProductVariant.query.all()
#     variants = [{'name': variant.name} for variant in product_variants]
#     return jsonify({'variants': variants})



############### start product gallery












# Function to generate a unique filename for uploaded images (you can customize this)
def generate_unique_filename(filename):
    import uuid
    unique_filename = uuid.uuid4().hex + '_' + filename
    return unique_filename



def get_s3_image_url(orderz, product_id, image_file):
    if orderz==0:
        folder = 'gallery/'
    else:
        folder = 'gallery/'
    
    return f'https://{Config.AWS_S3_BUCKET}.s3.amazonaws.com/products/{product_id}/{folder}{image_file}'

@products.route('/products/images/<int:product_id>', methods=['GET'])
def get_images_by_post(product_id):
    # Vytvoríme dotaz na databázu, aby sme získali všetky obrázky priradené k príspevku
    images = ProductGallery.query.filter_by(product_id=product_id).order_by(ProductGallery.orderz.asc()).all()

    # Vytvoríme zoznam obrázkov v JSON formáte
    image_list = []
    for image in images:
        image_data = {
            'id': image.id,
            'title': image.title,
            'orderz': image.orderz,
            'image_url': get_s3_image_url(image.orderz,product_id, image.image_file2)
        }
        image_list.append(image_data)
        
    print(image_list)

    return jsonify(image_list)

# Define a route to handle image upload
@products.route('/products/images/<int:product_id>/upload', methods=['PUT'])
def upload_image(product_id):
    product = Product.query.get(product_id)
    
    new_directory_name2 = 'products/'+str(product_id)+'/gallery/'


    file = request.files['image_file2']

    if file:
        file_filename = secure_filename(file.filename)
        file_basename, file_extension = os.path.splitext(file_filename)
        new_filename = uuid.uuid4().hex + '_' + file_basename + file_extension
        print('---------------------------')
        print(new_filename)
        print('---------------------------')
        # s3_key = new_directory_name2 + 
        s3_key = new_directory_name2 + new_filename
        # s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        
        s3.upload_fileobj(file, Config.AWS_S3_BUCKET, s3_key)
        existing_images_count = ProductGallery.query.filter_by(product_id=product.id).count()
        # Definujte hodnotu orderz na základe počtu prvkov
        if existing_images_count == 0:
            new_orderz = existing_images_count  # +1 pre nový obrázok
        else:
            new_orderz = existing_images_count + 1  # +1 pre nový obrázok
        
        # form.picture.data.save(os.path.join(current_app.root_path+'/static/posts/'+str(post.id), file_filename))
        picture = ProductGallery(title='', image_file2=new_filename, orderz=new_orderz, product_id=product.id)
        db.session.add(picture)
        db.session.commit()

    # print(file)
        return jsonify({"message": "Image uploaded successfully"})
        # return jsonify(message="File uploaded successfully", image_file2=filename)

    return jsonify({"error": "Failed to upload image"}), 500




@products.route('/products/<product_id>/gallery/delete/<image_id>', methods=['DELETE'])
@roles_required('Admin', 'WebAdmin')
def delete_image(product_id, image_id):
    print(product_id)
    try:     
        # request_data = request.json
        # image_id_to_delete = request_data.get('imageId')
        image = ProductGallery.query.filter_by(id=image_id).first()

        s3.delete_object(Bucket=Config.AWS_S3_BUCKET, Key=f"/products/{product_id}/gallery/{image.image_file2}")
        db.session.delete(image)
        db.session.commit()
        
        return jsonify({"message": "Obrázok bol úspešne vymazaný"})

    except Exception as e:
        # logging.error(f'Chyba: {str(e)}')
        return jsonify({"error": str(e)}), 500  # Vrátiť JSON s chybovou správou a HTTP kódom 500 v prípade chyby



# Define a route to update image order
@products.route('/products/<int:product_id>/gallery/update_order', methods=['POST'])
def update_image_order(product_id):
    data = request.json
    # images = data.get('data')
    print(data)
    
    for image in data:
        new_order_image = ProductGallery.query.get(image['image_id'])
        new_order_image.orderz = image['orderz']
    
    db.session.commit()

    return jsonify({"message": "Image order updated successfully"})

















################ end product gallery


@products.route('/product/add_product_variant', methods=['POST'])
def add_product_variant():
    if request.method == 'POST':
        name = request.json['name']  # Získajte názov z POST requestu
        # Vytvorte nový záznam v tabuľke product_variant
        new_variant = ProductVariant(name=name,type=2)
        db.session.add(new_variant)
        db.session.commit()
        return jsonify({'message': 'Product variant added successfully'})

@products.route('/product/get_product_variants')
def get_product_variants():
    product_variants = ProductVariant.query.all()
    print(product_variants)
    variants = [{'id': variant.id, 'name': variant.name} for variant in product_variants]
    return jsonify({'variants': variants})

@products.route('/product/add_variant_product', methods=['POST'])
def add_variant_product():
    if request.method == 'POST':
        product_id = request.json['product_id']
        product_variant_id = request.json['product_variant_id']
        variant_text = request.json['variant_text']
        variant_image = request.json['variant_image']
        
        # Vytvorte nový záznam v tabuľke variant_products
        new_variant_product = variant_products.insert().values(
            product_id=product_id,
            variant_id=product_variant_id,
            variant_text=variant_text,
            variant_image=variant_image
        )

        db.session.execute(new_variant_product)
        db.session.commit()
        return jsonify({'message': 'Variant product added successfully'})

@products.route('/product/delete/variants/<int:product_id>/<int:variant_id>/<string:variant_text>', methods=['DELETE'])
def delete_variants_product(product_id, variant_id, variant_text):
    try:
        # Použite SQLAlchemy na získanie záznamu, ktorý chcete vymazať
        variants_to_delete = db.session.execute(
            variant_products.delete()
            .where(variant_products.c.product_id == product_id)
            .where(variant_products.c.variant_id == variant_id)
            .where(variant_products.c.variant_text == variant_text)
        )

        # Potvrďte transakciu
        if variants_to_delete:
            # Odstráňte záznam z databázy
            db.session.commit()

            # Po úspešnom vymazaní produktu vráťte úspešnú odpoveď
            return jsonify({'message': 'VariantProdukt bol úspešne vymazaný'})
        else:
            # Ak sa záznam nenašiel, vráťte chybovú odpoveď
            return jsonify({'error': 'VariantProdukt neexistuje'}), 404

    except Exception as e:
        # Ak nastane chyba pri vymazávaní, vráťte chybovú odpoveď
        return jsonify({'error': 'Chyba pri vymazávaní VariantProdukt', 'details': str(e)}), 500


@products.route('/product/delete/variant/<int:variant_id>', methods=['DELETE'])
def delete_variant_product(variant_id):
    try:
        free_variants = db.session.query(variant_products).filter(variant_products.c.variant_id==variant_id).all()
        if free_variants:
            return jsonify({'message': 'ProduktVariant nie je moyne vymazat'})
        else:
            variant_product = ProductVariant.query.get_or_404(variant_id)
        
            db.session.delete(variant_product)
            db.session.commit()

            return jsonify({'message': 'ProduktVariant bol úspešne vymazaný'})

    except Exception as e:
        return jsonify({'error': 'Chyba pri vymazávaní ProduktVariant', 'details': str(e)}), 500


@products.route('/product/get_variant_products/<int:product_id>')
def get_variant_products(product_id):
    # Načítajte existujúce variant_products a vráťte ich vo forme JSON
    variant_products2 = db.session.query(
        variant_products.c.product_id, variant_products.c.variant_id, variant_products.c.variant_text, variant_products.c.variant_image,
        ProductVariant.name
    ).join(ProductVariant,variant_products.c.variant_id==ProductVariant.id).filter(variant_products.c.product_id==product_id).all()
    print('--------------------------')
    print(variant_products2)
    print('--------------------------')
    return jsonify({'variant_products': [{'variant_name': product.name,'product_id': product.product_id,'variant_id': product.variant_id, 'variant_text': product.variant_text, 'variant_image': product.variant_image} for product in variant_products2]})

# @app.route('/product/delete_variant_product/<int:id>', methods=['POST'])
# def delete_variant_product(id):
#     # Nájdite a vymažte variant_product podľa zadaného ID
#     variant_product = VariantProduct.query.get_or_404(id)
#     db.session.delete(variant_product)
#     db.session.commit()
#     return jsonify({'message': 'Variant product deleted successfully'})

@products.route('/product/create-custom-payment-session', methods=['POST'])
def create_custom_payment_session():
    data = request.get_json()
    custom_price = data['customPrice']
    product_name = data['productName']
    product_id = data['ideProduct']
    product_variants = data['variantProductsList22']
    unit_price = data['unit_price']
    quantity = data['quantity']
    # print(product_variants)
    # Vytvorenie platobnej relácie
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'eur',
                        'product_data': {
                            'name': product_name,
             
      
                        },
                        'unit_amount': int(float(unit_price) * 100),  # Cena v centoch
                    },
                    'quantity': int(quantity),
                },
            ],
            customer_email=current_user.email,
            mode='payment',
            success_url=current_app.url_for('products.success_products', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=current_app.url_for('products.cancel_products', _external=True),
            metadata={
                'user_id': current_user.id,
                'product_id': product_id,
                'product_name': product_name, 
                'product_variants': product_variants,  
                'amount': float(unit_price),  
                'quantity': int(quantity),  

            },
        )
        return jsonify(session)
    except Exception as e:
        return jsonify(error=str(e))

@products.route("/product/<int:product_id>")
@login_required
def product(product_id):
    
    title_image = db.session.query(ProductGallery).filter(ProductGallery.product_id == product_id).order_by(ProductGallery.orderz.asc()).first()
    product = Product.query.outerjoin(ProductGallery, Product.id == ProductGallery.product_id).filter(Product.is_visible==True).filter(Product.id==product_id).first()
    check_user = Order.query.filter(Order.user_id==current_user.id).filter(Order.produc_id==product_id).first()
    stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
    pro = db.session.query(Product).filter(Product.id == product_id).first()
    
    form = PurchaseForm()

    form.sizes.choices = [(size.id, size.name) for size in ProductVariant.query.all()]
    
    # if form.validate_on_submit():

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    # Namiesto 'price' môžete nastaviť 'price_data' s vlastnou cenou a menou
                    'price_data': {
                        'currency': 'eur',  # Mena, napríklad 'usd'
                        'unit_amount': 2000,  # Cena v centoch (tu je to $10.00)
                        'product_data': {
                            'name': 'Váš vlastný produkt',  # Názov vášho produktu
                            'description': 'Popis vášho produktu',  # Popis vášho produktu
                        },
                    },
                    'quantity': 1,
                },
            ],
            metadata={
                'user_id': current_user.id,
                'product_id': product.id,
                'custom_field': 'Hodnota pre vlastné pole',  # Ďalšie vlastné údaje môžete pridať sem
            },
            customer_email=current_user.email,
            mode='payment',
            success_url=current_app.url_for('products.success_products', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=current_app.url_for('products.cancel_products', _external=True),
        )
    except Exception as e:
        return str(e)
    
     
    calendar = Event.query.all()
    page = request.args.get('page', 1, type=int)

    products = db.session.query(Product).join(ProductGallery, Product.id == ProductGallery.product_id).join(ProductCategory, ProductCategory.id == Product.product_category_id).filter(ProductGallery.orderz<1).order_by(Product.date_posted.desc()).paginate(page=page, per_page=3)

    
    galleries = ProductGallery.query.filter(ProductGallery.product_id==product_id).all()
    category = ProductCategory.query.all()
    
    # session.permanent = True
    #         session["name"] = form.email.data
    
    if check_user or current_user.id==1:
        return render_template('products/product.html', title_image=title_image,
                               checkout_session_id=session['id'], 
                               checkout_public_key=current_app.config['STRIPE_PUBLIC_KEY'],
                               check_user=check_user, 
                               page=page, 
                               products=products, 
                               calendar=calendar, 
                               title=product.title, 
                               product=product, 
                               galleries=galleries, 
                               category=category, 
                               current_date=datetime.now(), next22=Next.next(), 
                               teamz=RightColumn.main_menu(), 
                               next_match=RightColumn.next_match(), 
                               score_table=RightColumn.score_table()
                            )
    else:
        return redirect( url_for('products.list_products'))

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
    return render_template('products/category_products.html', products=products, category=category, current_date=datetime.now(), next22=Next.next(), teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())





@products.route("/product/<int:product_id>/update", methods=['GET', 'POST'])
@login_required
def update_product(product_id):
    product = db.session.query(Product).filter_by(id=product_id).first()
    
    
    if product.saler != current_user:
        abort(403)
    form = ProductForm()
    form.category.choices = [(category.id, category.name) for category in ProductCategory.query.all()]
    if form.validate_on_submit():
        product.title = form.title.data
        product.content = form.content.data
        product.youtube_link = form.youtube_link.data
        product.stripe_link = form.stripe_link.data
        product.product_category_id = form.category.data
        product.price = form.price.data
        product.is_visible = form.is_visible.data
        
        path_image = os.path.join(str(current_app.root_path)+'/static/products/'+str(product.id)+'/gallery/')
        try:
            os.makedirs(path_image)
        except OSError as error:
            print(error) 

        if form.picture.data:
            file = form.picture.data
            file_filename = secure_filename(file.filename)
            form.picture.data.save(os.path.join(current_app.root_path+'/static/products/'+str(product.id)+'/'+file_filename))

       
            productgall = ProductGallery.query.filter(ProductGallery.orderz==0).filter(ProductGallery.product_id==product_id).first()
            productgall.title=form.title.data
            productgall.image_file2=file_filename

        for file in form.pictures.data:
            if file:
                print(file.filename)
                with open(os.path.realpath(current_app.root_path+'/static/products/'+str(product.id)+'/gallery/'+str(file.filename)), 'wb') as f:
                        f.write(file.read())

                # file_filename = secure_filename(file.filename)
                # form.picture.data.save(os.path.join(current_app.root_path+'/static/posts/'+str(post.id)+'/gallery', file_filename))
                pictures = ProductGallery(title=form.title.data, image_file2=file.filename, orderz=1, product_id=product.id)
                db.session.add(pictures)


        db.session.commit()
        flash('Your Product has been updated!', 'success')
        return redirect(url_for('products.product', product_id=product.id))
    elif request.method == 'GET':
        form.title.data = product.title
        form.content.data = product.content
        form.category.data = product.product_category_id
        form.price.data = product.price
        form.stripe_link.data = product.stripe_link
        form.youtube_link.data = product.youtube_link
        form.old_price.data = product.old_price
        form.is_visible.data = product.is_visible
    return render_template('products/create_product.html', title='Update Product',
                           product=product,form=form, product_id=product_id, legend='Update Product', current_date=datetime.now(), next22=Next.next(), teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())


@products.route("/product/<int:product_id>/delete", methods=['POST'])
@login_required
def delete_product(product_id):

    productgall = ProductGallery.query.filter_by(product_id=product_id).all()
    for gal in productgall:
        pg = ProductGallery.query.get(gal.id)
        db.session.delete(pg)

    product = Product.query.get(product_id)
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
    return render_template('products/list_categories.html', categories=categories, current_date=datetime.now(), next22=Next.next(), teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())


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
                           form=form, legend='New Product Category', current_date=datetime.now(), next22=Next.next(), teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())


@products.route("/product-category/<int:product_category_id>")
def category(product_category_id):
    category = Product.query.get_or_404(product_category_id)
    return render_template('products/category.html', name=category.name, category=category, current_date=datetime.now(), next22=Next.next(), teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())


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
                           form=form, legend='Update Product Category', current_date=datetime.now(), next22=Next.next(), teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())


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
