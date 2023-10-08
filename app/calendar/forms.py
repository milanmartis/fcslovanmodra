
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired,FileAllowed
from wtforms import StringField, SubmitField, TextAreaField, SelectField, IntegerField, validators, BooleanField, DecimalField, SelectMultipleField
from wtforms.validators import DataRequired, StopValidation
from wtforms import MultipleFileField
from wtforms import widgets
from wtforms import DateField, DateTimeField, DateTimeLocalField



class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(html_tag='ol', prefix_label=False)
    option_widget = widgets.CheckboxInput()


class MultiCheckboxAtLeastOne():
    def __init__(self, message=None):
        if not message:
            message = 'At least one option must be selected.'
        self.message = message

    def __call__(self, form, field):
        if len(field.data) == 0:
            raise StopValidation(self.message)




class EventForm(FlaskForm):
    title = StringField('Event Name', validators=[DataRequired()])
    team = SelectField('Team', choices=[], coerce=int)
    category = SelectField('Category', choices=[], coerce=int, validators=[DataRequired()])

    start = DateTimeLocalField('Start', format='%Y/%m/%dT%H:%M:%s')
    end = DateTimeLocalField('End', format='%Y/%m/%dT%H:%M:%s')
    address = StringField('Event Address', validators=[DataRequired()])
    link = StringField('Event Link', validators=[DataRequired()])

    submit = SubmitField('Save')


class UpdateEventForm(FlaskForm):
    title2 = StringField('Event Name', validators=[DataRequired()])
    team2 = SelectField('Team', choices=[], coerce=int)
    category2 = SelectField('Category', choices=[], coerce=int, validators=[DataRequired()])

    start2 = DateTimeLocalField('Start', format='%Y/%m/%dT%H:%M:%s')
    end2 = DateTimeLocalField('End', format='%Y/%m/%dT%H:%M:%s')
    address2 = StringField('Event Address', validators=[DataRequired()])
    link2 = StringField('Event Link', validators=[DataRequired()])

    submit = SubmitField('Save')


