from app.models import Post, PostGallery, Category, Team, Event, ScoreTable
from app import db


class RightColumn:
    def main_menu():
        menuteam = Team.query.all()
        return menuteam

    def next_match():
        next_match = db.session.query(Event).filter(Event.event_team_id==1).order_by(Event.start_event.asc()).first()
        return next_match

    def score_table():
        score_table = ScoreTable.query.all()
        return score_table