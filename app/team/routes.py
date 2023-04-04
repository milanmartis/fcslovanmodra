from flask import (render_template, url_for, flash, jsonify,
                   redirect, request, abort, Blueprint, current_app)
from app.models import Team, Events,Post, PostGallery, Category, teams_members
from flask_login import current_user, login_required
from app.team.forms import TeamForm

from flask import Blueprint
from app import db
from datetime import  timedelta
import datetime
from dateutil import parser
from flask_security import roles_accepted
from app.main.routes import main_menu


team = Blueprint('team', __name__)



@team.route("/teams")
def list_teams():
    # page = request.args.get('page', 1, type=int)
    # teams = Team.query.order_by(Team.id.desc()).paginate(page=page, per_page=5)
    teams = Team.query.order_by(Team.id.asc()).all()
    return render_template('teams/list_teams.html', teams=teams, teamz=main_menu())


@team.route("/teams/new", methods=['GET', 'POST'])
@login_required
# @roles_accepted('Admin')
def new_team():
    form = TeamForm()
    if form.validate_on_submit():
        team = Team(name=form.name.data, score_scrap=form.score_scrap.data, player_list_scrap=form.player_list_scrap.data)
        db.session.add(team)
        db.session.commit()
        flash('A New Team has been created!', 'success')
        return redirect(url_for('team.list_teams'))
    return render_template('teams/create_team.html', title='New Team',
                           form=form, legend='New Team', teamz=main_menu())


@team.route("/team/<team_name>")
def team_name(team_name):
    team = Team.query.filter(Team.name.like(team_name)).first()
    return render_template('teams/team.html', team=team, teamz=main_menu())





@team.route("/teams/<int:team_id>/update", methods=['GET', 'POST'])
@login_required
def update_team(team_id):
    team = Team.query.get_or_404(team_id)
    # if post.author != current_user:
    #     abort(403)
    form = TeamForm()
    if form.validate_on_submit():
        team.name = form.name.data
        team.score_scrap = form.score_scrap.data
        team.player_list_scrap = form.player_list_scrap.data
        db.session.commit()
        flash('A Team has been updated!', 'success')
        return redirect(url_for('team.list_teams', team_id=team.id))
    elif request.method == 'GET':
        form.name.data = team.name
        form.score_scrap.data = team.score_scrap
        form.player_list_scrap.data = team.player_list_scrap
    return render_template('teams/create_team.html', title='Update Team',
                           form=form, legend='Update Team', teamz=main_menu())


@team.route("/teams/<int:team_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_team(team_id):
    print(team_id)
    team = Team.query.get_or_404(team_id)
    ifemptyteam = db.session.query(teams_members).filter(teams_members.c.team_id==team_id).all()

    if ifemptyteam:
        flash('A Team is not empty!', 'danger')
    else:
        db.session.delete(team)
        db.session.commit()
        flash('A Team has been deleted!', 'success')

    return redirect(url_for('team.list_teams'))

