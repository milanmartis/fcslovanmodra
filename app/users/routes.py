from flask import render_template, url_for, flash, redirect, request, Blueprint, session
from flask_login import login_user, current_user, logout_user, login_required
from app import db, bcrypt
from app.models import User, Post, Role, Team, Member, Player, Position, roles_users, teams_members, positions_members
from app.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm,UpdateMemberForm,
                                   RequestResetForm, ResetPasswordForm, RolesForm)
from app.users.utils import save_picture, send_reset_email, save_picture_member
import uuid
from app.main.routes import RightColumn
from flask_security import roles_required

users = Blueprint('users', __name__)


from functools import wraps


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


@users.route("/register", methods=['GET', 'POST'])
def register():

    # if current_user.is_authenticated and not current_user.id==1:
    #     return redirect(url_for('main.home'))
    
    form = RegistrationForm()
    form.role.choices = [(role.id, role.name) for role in Role.query.all()]
    # form.team.choices = [(team.id, team.name) for team in Team.query.all()]

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(uuid=str(uuid.uuid4()), username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        role = Role.query.filter(Role.id.in_(form.role.data)).all()
        # team = Team.query.filter_by(id=form.team.data).first()
        member = Member(name=form.name.data, phone=form.phone.data, address=form.address.data, psc=form.psc.data, city=form.city.data,user_id=user.id)
        for rol in role:
            user.roles.append(rol)
        # member.teams.append(team)
        db.session.add(member)
        db.session.commit()

        flash('New account has been created!', 'success')
        if current_user.is_authenticated:
            return redirect(url_for('users.list_members'))
        else:
            return redirect(url_for('users.login'))
    
    return render_template('users/register.html', title='Register', form=form, teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())


@users.route("/login", methods=['GET', 'POST'])
def login():

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            session.permanent = True
            session['logged_in'] = True
            session["name"] = form.email.data
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('users/login.html', title='Login', form=form, teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())


@users.route("/logout")
def logout():
    session["name"] = None
    session['logged_in'] = False

    logout_user()
    return redirect(url_for('main.home'))



@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    
    member = Member.query.filter_by(user_id=current_user.id).first_or_404()

    form = UpdateAccountForm()
    if form.validate_on_submit():
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
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account'))
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
                           image_file=image_file, form=form, teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())



@users.route("/user/<string:username>")
@login_required
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('users/user_posts.html', posts=posts, user=user, teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())



@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('users.login'))
    return render_template('users/reset_request.html', title='Reset Password', form=form, teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('users/reset_token.html', title='Reset Password', form=form, teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())





################  ROLES  #################

@users.route("/users/roles")
@login_required
def list_roles():
    roles = Role.query.order_by(Role.id.desc()).all()
    return render_template('users/list_roles.html', roles=roles, teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())


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
                           form=form, legend='New Role', teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())


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
                           form=form, legend='Update Role', teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())


@users.route("/users/role/<int:role_id>/delete", methods=['POST'])
@login_required
@roles_required('Admin')
def delete_role(role_id):
    role = Role.query.get_or_404(role_id)
    ifemptyrole = db.session.query(roles_users).filter(roles_users.c.role_id==role_id).all()

    if ifemptyrole:
        flash('A Role is not empty!', 'success')
    else:
        db.session.delete(role)
        db.session.commit()
        flash('A Role has been deleted!', 'success')
    flash('A role has been deleted!', 'success')
    return redirect(url_for('users.list_roles'))



################################# MEMBERS ##################################

# @users.route("/members")
# @login_required
# def list_members():
#     # page = request.args.get('page', 1, type=int)
#     # teams = Team.query.order_by(Team.id.desc()).paginate(page=page, per_page=5)
#     members = User.query.order_by(User.id.asc()).all()
#     return render_template('users/list_members.html', members=members)




