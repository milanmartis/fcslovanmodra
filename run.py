import eventlet
eventlet.monkey_patch()

import os
from flask_socketio import SocketIO
from app import create_app

app = create_app()

socketio = SocketIO(
    app,
    async_mode="eventlet",
    cors_allowed_origins="*",
    logger=True,
    
    engineio_logger=True,
)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port, debug=True, use_reloader=False)