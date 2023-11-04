
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired,FileAllowed
from wtforms import StringField, SubmitField, TextAreaField, SelectField, IntegerField, validators, BooleanField, DecimalField
from wtforms.validators import DataRequired
from wtforms import MultipleFileField

class ProductForm(FlaskForm):
    title = StringField('Name of the product', validators=[DataRequired()])
    content = TextAreaField('Description', validators=[DataRequired()])
    category = SelectField('Product Category', choices=[], coerce=int, validators=[DataRequired()])
    is_visible = BooleanField('Visible')
    stripe_link = StringField('Stripe ID', validators=[DataRequired()])
    youtube_link = StringField('Link to the product')
    price = DecimalField(places=2, validators=[DataRequired()])
    old_price = DecimalField(places=2, validators=[DataRequired()])
    picture = FileField('Title Image upload')
    pictures = FileField('Preview Picture', render_kw={'multiple': True}, validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    # pictures = MultipleFileField('Gallery Image(s) upload', render_kw={'multiple': True})
    submit = SubmitField('Post')


class ProductCategoryForm(FlaskForm):
    name = StringField('', validators=[DataRequired()])
    submit = SubmitField('Save It')



class ProductVariantForm(FlaskForm):
    text = StringField('Version description', validators=[DataRequired()])
    submit = SubmitField('Create')

class ProductVersionForm2(FlaskForm):
    text = StringField('Version description', validators=[DataRequired()])
    proimages = SelectField('Product images', choices=[], coerce=int, validators=[DataRequired()])
    submit = SubmitField('Create')

class PurchaseForm(FlaskForm):
    name = StringField('', validators=[DataRequired()])
    sizes = SelectField('Available version', choices=[], coerce=int, validators=[DataRequired()])

    submit = SubmitField('Zaplatiť teraz')

