
# from flask_login import current_user
# from app import db
# from app.models import Role, roles_users
# from functools import wraps



# # role = 'ff'
# def user_role(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if current_user.is_authenticated:
#             role = []
#             roles = db.session.query(Role.name).filter(roles_users.c.user_id==current_user.id).filter(Role.id==roles_users.c.role_id).all()
#             for rol in roles:
#                 role.append(rol)

#             return role
#         return f(*args, **kwargs)
        
#     return decorated_function
    
