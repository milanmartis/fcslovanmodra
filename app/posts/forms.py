
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired,FileAllowed
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired
from wtforms import MultipleFileField

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    category = SelectField('Category', choices=[], coerce=int, validators=[DataRequired()])
    picture = FileField('Title Image upload')
    pictures = MultipleFileField('Gallery Image(s) upload', render_kw={'multiple': True})
    submit = SubmitField('Post')

class CategoryForm(FlaskForm):
    name = StringField('', validators=[DataRequired()])
    submit = SubmitField('Save It')


