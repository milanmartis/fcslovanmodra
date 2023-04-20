
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
    link = StringField('Link to the product', validators=[DataRequired()])
    price = DecimalField(places=2, validators=[DataRequired()])
    old_price = DecimalField(places=2, validators=[DataRequired()])
    picture = FileField('Title Image upload')
    pictures = MultipleFileField('Gallery Image(s) upload', render_kw={'multiple': True})
    submit = SubmitField('Post')

class ProductCategoryForm(FlaskForm):
    name = StringField('', validators=[DataRequired()])
    submit = SubmitField('Save It')

