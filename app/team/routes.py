from flask import (render_template, url_for, flash, jsonify,
                   redirect, request, abort, Blueprint, current_app)
from app.models import Team, ScoreTable, User, Player, Position, Member,Post, PostGallery, Category, teams_members, positions_members
from flask_login import current_user, login_required
from app.team.forms import TeamForm

from flask import Blueprint
from app import db
from datetime import  timedelta
import datetime
from dateutil import parser
from flask_security import roles_accepted
from app.main.routes import RightColumn
from app.main.routes import Next
from flask_security import roles_required
import pandas as pd
import numpy as np

team = Blueprint('team', __name__)



@team.route("/teams")
@login_required
@roles_required('Admin', 'WebAdmin')
def list_teams():
    # page = request.args.get('page', 1, type=int)
    # teams = Team.query.order_by(Team.id.desc()).paginate(page=page, per_page=5)
    teams = Team.query.order_by(Team.id.asc()).all()
    return render_template('teams/list_teams.html', teams=teams, next22=Next.next(), teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())


@team.route("/teams/new", methods=['GET', 'POST'])
@login_required
@roles_required('Admin', 'WebAdmin')
def new_team():
    form = TeamForm()
    if form.validate_on_submit():
        team = Team(name=form.name.data, score_scrap=form.score_scrap.data, player_list_scrap=form.player_list_scrap.data)
        db.session.add(team)
        db.session.commit()
        flash('A New Team has been created!', 'success')
        return redirect(url_for('team.list_teams'))
    return render_template('teams/create_team.html', title='New Team',
                           form=form, legend='New Team', next22=Next.next(), teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())


@team.route("/info")
def team_youth():

    # team = Member.query.filter(Member.id==teams_members.c.member_id).filter(Member.id==positions_members.c.member_id).filter(teams_members.c.team_id==Team.id).filter(positions_members.c.position_id==Position.id).all()
    return render_template('teams/youth.html', next22=Next.next(), teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())


@team.route("/team/<team_name>")
def team_name(team_name):
    # members = Member.query.join(User.roles, Member.position, Member.teams).filter(Team.name.like(team_name)).all()
    # trener = Member.query.join(User.roles, Member.position, Member.teams).filter(Team.name.like(team_name)).all()
    trener = (
    Member.query
    .join(User.roles)
    .join(Member.position)
    .join(Member.teams)
    .filter(Team.name.like(team_name))
    .all()
)
    
    members = Player.query.filter(Team.id == Player.team_id).filter(Team.name.like(team_name)).all()

    team = Team.query.filter(Team.name.like(team_name)).first()
    # team = Member.query.filter(Member.id==teams_members.c.member_id).filter(Member.id==positions_members.c.member_id).filter(teams_members.c.team_id==Team.id).filter(positions_members.c.position_id==Position.id).all()
    return render_template('teams/team.html', team=team, members=members, trener=trener, next22=Next.next(), teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())



# @team.route("/team/<team_name>/table")
# def team_name(team_name):
#     team = Team.query.filter(Team.name.like(team_name)).first()
#     return render_template('teams/team_table.html', team=team, teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())





@team.route("/teams/<int:team_id>/update", methods=['GET', 'POST'])
@login_required
@roles_required('Admin', 'WebAdmin')
def update_team(team_id):
    team = Team.query.get_or_404(team_id)
    form = TeamForm()
    
    score_scrap = request.form.get("score_scrap")
    print(score_scrap)
        
    if request.form.get('what') and team.score_scrap and score_scrap:
        
        ScoreTable.query.filter(ScoreTable.team_id == team_id).delete()

        
        df = pd.read_html(score_scrap)
        ###########################################################################################
        # df = pd.DataFrame(df, index=labels)
        x = int(len(df))

        for i in range(0, x):
            df[i] = df[i][['Klub', 'Z', 'V', 'R', 'P', 'Skóre', 'B']]
            # df[i] = pd.DataFrame(df[i], index=range(1, 16)+1)
            # df[i] = df[i].dropna(subset = ['Klub'])
            # df['Klub'] = df['Klub'].replace(np.nan, 'Inter')
            df[i] = df[i].replace(np.nan, '', regex=True)
            df[i].index = df[i].index + 1
            df[i]['team_id'] = team_id
            # rec = df[i].head(100).to_records().tolist()
            # score_team[i] = ScoreTable(club=rec[i][1],games=rec[i][2],wins=rec[i][3],draws=rec[i][4],loses=rec[i][5], score=rec[i][6], points=rec[i][7], team_id=team_id)
            # db.session.add(score_team[i])

            records_to_insert = df[i].head(100).to_records()

        # cursor = connection.cursor()
        # cursor.executemany(mySql_insert_query, records_to_insert)
        # connection.commit()
        # print(records_to_insert)
        for rec in records_to_insert:
            score_team = ScoreTable(club=rec[1],games=int(rec[2]),wins=int(rec[3]),draws=int(rec[4]),loses=int(rec[5]), score=rec[6], points=int(rec[7]), team_id=team_id)
            db.session.add(score_team)
            # print(rec[1])
        db.session.commit()



    player_list_scrap = request.form.get("player_list_scrap")
        
    if  request.form.get('what') and team.player_list_scrap and player_list_scrap:
        
        Player.query.filter(Player.team_id == team_id).delete()
        
        df = pd.read_html(player_list_scrap)

        x = int(len(df))

        for i in range(0, x):
            
            if i == 0:
                pozicia = 1
                # df[i] = df[i].set_index(pozicia)

            if i == 1:
                pozicia = 2
                # df[i] = df[i].set_index(pozicia)

            if i == 2:
                pozicia = 3
                # df[i] = df[i].set_index(pozicia)

            if i == 3:
                pozicia = 4
                # df[i] = df[i].set_index(pozicia)

            df[i]['pozicia'] = pozicia
            df[i]['team'] = team_id
            
            records_to_insert = df[i].head(100).to_records().tolist()
            
            print(records_to_insert)


            for rec in records_to_insert:
                score_team = Player(name=rec[1], position=rec[5], team=team_id, score=int(rec[2]), yellow_card=int(rec[3]), red_card=rec[4], team_id=team_id)
                db.session.add(score_team)
                # print(rec[1])
        db.session.commit()
        
         
    
    # if post.author != current_user:
    #     abort(403)
    if form.validate_on_submit():
        team.name = form.name.data
        team.main_league = form.main_league.data
        team.score_scrap = form.score_scrap.data
        team.player_list_scrap = form.player_list_scrap.data
        db.session.commit()
        flash('A Team has been updated!', 'success')
        return redirect(url_for('team.list_teams', team_id=team.id))
    elif request.method == 'GET':
        form.name.data = team.name
        form.main_league.data = team.main_league
        form.score_scrap.data = team.score_scrap
        form.player_list_scrap.data = team.player_list_scrap
    return render_template('teams/create_team.html', title='Update Team',
                           form=form, team=team, legend='Update Team', next22=Next.next(), teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())


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

