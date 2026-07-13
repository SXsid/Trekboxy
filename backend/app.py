import os

from dotenv import load_dotenv

_ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
load_dotenv(_ENV_PATH)

import redis as redis_lib
from config import Config
from extensions import db, jwt, mail, make_celery
from flask import Flask
from flask_cors import CORS

celery = None


def create_app():
    global celery

    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, resources={r"/api/*": {"origins": "http://localhost:5713"}})

    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)

    import extensions

    extensions.redis_client = redis_lib.from_url(
        app.config["REDIS_URL"], decode_responses=True
    )

    celery = make_celery(app)

    from celery.schedules import crontab

    celery.conf.beat_schedule = {
        "process-outbox-every-30s": {
            "task": "tasks.process_outbox",
            "schedule": 5.0,  # seconds
        },
        "daily-trek-reminders": {
            "task": "tasks.send_daily_reminders",
            "schedule": crontab(hour="8", minute="0"),
        },
        "monthly-admin-report": {
            "task": "tasks.send_monthly_report",
            "schedule": crontab(hour="9", minute="0", day_of_month="1"),
        },
    }

    from api.admin import admin_bp
    from api.auth import auth_bp
    from api.bookings import bookings_bp
    from api.staff import staff_bp
    from api.treks import treks_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(treks_bp, url_prefix="/api/treks")
    app.register_blueprint(bookings_bp, url_prefix="/api/bookings")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(staff_bp, url_prefix="/api/staff")

    @app.route("/", methods=["GET"])
    def home():
        return "hello worldt"

    with app.app_context():
        from models import Booking, TaskOutbox, Trek, User  # noqa: F401

        db.create_all()

        from seed import seed_admin

        seed_admin()

    return app
