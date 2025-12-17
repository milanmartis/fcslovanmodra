from flask import render_template, url_for, request, redirect, jsonify, Blueprint, flash
from app.models import Event, PostGallery, Category, Team, EventCategory
# from flask_login import current_user, login_required
from app.calendar.forms import EventForm, UpdateEventForm
from app.main.routes import RightColumn
from app.main.routes import Next
from flask import Blueprint
from app import db
from datetime import  timedelta
from datetime import datetime
from dateutil import parser
# from flask_security import roles_required
from flask import current_app
from flask_login import login_user, current_user, logout_user, login_required
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
calendar = Blueprint('calendar', __name__)




@calendar.route("/calendar", methods=["GET"])
@login_required
def index():
    current_app.logger.info("calendar.index START")

    try:
        events = Event.query.all()
        current_app.logger.info("calendar.index: events OK, count=%s", len(events))

        teams = Team.query.all()
        cats = EventCategory.query.all()
        current_app.logger.info("calendar.index: teams=%s, cats=%s", len(teams), len(cats))

        form = EventForm()
        form.team.choices = [(t.id, t.name) for t in teams]
        form.category.choices = [(c.id, c.name) for c in cats]

        form2 = UpdateEventForm()
        form2.team2.choices = [(t.id, t.name) for t in teams]
        form2.category2.choices = [(c.id, c.name) for c in cats]

        current_app.logger.info("calendar.index: pred RightColumn/Next")
        next22 = Next.next()
        teamz = RightColumn.main_menu()
        next_match = RightColumn.next_match()
        score_table = RightColumn.score_table()
        current_app.logger.info("calendar.index: RightColumn/Next OK")

        resp = render_template(
            'calendar/calendar.html',
            form=form,
            form2=form2,
            calendar=events,
            current_date=datetime.now(),
            next22=next22,
            teamz=teamz,
            next_match=next_match,
            score_table=score_table
        )
        current_app.logger.info("calendar.index END OK")
        return resp

    except Exception:
        current_app.logger.exception("calendar.index ERROR")
        return "Chyba pri načítaní kalendára", 500


@calendar.route("/calendar/insert",methods=["POST"])
@login_required
@roles_required('Admin')
def insert():
    
    form = EventForm()
    data = request.get_json()
    

    if data:
        try:
            form.team.choices = [(team.id, team.name) for team in Team.query.all()]
            form.category.choices = [(category.id, category.name) for category in EventCategory.query.all()]
            # print(form.title.data)
            # db.session.rollback()
            # title = request.form['title']
            # start = parser.isoparse(request.form['start'])
            # end = parser.isoparse(request.form['end'])
            # id = request.form['id']
            
            # print(request.form.getlist('team'))

            # teamz = Team.query.filter(Team.id.in_(data['team'])).all()
            event = Event(
                title=data['title'], 
                start_event=parser.isoparse(data['start']),
                end_event=parser.isoparse(data['end']), 
                user_id=current_user.id, 
                address=data['address'], 
                link=data['link'], 
                event_category_id=data['category'], 
                event_team_id=data['team']
            )
            # for team in teamz:
            #     event.teams.append(team)
            db.session.add(event)
            db.session.commit()  

        
            new_id_event = event.id
        
            return jsonify(new_id_event)  
        except Exception as e:
            db.session.rollback()
            flash('Chyba pri pridávaní udalosti. Skúste to znova.', 'danger')
            return jsonify({"error": "Chyba pri pridávaní udalosti"}), 500
        finally:
            db.session.remove()


  

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
@roles_required('Admin', 'Trener')
def update():
    
    form2 = UpdateEventForm()
    data = request.get_json()


    form2.team2.choices = [(team.id, team.name) for team in Team.query.all()]
    form2.category2.choices = [(category.id, category.name) for category in EventCategory.query.all()]
    
    if request.method == 'POST':
        try:
            # team_list = db.session.query(teams_events).filter(teams_events.c.event_id==request.form['id']).all()
            title = data['title2']
            start = parser.isoparse(data['start2'])
            end = parser.isoparse(data['end2'])
            id = data['id2']
            address = data['address2']
            link = data['link2']
            event = Event.query.get(int(id))
            event.title = title
            event.start_event = start
            event.end_event = end
            event.address = address
            event.link = link
            event.event_category_id = data['category2']
            event.event_team_id = data['team2']
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
            return jsonify('success')
        except Exception as e:
            db.session.rollback()
            flash('Chyba pri aktualizácii udalosti. Skúste to znova.', 'danger')
            return jsonify({"error": "Chyba pri aktualizácii udalosti"}), 500
        finally:
            db.session.remove()

    elif request.method == 'GET':
        try:     
            request.form['title'] = event.title
            request.form['start'] = event.start_event
            request.form['end'] = event.end_event
            request.form['id'] = event.id
            request.form['team'] = event.teams
            request.form['category'] = event.event_category_id
            request.form['address'] = event.address
            request.form['link'] = event.link
        except Exception as e:
            flash('Chyba pri načítaní údajov udalosti.', 'danger')
        finally:
            db.session.remove()
        
  

@calendar.route("/calendar/ajax_delete", methods=["POST"])
def ajax_delete():
    data = request.get_json()

    if data:
        try:
            getid = data['id']
            # Events.query.filter(Events.id == getid).delete()
            u = db.session.get(Event, getid)
            db.session.delete(u)
            db.session.commit()
            msg = 'Record deleted successfully' 
            return jsonify(getid) 
        except Exception as e:
            db.session.rollback()
            flash('Chyba pri mazaní udalosti. Skúste to znova.', 'danger')
            return jsonify({"error": "Chyba pri mazaní udalosti"}), 500
        finally:
            db.session.remove()
  
