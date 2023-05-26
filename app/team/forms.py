
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired,FileAllowed
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired
from wtforms import MultipleFileField


class TeamForm(FlaskForm):
    name = StringField('Name of The Team', validators=[DataRequired()])
    main_league = StringField('Name of the main league')
    score_scrap = StringField('Table of Ligue (full web link)')
    player_list_scrap = StringField('Players LineUp (full web link)')
    
    # role = SelectField('Role', choices=[], coerce=int, validators=[DataRequired()])

    submit = SubmitField('Save')

