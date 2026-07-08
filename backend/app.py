import redis as redis_lib
from flask import Flask
from flask_cors import CORS

from config import Config
from extensions import db, jwt, mail, make_celery

celery = None


def create_app():
    global celery

    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, resources={r"/api/*": {"origins": "http://localhost:8080"}})

    db.init_app(app)

    with app.app_context():
        from models import Booking, TaskOutbox, Trek, User

        db.create_all()

        from seed import seed_admin

        seed_admin()

    return app
