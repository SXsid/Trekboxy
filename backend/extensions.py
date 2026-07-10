import redis as redis_lib
from celery import Celery
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

jwt = JWTManager()

mail = Mail()

redis_client: redis_lib.Redis | None = None


def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config["CELERY_BROKER_URL"],
        backend=app.config["CELERY_RESULT_BACKEND"],
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
