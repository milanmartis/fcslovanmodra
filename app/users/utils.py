import os
import secrets
from PIL import Image
from flask import url_for, current_app
from flask_mail import Message
from app import mail


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

def save_picture_member(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/members_pics', picture_fn)

    # output_size = (125, 125)
    i = Image.open(form_picture)
    # i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Obnovenie hesla',
                  sender=('FC Slovan Modra', 'info@fcslovanmodra.sk'),
                  recipients=[user.email])
    msg.body = f'''Pre obnovenie hesla kliknite na tento odkaz:
{url_for('users.reset_token', token=token, _external=True)}
Ak ste túto žiadosť neodoslali, jednoducho ignorujte tento e-mail a nebudú vykonané žiadne zmeny.
'''
    mail.send(msg)


def send_confirm_email(user):
    token = user.get_confirm_token()
    msg = Message('Potvrd+te svoju registráciu',
                  sender=('FC Slovan Modra', 'info@fcslovanmodra.sk'),
                  recipients=[user.email])
    msg.body = f'''Na potvrdenie registrácie kliknite na tento odkaz:
{url_for('users.confirm_token', token=token, _external=True)}
Ak ste túto žiadosť neodoslali, jednoducho ignorujte tento e-mail a nebudú vykonané žiadne zmeny.
'''
    mail.send(msg)



def environment():
    """
    This is not how you want to handle environments in a real project,
    but for the sake of simplicity I'll create this function.

    Look at using environment variables or dotfiles for these.
    """
    return {
        "billing": {
            "stripe": {
                "token": "****",
                "product": "****",
            }
        }

    }