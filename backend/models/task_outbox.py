from datetime import datetime

from extensions import db


class TaskOutbox(db.Model):

    __tablename__ = "task_outbox"

    id = db.Column(db.Integer, primary_key=True)

    # Unique key that identifies this specific job execution.
    # Format depends on task type:
    #   csv_export:    "csv_export:{user_id}:{date}"
    #   daily_reminder: "daily_reminder:{date}"
    #   monthly_report: "monthly_report:{year}-{month}"
    idempotency_key = db.Column(db.String(200), unique=True, nullable=False)

    # What kind of job is this?
    # Valid: 'CSV_EXPORT', 'DAILY_REMINDER', 'MONTHLY_REPORT'
    task_type = db.Column(db.String(50), nullable=False)

    # JSON payload the Celery task needs to run.
    # CSV_EXPORT needs: {"user_id": 42}
    # DAILY_REMINDER needs: {} (it queries all upcoming treks itself)
    # MONTHLY_REPORT needs: {"year": 2026, "month": 7}
    payload = db.Column(db.JSON, nullable=False, default=dict)

    # Status lifecycle:
    #   PENDING    → row created, not yet sent to Celery
    #   PROCESSING → .delay() called, Celery is working on it
    #   DONE       → Celery finished successfully
    #   FAILED     → Celery raised an exception
    status = db.Column(db.String(20), nullable=False, default="PENDING")

    # Filled in after .delay() is called — lets us track the Celery task
    celery_task_id = db.Column(db.String(200), nullable=True)

    # Error message if status = FAILED
    error_message = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime, nullable=True)  # filled when DONE or FAILED
