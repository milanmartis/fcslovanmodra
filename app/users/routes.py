from flask import render_template, url_for, flash, redirect, request, Blueprint, session, current_app, jsonify
# from flask_login import 
from app import db, bcrypt
from sqlalchemy import func
from flask_mail import Message
from app import csrf
import os

from app.models import User, Post, Role, Team, Member, Player, Position, roles_users, teams_members, positions_members
from app.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm,UpdateMemberForm,
                                   RequestResetForm, ResetPasswordForm, RolesForm)
from app.users.utils import (
    save_picture,
    save_picture_member,
    send_reset_email,
    send_confirm_email,
    _send_mail,
)
import uuid
from app.main.routes import RightColumn
from app.main.routes import Next
# from flask_security import roles_required, login_user, current_user, logout_user, login_required
from flask_login import login_user, current_user, logout_user, login_required

# from flask_principal import identity_changed, Identity
from flask_principal import Identity, identity_changed
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.utils import secure_filename


users = Blueprint('users', __name__)

from app.posts.routes import s3_client, s3_presign, s3_extra_args, BUCKET_NAME

def make_member_key(member_id: int, filename: str) -> str:
    return f"members/{member_id}/{filename}"

from functools import wraps
from flask import abort

def roles_required(*roles):
    def deco(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if not current_user.has_role(*roles):
                abort(403)
            return fn(*args, **kwargs)
        return wrapper
    return deco


ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp"}

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# def access_required(role="Admin"):
    
#     def wrapper(fn):
#         @wraps(fn)
#         def decorated_view(*args, **kwargs):
#             if session.get("role") == None or role == "ANY":
#                 session['header'] = "Welcome Guest, Request a new role for higher rights!"
#                 return redirect(url_for('main.home'))
#             if session.get("role") == 'Member' and role == 'Member':
#                 print("access: Member")
#                 session['header'] = "Welcome to Member Page!"
#                 return redirect(url_for('index'))
#             if session.get("role") == 'Admin' and role == 'Admin':
#                 session['header'] = "Welcome to Admin Page!"
#                 print("access: Admin")
#             else:
#                 session['header'] = "Oh no no, you haven'tn right of access!!!"
#                 return redirect(url_for('index'))
#             return fn(*args, **kwargs)
#         return decorated_view
#     return wrapper





@users.route("/register", methods=["GET", "POST"])
@csrf.exempt
def register():
    form = RegistrationForm()
    form.role.choices = [(role.id, role.name) for role in Role.query.all()]

    if form.validate_on_submit():
        try:
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
            user = User(
                uuid=str(uuid.uuid4()),
                username=form.username.data,
                email=form.email.data,
                password=hashed_password
            )
            db.session.add(user)
            db.session.flush()  # aby user.id existovalo ešte pred commitom

            member = Member(
                name=form.name.data,
                phone=form.phone.data,
                address=form.address.data,
                psc=form.psc.data,
                city=form.city.data,
                user_id=user.id,
            )
            db.session.add(member)

            roles = Role.query.filter(Role.id.in_(form.role.data)).all()
            for rol in roles:
                user.roles.append(rol)

            db.session.commit()

            send_confirm_email(user)
            flash("Bol vám zaslaný e-mail na potvrdenie registrácie.", "info")
            return redirect(url_for("users.login"))

        except Exception as e:
            db.session.rollback()
            current_app.logger.exception("register failed: %s", e)
            flash("Chyba pri vytváraní účtu. Skúste to znova.", "danger")

    return render_template(
        "users/register.html",
        title="Register",
        form=form,
        current_date=datetime.now(),
        next22=Next.next(),
        teamz=RightColumn.main_menu(),
        next_match=RightColumn.next_match(),
        score_table=RightColumn.score_table(),
    )


@users.route("/login", methods=["GET", "POST"])
@csrf.exempt
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user is None:
            flash("Zadaný účet neexistuje. Registrujte sa!", "danger")
            return redirect(url_for("users.login"))

        if not user.confirm:
            flash("Váš účet nie je aktivovaný. Potvrďte konfirmačný e-mail!", "danger")
            return redirect(url_for("users.login"))

        if bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)  # Flask-Login

            session.permanent = True
            session["id"] = user.id
            session["logged_in"] = True
            session["name"] = form.email.data

            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("main.home"))

        flash("Prihlásenie nebolo úspešné. Skontrolujte e-mail alebo heslo.", "danger")
        return redirect(url_for("users.login"))

    return render_template(
        "users/login.html",
        title="Login",
        form=form,
        current_date=datetime.now(),
        next22=Next.next(),
        teamz=RightColumn.main_menu(),
        next_match=RightColumn.next_match(),
        score_table=RightColumn.score_table(),
    )


