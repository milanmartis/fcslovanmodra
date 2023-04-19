from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, SelectMultipleField, IntegerField, RadioField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, StopValidation
from flask_login import current_user
from app.models import User
import phonenumbers
from wtforms import widgets


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
        
class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    
    name = StringField('Name & Surname', validators=[DataRequired()])
    phone = StringField('Phone Number (+421...)', validators=[DataRequired()])
    address = StringField('Street', validators=[DataRequired()])
    psc =StringField('Post Code', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    # eban = StringField('EBAN', validators=[DataRequired()])

    role = MultiCheckboxField('Role', choices=[], coerce=int)
    # team = SelectField('Team', choices=[], coerce=int, validators=[DataRequired()])


    submit = SubmitField('Submit')


    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                'That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(
                'That email is taken. Please choose a different one.')
        
    def validate_phone(self, phone):
        try:
            p = phonenumbers.parse(phone.data)
            if not phonenumbers.is_valid_number(p):
                raise ValueError()
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError('Invalid phone number')

class UpdateMemberForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])

    name = StringField('Name & Surname', validators=[DataRequired()])
    phone = StringField('Phone Number (+421...)', validators=[DataRequired()])
    address = StringField('Street', validators=[DataRequired()])
    psc =StringField('Post Code', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    # eban = StringField('EBAN', validators=[DataRequired()])

    role = MultiCheckboxField('Role', choices=[], coerce=int)
    team = MultiCheckboxField('Team', choices=[], coerce=int)
    position = MultiCheckboxField('Position', choices=[], coerce=int)
    
    weight = IntegerField('Weight')
    height = IntegerField('Height')


    picturemember = FileField('Update Member Picture', validators=[
                        FileAllowed(['jpg', 'png'])])
    
    submit = SubmitField('Submit')

    # def validate_username(self, username):
    #     if username.data != current_user.username:
    #         user = User.query.filter_by(username=username.data).first()
    #         if user:
    #             raise ValidationError(
    #                 'That username is taken. Please choose a different one.')

    # def validate_email(self, email):
    #     if email.data != current_user.email:
    #         user = User.query.filter_by(email=email.data).first()
    #         if user:
    #             raise ValidationError(
    #                 'That email is taken. Please choose a different one.')
        
    def validate_phone(self, phone):
        try:
            p = phonenumbers.parse(phone.data)
            if not phonenumbers.is_valid_number(p):
                raise ValueError()
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError('Invalid phone number')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[
                        FileAllowed(['jpg', 'png'])])
    
    
    name = StringField('Name & Surname', validators=[DataRequired()])
    phone = StringField('Phone Number (+421...)', validators=[DataRequired()])
    address = StringField('Street', validators=[DataRequired()])
    psc = StringField('Post Code', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])

    submit = SubmitField('Update')

    def validate_username(self, username):
        print(username.data)
        print(current_user.username)
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError(
                    'That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError(
                    'That email is taken. Please choose a different one.')
            


class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError(
                'There is no account with that email. You must register first.')
            


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password',
                             validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')



class RolesForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    description = TextAreaField('Description')
    
    submit = SubmitField('Save Role')



