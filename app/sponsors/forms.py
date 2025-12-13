# app/sponsors/forms.py
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional

class SponsorForm(FlaskForm):
    name = StringField('Názov', validators=[DataRequired()])
    
    # NEVALIDUJEME URL, nech tam môžeš dať aj "modra.sk"
    url = StringField('Odkaz (https://...)', validators=[Optional()])
    
    kind = SelectField(
        'Typ',
        choices=[
            ('main', 'Hlavný partner'),
            ('partner', 'Partner'),
        ],
        validators=[DataRequired()]
    )

    image = FileField(
        'Obrázok',
        validators=[
            FileRequired(message="Vyber obrázok."),
            FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Povolené sú len obrázky.')
        ]
    )

    submit = SubmitField('Uložiť')