@users.route("/members")
@login_required
@roles_required('Admin')
def list_members():
    page = request.args.get('page', 1, type=int)
    members = Member.query.filter(Member.id!=1).order_by(Member.id.desc()).paginate(page=page, per_page=10)
    return render_template('users/list_members.html', members=members, teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())



@users.route("/player/<int:member_id>", methods=['GET'])
def member(member_id):
    
    player = Member.query.get_or_404(member_id)
    print(player.name)
    player_info = Player.query.filter(Player.name.like(player.name)).first()
    
    
    return render_template('users/member.html', title='Player',
                           legend='Player', player=player, player_info=player_info, teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())
    



@users.route("/member/<int:member_id>/update", methods=['GET', 'POST'])
@login_required
@roles_required('Admin')
def update_member(member_id):

    # member = Member.query.join(Role, roles_members).filter(Role.id==roles_members.c.role_id).filter(Member.id==member_id)

    member = Member.query.get_or_404(member_id)
    user = User.query.get_or_404(member.user_id)
   
    form = UpdateMemberForm()
    role_list = db.session.query(roles_users).filter(roles_users.c.user_id==user.id).all()
    team_list = db.session.query(teams_members).filter(teams_members.c.member_id==member_id).all()
    position_list = db.session.query(positions_members).filter(positions_members.c.member_id==member_id).all()

    form.role.choices = [(role.id, role.name) for role in Role.query.all()]
    # form.role.choices = [(role.id, role.name) for role in Role.query.filter(Role.id.not_in([1])).all()]
    form.team.choices = [(team.id, team.name) for team in Team.query.all()]
    form.position.choices = [(position.id, position.name) for position in Position.query.all()]

    if form.validate_on_submit():
        if form.picturemember.data:
            picture_file = save_picture_member(form.picturemember.data)
            member.image_file = picture_file
        member.name = form.name.data
        member.phone = form.phone.data
        member.address = form.address.data
        member.psc = form.psc.data
        member.city = form.city.data
        member.weight = form.weight.data
        member.height = form.height.data
        # member.position = form.position.data
        db.session.commit()

############ ROLE
        for data in role_list:
            role = Role.query.filter_by(id=data[1]).first()
            role.roled.remove(user)
            db.session.commit()

        for data in form.role.data:
            role = Role.query.filter_by(id=data).first()
            role.roled.append(user)
            db.session.commit()

############ TEAM
        for data2 in team_list:
            team = Team.query.filter_by(id=data2[1]).first()
            team.teamed.remove(member)
            db.session.commit()

        for data2 in form.team.data:
            team = Team.query.filter_by(id=data2).first()
            team.teamed.append(member)
            db.session.commit()
        
############ POSITION
        for data3 in position_list:
            position = Position.query.filter_by(id=data3[1]).first()
            position.positioned.remove(member)
            db.session.commit()

        print(form.position.data)

        for data3 in form.position.data:
            position = Position.query.filter_by(id=data3).first()
            position.positioned.append(member)
            db.session.commit()
        
        flash('A Member has been updated!', 'success')
        return redirect(url_for('users.list_members', member_id=member.id))
    
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

        rolelist=[]
        for rol in role_list:
            rolelist.append(rol[1])
        form.role.data = rolelist

        teamlist=[]
        for team in team_list:
            teamlist.append(team[1])
        form.team.data = teamlist

        positionlist=[]
        for position in position_list:
            positionlist.append(position[1])
        form.position.data = positionlist


    image_file = url_for('static', filename='members_pics/' + member.image_file)
    return render_template('users/create_member.html', title='Update Member',
                           form=form, image_file=image_file, legend='Update Member', teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())


@users.route("/member/<int:member_id>/delete", methods=['GET', 'POST'])
@login_required
@roles_required('Admin')
def delete_member(member_id):
    member = Member.query.get_or_404(member_id)
    user = User.query.get_or_404(member.user_id)
    db.session.delete(member)
    db.session.delete(user)
    db.session.commit()
    flash('A Member has been deleted!', 'success')
    return redirect(url_for('users.list_members'))




