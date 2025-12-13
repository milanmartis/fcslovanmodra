# app/users/utils.py
import os
import secrets
from PIL import Image
from flask import url_for, current_app
from flask_mail import Message


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, "static/profile_pics", picture_fn)

    output_size = (125, 125)
    img = Image.open(form_picture)
    img.thumbnail(output_size)
    img.save(picture_path)

    return picture_fn


def save_picture_member(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, "static/members_pics", picture_fn)

    img = Image.open(form_picture)
    img.save(picture_path)

    return picture_fn


def _send_mail(msg: Message) -> None:
    """
    Safe mail send without importing `mail` from app (prevents circular imports).
    Flask-Mail registers itself as extension named 'mail'.
    """
    try:
        mail_ext = current_app.extensions.get("mail")
        if mail_ext is None:
            raise RuntimeError("Flask-Mail extension is not initialized. Did you call mail.init_app(app)?")

        mail_ext.send(msg)

    except Exception:
        current_app.logger.exception("MAIL SEND FAILED")
        raise


def send_reset_email(user):
    token = user.get_reset_token()

    msg = Message(
        subject="Obnovenie hesla",
        recipients=[user.email],
        sender=current_app.config.get("MAIL_DEFAULT_SENDER"),
    )

    msg.body = (
        "Pre obnovenie hesla kliknite na tento odkaz:\n"
        f"{url_for('users.reset_token', token=token, _external=True)}\n\n"
        "Ak ste túto žiadosť neodoslali, jednoducho ignorujte tento e-mail a nebudú vykonané žiadne zmeny.\n"
    )

    _send_mail(msg)


def send_confirm_email(user):
    token = user.get_confirm_token()

    msg = Message(
        subject="Potvrďte svoju registráciu",
        recipients=[user.email],
        sender=current_app.config.get("MAIL_DEFAULT_SENDER"),
    )

    msg.body = (
        "Na potvrdenie registrácie kliknite na tento odkaz:\n"
        f"{url_for('users.confirm_token', token=token, _external=True)}\n\n"
        "Ak ste túto žiadosť neodoslali, jednoducho ignorujte tento e-mail a nebudú vykonané žiadne zmeny.\n"
    )

    _send_mail(msg)