@users.route("/logout")
def logout():
    try:
        if hasattr(current_user, 'exists'):
            user = User.query.get(current_user.id)
            session["name"] = None
            session['logged_in'] = False
            user.active = False
            db.session.commit()
        else:
            print("Prihlásenie neexistuje!")

        logout_user()
    except Exception as e:
        db.session.rollback()
        flash('Chyba pri odhlásení. Skúste to znova.', 'danger')
    # finally:
    #     db.session.remove()
    return redirect(url_for('main.home'))



@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    
    member = Member.query.filter_by(user_id=current_user.id).first_or_404()

    form = UpdateAccountForm()
    if form.validate_on_submit():
        try:
            if form.picture.data:
                picture_file = save_picture(form.picture.data)
                current_user.image_file = picture_file
            current_user.username = form.username.data
            current_user.email = form.email.data
            member.name = form.name.data
            member.phone = form.phone.data
            member.address = form.address.data
            member.psc = form.psc.data
            member.city = form.city.data
            db.session.commit()
            flash('Váš účet bol aktualizovaný!', 'success')
            return redirect(url_for('users.account'))
        except Exception as e:
            db.session.rollback()
            flash('Chyba pri aktualizácii účtu. Skúste to znova.', 'danger')
        # finally:
        #     db.session.remove()
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.name.data = member.name
        form.phone.data = member.phone
        form.address.data = member.address
        form.psc.data = member.psc
        form.city.data = member.city
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('users/account.html', title='Account',
                           image_file=image_file, form=form, current_date=datetime.now(), next22=Next.next(), teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())



@users.route("/user/<string:username>")
@login_required
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('users/user_posts.html', posts=posts, user=user, current_date=datetime.now(), next22=Next.next(), teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())



