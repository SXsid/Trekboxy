from datetime import date, datetime, timedelta
from typing import Optional

from flask_mail import Message

from app import celery
from extensions import db, mail


@celery.task(
    name="tasks.send_daily_reminders",
    bind=True,
    max_retries=3,
    acks_late=True,
    reject_on_worker_lost=True,
)
def send_daily_reminders(self, target_date_str: Optional[str] = None):
    from models import Booking, Trek, User
    from models.task_outbox import TaskOutbox

    target_date = (
        date.fromisoformat(target_date_str) if target_date_str else date.today()
    )
    idempotency_key = f"daily_reminder:{target_date.isoformat()}"

    existing = TaskOutbox.query.filter_by(idempotency_key=idempotency_key).first()
    if existing and existing.status in ("DONE", "PROCESSING"):
        print(f"[reminder] Already ran for {target_date}, skipping")
        return

    if not existing:
        outbox = TaskOutbox(
            idempotency_key=idempotency_key,
            task_type="DAILY_REMINDER",
            payload={"date": target_date.isoformat()},
            status="PROCESSING",
        )
        db.session.add(outbox)
    else:
        outbox = existing
        outbox.status = "PROCESSING"

    db.session.commit()

    try:
        two_days_from_target = target_date + timedelta(days=2)

        upcoming_treks = Trek.query.filter(
            Trek.start_date >= target_date,
            Trek.start_date <= two_days_from_target,
            Trek.status == "Open",
        ).all()

        emails_sent = 0

        for trek in upcoming_treks:
            bookings = Booking.query.filter_by(trek_id=trek.id, status="Booked").all()

            for booking in bookings:
                user =booking.trekker
                if not user or not user.email:
                    continue

                _send_reminder_email(user, trek)
                emails_sent += 1

        outbox.status = "DONE"
        outbox.processed_at = datetime.utcnow()
        db.session.commit()

        print(f"[reminder] Sent {emails_sent} reminder emails for {target_date}")

    except Exception as exc:
        outbox.status = "FAILED"
        outbox.error_message = str(exc)
        db.session.commit()

        raise self.retry(exc=exc, countdown=60)


def _send_reminder_email(user, trek):
    subject = f"Reminder: Your trek '{trek.name}' starts soon!"
    body = f"""\
Hi {user.full_name or user.username},

This is a reminder that your trek is coming up!

Trek:     {trek.name}
Location: {trek.location}
Starts:   {trek.start_date}
Duration: {trek.duration_days} days

Get ready and stay safe on the trail!

— TMA Team""".strip()

    msg = Message(subject=subject, recipients=[user.email], body=body)
    mail.send(msg)
