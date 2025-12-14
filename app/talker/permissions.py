from flask_security import current_user
from app.models import Member, TalkRoom

def is_admin_user() -> bool:
    try:
        return current_user.has_role("Admin") or current_user.has_role("WebAdmin")
    except Exception:
        return False

def user_can_access_room(room: TalkRoom) -> bool:
    if not current_user.is_authenticated:
        return False

    if is_admin_user():
        return True

    # custom room (team_id None): len ak je user v members
    if room.team_id is None:
        return any(u.id == current_user.id for u in room.members)

    # team room: user musí patriť do teamu
    member = Member.query.filter_by(user_id=current_user.id).first()
    if not member:
        return False

    return any(t.id == room.team_id for t in member.teams)