@users.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    form = RequestResetForm()
    if form.validate_on_submit():
        email = (form.email.data or "").strip().lower()

        user = User.query.filter(func.lower(User.email) == email).first()

        current_app.logger.warning("RESET_REQUEST email=%s user_found=%s", email, bool(user))

        if user:
            current_app.logger.warning("RESET_REQUEST sending mail to user_id=%s", user.id)
            send_reset_email(user)

        flash("Bol vám odoslaný e-mail s inštrukciami.", "info")
        return redirect(url_for("users.login"))

    return render_template('users/reset_request.html', title='Reset Password', form=form, current_date=datetime.now(), next22=Next.next(), teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('Použitý token je expirovaný.', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Vaše heslo bolo zmenené! Môžete sa prihlásiť.', 'success')
        return redirect(url_for('users.login'))
    return render_template('users/reset_token.html', title='Reset Password', form=form, current_date=datetime.now(), next22=Next.next(), teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())



# @users.route("/confirm_email", methods=['GET', 'POST'])
# def confirm_request():
#     if current_user.is_authenticated:
#         return redirect(url_for('main.home'))
#     form = RequestResetForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(email=form.email.data).first()
#         send_reset_email(user)
#         flash('An email has been sent with instructions to reset your password.', 'info')
#         return redirect(url_for('users.login'))
#     return render_template('users/reset_request.html', title='Reset Password', form=form, current_date=datetime.now(), next22=Next.next(), teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())


@users.route("/confirm_email/<token>", methods=['GET', 'POST'])
def confirm_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_confirm_token(token)
    if user is None:
        flash('Použitý token je expirovaný.', 'warning')
        return redirect(url_for('users.register'))
    else:
        user.confirm = True
        db.session.commit()
        flash('Váš e-mail bol úspešne potvrdený! Vitajte v klube. Môžete sa prihlásiť.', 'success')
        return redirect(url_for('users.login'))
    # return render_template('users/confirm_email.html', title='Confirm Register Email', form=form, current_date=datetime.now(), next22=Next.next(), teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())





################  ROLES  #################

@users.route("/users/roles")
@login_required
def list_roles():
    roles = Role.query.order_by(Role.id.desc()).all()
    return render_template('users/list_roles.html', roles=roles, current_date=datetime.now(), next22=Next.next(), teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())


@users.route("/users/role/new", methods=['GET', 'POST'])
@login_required
def new_role():
    form = RolesForm()
    if form.validate_on_submit():
        role = Role(name=form.name.data)
        db.session.add(role)
        db.session.commit()
        flash('Your Role has been created!', 'success')
        return redirect(url_for('users.list_roles'))
    return render_template('users/create_role.html', title='New Role',
                           form=form, legend='New Role', current_date=datetime.now(), next22=Next.next(), teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())


# @users.route("/users/role/<int:role_id>")
# def role(role_id):
#     category = Category.query.get_or_404(category_id)
#     return render_template('posts/category.html', name=category.name, category=category)


@users.route("/users/role/<int:role_id>/update", methods=['GET', 'POST'])
@login_required
@roles_required('Admin')
def update_role(role_id):
    role = Role.query.get_or_404(role_id)
    # if post.author != current_user:
    #     abort(403)
    form = RolesForm()
    if form.validate_on_submit():
        role.name = form.name.data
        role.description = form.description.data
        db.session.commit()
        flash('A role has been updated!', 'success')
        return redirect(url_for('users.list_roles', role_id=role.id))
    elif request.method == 'GET':
        form.name.data = role.name
        form.description.data = role.description
    return render_template('users/create_role.html', title='Update Role',
                           form=form, legend='Update Role', current_date=datetime.now(), next22=Next.next(), teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())


from sqlalchemy import exists
from flask import redirect, url_for, flash
# from flask_security import roles_required
from flask_login import login_required

@users.route("/users/role/<int:role_id>/delete", methods=["POST"])
@csrf.exempt
@login_required
@roles_required("Admin")
def delete_role(role_id):
    role = Role.query.get_or_404(role_id)

    role_in_use = db.session.query(
        exists().where(roles_users.c.role_id == role_id)
    ).scalar()

    if role_in_use:
        flash("A Role is not empty! (Some users still have it assigned.)", "warning")
        return redirect(url_for("users.list_roles"))

    db.session.delete(role)
    db.session.commit()
    flash("A Role has been deleted!", "success")
    return redirect(url_for("users.list_roles"))



################################# MEMBERS ##################################

# @users.route("/members")
# @login_required
# def list_members():
#     # page = request.args.get('page', 1, type=int)
#     # teams = Team.query.order_by(Team.id.desc()).paginate(page=page, per_page=5)
#     members = User.query.order_by(User.id.asc()).all()
#     return render_template('users/list_members.html', members=members)




from flask import request, render_template
from flask_security import login_required
from datetime import datetime

from app import db
from app.models import Member, User, Role, Team, roles_users, teams_members  # <- dôležité

@users.route("/members")
@login_required
def list_members():
    page = request.args.get("page", 1, type=int)

    role_id = request.args.get("role", type=int)   # <-- zmena: id
    team_id = request.args.get("team", type=int)
    q = (request.args.get("q") or "").strip()

    qry = (
        db.session.query(Member)
        .filter(Member.id != 1)
        .join(User, User.id == Member.user_id)
    )

    if team_id:
        qry = (qry
               .join(teams_members, teams_members.c.member_id == Member.id)
               .filter(teams_members.c.team_id == team_id))

    if role_id:
        qry = (qry
               .join(roles_users, roles_users.c.user_id == User.id)
               .filter(roles_users.c.role_id == role_id))

    if q:
        if q.isdigit():
            qry = qry.filter(Member.id == int(q))
        else:
            qry = qry.filter(Member.name.ilike(f"%{q}%"))

    members = qry.order_by(Member.id.desc()).distinct().paginate(page=page, per_page=10)

    roles = Role.query.order_by(Role.name.asc()).all()
    teams = Team.query.order_by(Team.name.asc()).all()

    wants_partial = (
        request.headers.get("X-Requested-With") == "XMLHttpRequest"
        or request.args.get("partial") == "1"
    )

    ctx = dict(
        members=members,
        roles=roles,
        teams=teams,
        active_role=role_id,   # <-- zmena: int
        active_team=team_id,
        q=q,
        current_date=datetime.now(),
        next22=Next.next(),
        teamz=RightColumn.main_menu(),
        next_match=RightColumn.next_match(),
        score_table=RightColumn.score_table(),
    )

    if wants_partial:
        return render_template("users/_members_list.html", **ctx)

    return render_template("users/list_members.html", **ctx)


@users.route("/player/<int:member_id>", methods=['POST','GET'])
def member(member_id):
    player = Player.query.filter(Player.id == member_id).first()
    if player is None:
        return "Hráč neexistuje", 404

    search = "{}%".format(player.name)
    member_obj = Member.query.filter(Member.name.like(search)).first_or_404()

    return render_template(
        'users/member.html',
        title='Player',
        legend='Player',
        player=player,
        player_info=member_obj,   # <-- OK, ale lepšie je dať aj member_id explicitne
        member_db_id=member_obj.id,
        current_date=datetime.now(),
        next22=Next.next(),
        teamz=RightColumn.main_menu(),
        next_match=RightColumn.next_match(),
        score_table=RightColumn.score_table()
    )

@users.route("/member/<int:member_id>/update", methods=['GET', 'POST'])
@csrf.exempt
@login_required
def update_member(member_id):
    member = Member.query.get_or_404(member_id)
    user = User.query.get_or_404(member.user_id)

    form = UpdateMemberForm()

    role_list = db.session.query(roles_users).filter(roles_users.c.user_id == user.id).all()
    team_list = db.session.query(teams_members).filter(teams_members.c.member_id == member_id).all()
    position_list = db.session.query(positions_members).filter(positions_members.c.member_id == member_id).all()

    form.role.choices = [(role.id, role.name) for role in Role.query.all()]
    form.team.choices = [(team.id, team.name) for team in Team.query.all()]
    form.position.choices = [(position.id, position.name) for position in Position.query.all()]

    # S3 preview
    image_url = None

    if member.image_file and member.image_file != "default.png":
        try:
            image_url = s3_presign(make_member_key(member.id, member.image_file))
        except Exception as e:
            current_app.logger.warning("member presign failed: %s", e)
            image_url = None

    if form.validate_on_submit():
        try:
            # --- upload do S3 ---
            if form.picturemember.data and getattr(form.picturemember.data, "filename", ""):
                file = form.picturemember.data

                if not allowed_file(file.filename):
                    flash("Nepodporovaný typ súboru (jpg/jpeg/png/gif/webp).", "danger")
                    return redirect(request.url)

                # zmaž starý v S3
                if member.image_file:
                    try:
                        s3_client().delete_object(
                            Bucket=BUCKET_NAME,
                            Key=make_member_key(member.id, member.image_file)
                        )
                    except Exception as e:
                        current_app.logger.warning("Old member image delete failed: %s", e)

                original = secure_filename(file.filename)
                _, ext = os.path.splitext(original)

                # ✅ FIX: image_file je VARCHAR(20) → ulož max 20 znakov
                # 16 + ".jpg"(4) = 20
                new_filename = f"{uuid.uuid4().hex[:16]}{ext.lower()}"

                s3_client().upload_fileobj(
                    file,
                    BUCKET_NAME,
                    make_member_key(member.id, new_filename),
                    ExtraArgs=s3_extra_args(file),
                )

                member.image_file = new_filename

            # --- polia člena ---
            member.name = form.name.data
            member.phone = form.phone.data
            member.address = form.address.data
            member.psc = form.psc.data
            member.city = form.city.data
            member.weight = form.weight.data
            member.height = form.height.data

            # ✅ ROLE/TEAM/POSITION – cez association tabuľky (bez .teamed/.positioned)
            db.session.execute(
                roles_users.delete().where(roles_users.c.user_id == user.id)
            )
            for rid in (form.role.data or []):
                db.session.execute(
                    roles_users.insert().values(user_id=user.id, role_id=int(rid))
                )

            db.session.execute(
                teams_members.delete().where(teams_members.c.member_id == member.id)
            )
            for tid in (form.team.data or []):
                db.session.execute(
                    teams_members.insert().values(member_id=member.id, team_id=int(tid))
                )

            db.session.execute(
                positions_members.delete().where(positions_members.c.member_id == member.id)
            )
            for pid in (form.position.data or []):
                db.session.execute(
                    positions_members.insert().values(member_id=member.id, position_id=int(pid))
                )

            db.session.commit()
            flash('A Member has been updated!', 'success')
            return redirect(url_for('users.list_members', member_id=member.id))

        except Exception as e:
            current_app.logger.exception("update_member failed: %s", e)
            db.session.rollback()
            flash('Chyba pri aktualizácii člena. Skúste to znova.', 'danger')

    elif request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
        form.name.data = member.name
        form.phone.data = member.phone
        form.address.data = member.address
        form.psc.data = member.psc
        form.city.data = member.city
        form.weight.data = member.weight
        form.height.data = member.height

        form.role.data = [r[1] for r in role_list]
        form.team.data = [t[1] for t in team_list]
        form.position.data = [p[1] for p in position_list]

    return render_template(
        'users/create_member.html',
        title='Update Member',
        form=form,
        image_url=image_url,
        member_id=member.id,
        legend='Update Member',
        current_date=datetime.now(),
        next22=Next.next(),
        teamz=RightColumn.main_menu(),
        next_match=RightColumn.next_match(),
        score_table=RightColumn.score_table()
    )



@users.route("/member/<int:member_id>/delete", methods=["POST"])
@csrf.exempt
@login_required
@roles_required("Admin")
def delete_member(member_id):
    member = Member.query.get_or_404(member_id)

    user_id = member.user_id
    user = User.query.get(user_id)

    # 1) najprv Member (tým uvoľníš FK)
    db.session.delete(member)
    db.session.flush()

    # 2) až potom User (ak chceš mazať aj user účet)
    if user:
        db.session.delete(user)

    db.session.commit()
    flash("Člen bol odstránený.", "success")
    return redirect(url_for("users.list_members"))





@users.route("/member/<int:member_id>/photo", methods=["POST"])
@login_required
@csrf.exempt
def upload_member_photo(member_id):
    member = Member.query.get_or_404(member_id)

    # povolenie: admin alebo vlastný profil
    is_admin = False
    try:
        is_admin = current_user.has_role("Admin") or current_user.has_role("WebAdmin")
    except Exception:
        pass

    if not is_admin and member.user_id != current_user.id:
        return {"error": "Forbidden"}, 403

    file = request.files.get("photo")
    if not file or not getattr(file, "filename", ""):
        return {"error": "Missing file"}, 400

    # voliteľne: jednoduchá kontrola prípony
    filename = secure_filename(file.filename).lower()
    if not (filename.endswith(".jpg") or filename.endswith(".jpeg") or filename.endswith(".png")):
        return {"error": "Only jpg/jpeg/png allowed"}, 400

    try:
        # použijeme tvoju utilitu (už to máš v imports)
        new_filename = save_picture_member(file)

        # (voliteľné) zmaž starú fotku z disku, ak chceš – nechávam bez delete
        member.image_file = new_filename
        db.session.commit()

        # vrátime URL aj s cache-bust parametrom
        img_url = url_for("static", filename=f"members_pics/{new_filename}", _external=False)
        return {"ok": True, "image_url": img_url + f"?v={uuid.uuid4().hex}"}

    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("upload_member_photo error: %s", e)
        return {"error": "Upload failed"}, 500
    # finally:
    #     db.session.remove()
        
        
@users.route("/_mail_test")
def mail_test():
    msg = Message(
        subject="test",
        recipients=["milanmartis@gmail.com"],  # dočasne
        sender=current_app.config.get("MAIL_DEFAULT_SENDER"),
        body="hello",
    )
    _send_mail(msg)
    return "ok"  

        
@users.route("/account/photo", methods=["POST"])
@login_required
@csrf.exempt
def upload_account_photo():
    file = request.files.get("photo")
    if not file or not getattr(file, "filename", ""):
        return jsonify({"error": "Missing file"}), 400

    filename = secure_filename(file.filename).lower()
    if not (filename.endswith(".jpg") or filename.endswith(".jpeg") or filename.endswith(".png")):
        return jsonify({"error": "Only jpg/jpeg/png allowed"}), 400

    try:
        picture_file = save_picture(file)
        current_user.image_file = picture_file
        db.session.commit()

        img_url = url_for("static", filename=f"profile_pics/{picture_file}", _external=False)
        return jsonify({"ok": True, "image_url": img_url + f"?v={uuid.uuid4().hex}"})
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("upload_account_photo error: %s", e)
        return jsonify({"error": "Upload failed"}), 500
    # finally:
    #     db.session.remove()