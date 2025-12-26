# run.py
# from app import create_app, db
# import os

# app = create_app()

# if __name__ == '__main__':
#     # TOTO je už len na lokálny dev server
#     port = int(os.environ.get('PORT', 5000))
#     app.run(debug=True, host='0.0.0.0', port=port)


# from app import create_app, db
# app = create_app()
# import os



# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#         port = int(os.environ.get('PORT', 5000))
#         app.run(debug=True, host='0.0.0.0', port = port)
#         # app.run(debug=True, host='0.0.0.0', port = port, use_reloader=True)


# from app import create_app, db
# import os

# app = create_app()

# if __name__ == "__main__":
#     with app.app_context():
#         db.create_all()

#     port = int(os.environ.get("PORT", 5000))

#     # debug=True automaticky zapne reloader,
#     # ale dávam to explicitne aby bolo jasné čo chceš
#     app.run(
#         host="0.0.0.0",
#         port=port,
#         debug=True,
#         use_reloader=True
#     )




import os
from app import create_app, socketio  # <-- pridaj socketio

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    socketio.run(
        app,
        host="0.0.0.0",
        port=port,
        debug=True,
        use_reloader=True,
        allow_unsafe_werkzeug=True  # ak máš novší Flask/Werkzeug a lokálne ti to vypisuje warning
    )
