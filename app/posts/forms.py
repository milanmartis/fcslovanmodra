
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    category = SelectField('Category', choices=[], coerce=int, validators=[DataRequired()])
    submit = SubmitField('Post')

class CategoryForm(FlaskForm):
    name = StringField('Name A Category', validators=[DataRequired()])
    submit = SubmitField('Save It')


