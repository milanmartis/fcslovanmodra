from flask import render_template, url_for, request, redirect, jsonify, Blueprint
from app.models import Event, PostGallery, Category, Team, EventCategory
from flask_login import current_user, login_required
from app.calendar.forms import EventForm, UpdateEventForm
from flask import Blueprint
from app import db
from datetime import  timedelta
import datetime
from dateutil import parser
from flask_security import roles_required
from app.main.routes import RightColumn

calendar = Blueprint('calendar', __name__)



@calendar.route("/calendar",methods=["POST","GET"])
@login_required
def index():
    calendar = Event.query.all()
    form = EventForm()
    form.team.choices = [(team.id, team.name) for team in Team.query.all()]
    form.category.choices = [(category.id, category.name) for category in EventCategory.query.all()]
    form2 = UpdateEventForm()
    form2.category2.choices = [(category.id, category.name) for category in EventCategory.query.all()]
    form2.team2.choices = [(team.id, team.name) for team in Team.query.all()]
    return render_template('calendar/calendar.html', form=form,form2=form2, calendar=calendar, teamz=RightColumn.main_menu(), next_match=RightColumn.next_match(), score_table=RightColumn.score_table())


@calendar.route("/calendar/insert",methods=["POST","GET"])
@login_required
@roles_required('Admin')
def insert():
    
    form = EventForm()
    
    form.team.choices = [(team.id, team.name) for team in Team.query.all()]
    form.category.choices = [(category.id, category.name) for category in EventCategory.query.all()]

    if request.method == 'POST':
        # db.session.rollback()
        # title = request.form['title']
        # start = parser.isoparse(request.form['start'])
        # end = parser.isoparse(request.form['end'])
        # id = request.form['id']
        
        print(request.form.getlist('team'))

        teamz = Team.query.filter(Team.id.in_((request.form.getlist('team')))).all()
        event = Event(title=form.title.data, start_event=parser.isoparse(request.form['start']),end_event=parser.isoparse(request.form['end']), 
                      user_id=current_user.id, event_category_id=request.form['category'], event_team_id=request.form['team'])
        # for team in teamz:
        #     event.teams.append(team)
        db.session.add(event)
        db.session.commit()  

     
        new_id_event = event.id
    
    return jsonify(new_id_event)    



  

# @calendar.route("/calendar/<int:event_id>/update", methods=["POST","GET"])
# def event_update(event_id):
    
#     event = Event.query.get(event_id)
#     calendar = Event.query.all()
    
#     if request.method == 'POST':
#         title = request.form['title']
#         start = parser.isoparse(request.form['start'])
#         end = parser.isoparse(request.form['end'])
#         id = request.form['id']
        
#         event.title = title
#         event.start_event = start
#         event.end_event = end
#         event.event_category_id = 222
#         db.session.commit()  
#         db.session.close()
    

#     return render_template('calendar/event.html', event=event, calendar=calendar)






@calendar.route("/calendar/update", methods=["POST","GET"])
@login_required
@roles_required('Admin','Trener')
def update():
    
    form2 = UpdateEventForm()
    

    form2.team2.choices = [(team.id, team.name) for team in Team.query.all()]
    form2.category2.choices = [(category.id, category.name) for category in EventCategory.query.all()]
    
    if request.method == 'POST':
        # team_list = db.session.query(teams_events).filter(teams_events.c.event_id==request.form['id']).all()
        title = request.form['title']
        start = parser.isoparse(request.form['start'])
        end = parser.isoparse(request.form['end'])
        id = request.form['id']
        event = Event.query.get(int(id))
        event.title = title
        event.start_event = start
        event.end_event = end
        event.event_category_id = request.form['category']
        event.event_team_id = request.form['team']
        # print('-------------------------')
        # print(team_list)
        # print('-------------------------')
        
        ############ Team&Event
        # for data2 in team_list:
        #     team = Team.query.filter_by(id=data2[1]).first()
        #     team.teamed.remove(event)
        #     db.session.commit()

        # for data2 in request.form['team']:
        #     team = Team.query.filter_by(id=data2).first()
        #     team.teamed.append(event)
        #     db.session.commit()

        
        db.session.commit()
        msg = 'success' 

    elif request.method == 'GET':
        
        request.form['title'] = event.title
        request.form['start'] = event.start_event
        request.form['end'] = event.end_event
        request.form['id'] = event.id
        request.form['team'] = event.teams
        request.form['category'] = event.event_category_id
        
    return jsonify(msg)    
  

@calendar.route("/calendar/ajax_delete", methods=["POST","GET"])
def ajax_delete():
    if request.method == 'POST':
        getid = request.form['id']
        # Events.query.filter(Events.id == getid).delete()
        u = db.session.get(Event, getid)
        db.session.delete(u)
        db.session.commit()
        msg = 'Record deleted successfully' 
    return jsonify(getid) 
  
