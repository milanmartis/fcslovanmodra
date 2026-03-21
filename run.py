import os
from dotenv import load_dotenv

load_dotenv()  # načíta .env z aktuálneho priečinka

from app import create_app, socketio

app = create_app()

if __name__ == "__main__":
    socketio.run(app, host="localhost", port=5000, debug=True, use_reloader=False, allow_unsafe_werkzeug=True)