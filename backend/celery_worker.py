from app import celery, create_app  # noqa: F401

app = create_app()
import tasks.exports  # noqa: F401
import tasks.reminders  # noqa: F401
import tasks.reports  # noqa: F401
