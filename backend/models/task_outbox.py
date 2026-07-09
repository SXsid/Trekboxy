from datetime import datetime

from extensions import db


class TaskOutbox(db.Model):

    __tablename__ = "task_outbox"

    id = db.Column(db.Integer, primary_key=True)

    idempotency_key = db.Column(db.String(200), unique=True, nullable=False)

    task_type = db.Column(db.String(50), nullable=False)

    payload = db.Column(db.JSON, nullable=False, default=dict)

    status = db.Column(db.String(20), nullable=False, default="PENDING")

    celery_task_id = db.Column(db.String(200), nullable=True)

    error_message = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime, nullable=True)
