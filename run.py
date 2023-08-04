
from app import create_app, db

app = create_app()
import os



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port = port)