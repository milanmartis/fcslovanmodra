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
    username = StringField('Užívateľské meno',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('E-mail',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Heslo',
                             validators=[DataRequired()])
    confirm_password = PasswordField('Potvrdiť heslo',
                                     validators=[DataRequired(), EqualTo('password')])
    
    name = StringField('Meno a priezvisko', validators=[DataRequired()])
    phone = StringField('Mobilné číslo (+421...)', validators=[DataRequired()])
    address = StringField('Ulica', validators=[DataRequired()])
    psc =StringField('PSČ', validators=[DataRequired()])
    city = StringField('Mesto', validators=[DataRequired()])
    # eban = StringField('EBAN', validators=[DataRequired()])

    role = MultiCheckboxField('Rola', choices=[], coerce=int)
    # team = SelectField('Team', choices=[], coerce=int, validators=[DataRequired()])


    submit = SubmitField('Registrovať')


    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                'Vybrané uživateľské meno už existuje. Vyberte iné.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(
                'Taký e-mail je už registrovaný. Vyberte iný.')
        
    def validate_phone(self, phone):
        try:
            p = phonenumbers.parse(phone.data)
            if not phonenumbers.is_valid_number(p):
                raise ValueError()
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError('Chybné mobilné číslo')

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
            raise ValidationError('Zlé telefónne číslo')


class LoginForm(FlaskForm):
    email = StringField('E-mail',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Heslo',
                             validators=[DataRequired()])
    remember = BooleanField('Zapamätať prihlásenie')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Užívateľské meno',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Zmeniť užívateľskú fotografiu', validators=[
                        FileAllowed(['jpg', 'png'])])
    
    
    name = StringField('Meno a priezvisko & Surname', validators=[DataRequired()])
    phone = StringField('Mobilné číslo (+421...)', validators=[DataRequired()])
    address = StringField('Ulica', validators=[DataRequired()])
    psc = StringField('PSČ', validators=[DataRequired()])
    city = StringField('Mesto', validators=[DataRequired()])

    submit = SubmitField('Uložiť')

    def validate_username(self, username):
        print(username.data)
        print(current_user.username)
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError(
                    'Vybrané uživateľské meno už existuje. Vyberte iné.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError(
                    'Taký e-mail je už registrovaný. Vyberte iný.')
            


class RequestResetForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    submit = SubmitField('Chcem nové heslo')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError(
                'Účet s takým e-mailom neexistuje. Skúste iný.')
            


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Heslo',
                             validators=[DataRequired()])
    confirm_password = PasswordField('Potvrdiť heslo',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Uložiť nové heslo')



class RolesForm(FlaskForm):
    name = StringField('Názov role', validators=[DataRequired()])
    description = TextAreaField('Popis role')
    
    submit = SubmitField('Uložiť')



