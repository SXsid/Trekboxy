import csv
import io
from datetime import date, datetime

from app import celery
from extensions import db, mail
from flask import current_app
from flask_mail import Message


@celery.task(
    name="tasks.export_bookings_csv",
    bind=True,
    max_retries=3,
    acks_late=True,
    reject_on_worker_lost=True,
)
def export_bookings_csv(self, user_id: int, outbox_id: int):
    from models import Booking, TaskOutbox, Trek, User

    outbox = TaskOutbox.query.get(outbox_id)

    if not outbox or outbox.status == "DONE":
        return
    outbox.status = "PROCESSING"
    db.session.commit()

    try:
        user = User.query.get(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        bookings = (
            Booking.query.filter_by(user_id=user_id)
            .order_by(Booking.booking_date.desc())
            .all()
        )

        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(
            [
                "Booking ID",
                "Trek Name",
                "Location",
                "Difficulty",
                "Start Date",
                "End Date",
                "Duration (days)",
                "Booking Status",
                "Booked On",
            ]
        )

        for b in bookings:
            trek = Trek.query.get(b.trek_id)
            writer.writerow(
                [
                    b.id,
                    trek.name if trek else "N/A",
                    trek.location if trek else "N/A",
                    trek.difficulty if trek else "N/A",
                    trek.start_date.isoformat() if trek and trek.start_date else "N/A",
                    trek.end_date.isoformat() if trek and trek.end_date else "N/A",
                    trek.duration_days if trek else "N/A",
                    b.status,
                    b.booking_date.isoformat() if b.booking_date else "N/A",
                ]
            )

        csv_content = output.getvalue()

        msg = Message(
            subject="Your Booking History — CSV Export",
            recipients=[user.email],
            body=(
                f"Hi {user.full_name or user.username},\n\n"
                "Please find your booking history attached.\n\n— HimTrek Team"
            ),
        )
        msg.attach(
            filename=f"bookings_{user.username}_{date.today().isoformat()}.csv",
            content_type="text/csv",
            data=csv_content.encode("utf-8"),
        )

        mail.send(msg)

        outbox.status = "DONE"
        outbox.processed_at = datetime.utcnow()
        db.session.commit()

        print(f"[export] CSV sent to {user.email} ({len(bookings)} bookings)")

    except Exception as exc:
        from celery.exceptions import MaxRetriesExceededError

        try:
            outbox.status = "DISPATCHED"
            outbox.error_message = str(exc)
            db.session.commit()
            raise self.retry(exc=exc, countdown=60)

        except MaxRetriesExceededError:
            outbox.status = "FAILED"
            outbox.error_message = str(exc)
            outbox.processed_at = datetime.utcnow()
            db.session.commit()


@celery.task(name="tasks.process_outbox")
def process_outbox():
    from models.task_outbox import TaskOutbox

    pending_tasks = (
        TaskOutbox.query.filter_by(status="PENDING")
        .with_for_update(skip_locked=True)
        .all()
    )

    for task in pending_tasks:
        task.status = "DISPATCHED"
        task.last_attempt_at = datetime.utcnow()
        db.session.commit()

        try:
            if task.task_type == "CSV_EXPORT":
                result = export_bookings_csv.delay(
                    user_id=task.payload.get("user_id"),
                    outbox_id=task.id,
                )

            elif task.task_type == "DAILY_REMINDER":
                from tasks.reminders import send_daily_reminders

                result = send_daily_reminders.delay(
                    target_date_str=task.payload.get("date")
                )

            elif task.task_type == "MONTHLY_REPORT":
                from tasks.reports import send_monthly_report

                result = send_monthly_report.delay(
                    year=task.payload.get("year"),
                    month=task.payload.get("month"),
                )

            else:
                print(f"[outbox] Unknown task_type: {task.task_type}, skipping")
                continue

            task.celery_task_id = result.id
            db.session.commit()

        except Exception as e:
            task.status = "PENDING"
            task.error_message = str(e)
            db.session.commit()
            print(f"[outbox] Failed to dispatch task {task.id} ({task.task_type}): {e}")
