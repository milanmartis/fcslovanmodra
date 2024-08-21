from flask import render_template, url_for, flash, jsonify, redirect, request, abort, Blueprint, current_app
from app.models import Team, ScoreTable, User, Player, Position, Member, Post, PostGallery, Category, teams_members, positions_members
from flask_login import current_user
from app.team.forms import TeamForm
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm import joinedload
from flask import Blueprint
from app import db
from datetime import timedelta, datetime
from dateutil import parser
from app.main.routes import RightColumn, Next
from flask_login import login_required
from flask_security import roles_required
import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import os
from dotenv import load_dotenv

load_dotenv()
from time import sleep


team = Blueprint('team', __name__)

@team.route("/teams")
@login_required
@roles_required('Admin', 'WebAdmin')
def list_teams():
    teams = Team.query.order_by(Team.id.asc()).all()
    return render_template('teams/list_teams.html', teams=teams, current_date=datetime.now(), next22=Next.next(), teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())


@team.route("/teams/new", methods=['GET', 'POST'])
@login_required
def new_team():
    form = TeamForm()
    if form.validate_on_submit():
        try:
            team = Team(name=form.name.data, score_scrap=form.score_scrap.data, player_list_scrap=form.player_list_scrap.data)
            db.session.add(team)
            db.session.commit()
            flash('A New Team has been created!', 'success')
            return redirect(url_for('team.list_teams'))
        except Exception as e:
            db.session.rollback()
            flash('Chyba pri vytváraní tímu. Skúste to znova.', 'danger')
        finally:
            db.session.remove()
    return render_template('teams/create_team.html', title='New Team',
                           form=form, legend='New Team', current_date=datetime.now(), next22=Next.next(), teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())


@team.route("/info")
def team_youth():
    return render_template('teams/youth.html', current_date=datetime.now(), next22=Next.next(), teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())


@team.route("/team/<team_name>")
def team_name(team_name):
    try:
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
        return render_template('teams/team.html', team=team, members=members, trener=trener, current_date=datetime.now(), next22=Next.next(), teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())
    except Exception as e:
        flash('Chyba pri načítavaní tímu. Skúste to znova.', 'danger')
    finally:
        db.session.remove()


@team.route("/teams/<int:team_id>/update", methods=['GET', 'POST'])
@login_required
def update_team(team_id):
    try:


        team = Team.query.get_or_404(team_id)
        form = TeamForm()

        score_scrap = request.form.get("score_scrap")

        if request.form.get('what') and team.score_scrap and score_scrap:
            ScoreTable.query.filter(ScoreTable.team_id == team_id).delete()

            s = Service(r'C:\Users\Dell\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe')
            driver = webdriver.Chrome(service=s)
            driver.get(score_scrap)
            sleep(5)
            html = driver.page_source
            driver.quit()

            df = pd.read_html(html)
            x = int(len(df))

            for i in range(0, x):
                df[i] = df[i][['Klub', 'Z', 'V', 'R', 'P', 'Skóre', 'B']]
                df[i] = df[i].replace(np.nan, '', regex=True)
                df[i].index = df[i].index + 1
                df[i]['team_id'] = team_id
                records_to_insert = df[i].head(100).to_records()

            for rec in records_to_insert:
                score_team = ScoreTable(
                    club=rec[1],
                    games=int(rec[2]),
                    wins=int(rec[3]),
                    draws=int(rec[4]),
                    loses=int(rec[5]),
                    score=rec[6],
                    points=int(rec[7]),
                    team_id=team_id
                )
                db.session.add(score_team)
            db.session.commit()

        player_list_scrap = request.form.get("player_list_scrap")
        
        if request.form.get('what') and team.player_list_scrap and player_list_scrap:
            Player.query.filter(Player.team_id == team_id).delete()

            s = Service(r'C:\Users\Dell\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe')
            driver2 = webdriver.Chrome(service=s)
            driver2.get(player_list_scrap)
            sleep(5)
            html_list_scrap = driver2.page_source
            driver2.quit()

            df = pd.read_html(html_list_scrap)
            x = int(len(df))

            for i in range(0, x):
                pozicia = i + 1
                df[i]['pozicia'] = pozicia
                df[i]['team'] = team_id
                records_to_insert = df[i].head(100).to_records().tolist()

                for rec in records_to_insert:
                    score_team = Player(
                        name=rec[1],
                        position=rec[5],
                        team=team_id,
                        score=int(rec[2]),
                        yellow_card=int(rec[3]),
                        red_card=rec[4],
                        team_id=team_id
                    )
                    db.session.add(score_team)
            db.session.commit()

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
    except Exception as e:
        db.session.rollback()
        flash('Chyba pri aktualizácii tímu. Skúste to znova.', 'danger')
    finally:
        db.session.remove()
    return render_template('teams/create_team.html', title='Update Team',
                           form=form, team=team, legend='Update Team', current_date=datetime.now(), next22=Next.next(), teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())


@team.route("/teams/<int:team_id>/delete", methods=['GET', 'POST'])
@login_required
@roles_required('Admin', 'WebAdmin')
def delete_team(team_id):
    try:
        team = Team.query.get_or_404(team_id)
        ifemptyteam = db.session.query(teams_members).filter(teams_members.c.team_id == team_id).all()

        if ifemptyteam:
            flash('A Team is not empty!', 'danger')
        else:
            db.session.delete(team)
            db.session.commit()
            flash('A Team has been deleted!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Chyba pri mazaní tímu. Skúste to znova.', 'danger')
    finally:
        db.session.remove()
    return redirect(url_for('team.list_teams'))