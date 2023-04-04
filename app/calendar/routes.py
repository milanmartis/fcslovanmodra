from flask import render_template, url_for, request, redirect, jsonify, Blueprint
from app.models import Events,Post, PostGallery, Category
from flask_login import current_user, login_required

from flask import Blueprint
from app import db
from datetime import  timedelta
import datetime
from dateutil import parser

calendar = Blueprint('calendar', __name__)


@calendar.route('/calendar')
def index():
    calendar = Events.query.all()
    return render_template('calendar/calendar.html', calendar = calendar)


@calendar.route("/calendar/insert",methods=["POST","GET"])
@login_required
def insert():
    if request.method == 'POST':
        db.session.rollback()
        title = request.form['title']
        # start = request.form['start']
        # end = request.form['end']
        start = parser.isoparse(request.form['start'])
        end = parser.isoparse(request.form['end'])
        print(title)     
        print('----------------------------')     
        print(start)  
        event = Events(title=title, start_event=start,end_event=end, user_id=current_user.id)
        db.session.add(event)
        db.session.commit()  
        db.session.close()
     
        msg = 'success' 
    
    calendar = Events.query.all()
        # return redirect(url_for('calendar.index'))
    # 
    return render_template('calendar/calendar.html', calendar = calendar)
    # return jsonify(msg)
  


  

@calendar.route("/calendar/<int:event_id>/update", methods=["POST","GET"])
def event_update(event_id):

    calendar = Events.query.all()
    event = Events.query.get(event_id)


    return render_template('calendar/event.html', event = event, calendar = calendar)






@calendar.route("/calendar/update", methods=["POST","GET"])
def update():
    if request.method == 'POST':
        title = request.form['title']
        start = parser.isoparse(request.form['start'])
        end = parser.isoparse(request.form['end'])
        id = request.form['id']
        print(start)
        print(end)
        print(title)
        print(id)

        event = Events.query.get(id)
        event.title = title

        event.start_event = start
        event.end_event = end


        # u = update(Events)
        # u = u.values({"title": title, "start_event": start, "start_end": end})
        # u = u.where(Events.id == id)
        # db.session.execute(event)
        db.session.commit()
        db.session.close()

        msg = 'success' 
    return jsonify(msg)    
  

@calendar.route("/calendar/ajax_delete",methods=["POST","GET"])
def ajax_delete():
    if request.method == 'POST':
        getid = request.form['id']
        # Events.query.filter(Events.id == getid).delete()
        u = db.session.get(Events, getid)
        db.session.delete(u)
        db.session.commit()
        msg = 'Record deleted successfully' 
    return jsonify(getid) 
  
