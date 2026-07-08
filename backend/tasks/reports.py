from calendar import monthrange
from datetime import date

from flask_mail import Message

from app import celery
from extensions import db, mail


@celery.task(
    name="tasks.send_monthly_report",
    bind=True,
    max_retries=2,
    acks_late=True,
    reject_on_worker_lost=True,
)
def send_monthly_report(self, year=None, month=None):
    from models import Booking, Trek, User
    from models.task_outbox import TaskOutbox

    # INFO: if done by cron
    if not year or not month:
        today = date.today()
        if today.month == 1:
            month, year = 12, today.year - 1
        else:
            month, year = today.month - 1, today.year

    idempotency_key = f"monthly_report:{year}-{month:02d}"

    existing = TaskOutbox.query.filter_by(idempotency_key=idempotency_key).first()
    if existing and existing.status in ("DONE", "PROCESSING"):
        print(f"[report] Already sent report for {year}-{month:02d}")
        return

    if not existing:
        outbox = TaskOutbox(
            idempotency_key=idempotency_key,
            task_type="MONTHLY_REPORT",
            payload={"year": year, "month": month},
            status="PROCESSING",
        )
        db.session.add(outbox)
    else:
        outbox = existing
        outbox.status = "PROCESSING"

    db.session.commit()

    try:
        # Date range for last month
        _, last_day = monthrange(year, month)
        start = date(year, month, 1)
        end = date(year, month, last_day)

        # --- Gather stats ---

        # Treks that were completed in this month
        completed_treks = Trek.query.filter(
            Trek.status == "Completed",
            Trek.end_date >= start,
            Trek.end_date <= end,
        ).all()

        # Total bookings made in this month
        from sqlalchemy import extract, func

        total_bookings = Booking.query.filter(
            extract("year", Booking.booking_date) == year,
            extract("month", Booking.booking_date) == month,
        ).count()

        cancelled_bookings = Booking.query.filter(
            extract("year", Booking.booking_date) == year,
            extract("month", Booking.booking_date) == month,
            Booking.status == "Cancelled",
        ).count()

        # Most popular treks — by booking count (all time, not just this month)
        popular = (
            db.session.query(Trek, func.count(Booking.id).label("booking_count"))
            .join(Booking, Trek.id == Booking.trek_id)
            .group_by(Trek.id)
            .order_by(func.count(Booking.id).desc())
            .limit(5)
            .all()
        )

        # Find admin to send to
        admin = User.query.filter_by(role="admin").first()
        if not admin:
            print("[report] No admin found, skipping email")
            return

        html_body = _build_report_html(
            year=year,
            month=month,
            completed_treks=completed_treks,
            total_bookings=total_bookings,
            cancelled_bookings=cancelled_bookings,
            popular=popular,
        )

        msg = Message(
            subject=f"TMA Monthly Report — {year}/{month:02d}",
            recipients=[admin.email],
            html=html_body,
        )
        mail.send(msg)

        outbox.status = "DONE"
        outbox.processed_at = date.today()
        db.session.commit()

        print(f"[report] Monthly report sent to {admin.email}")

    except Exception as exc:
        outbox.status = "FAILED"
        outbox.error_message = str(exc)
        db.session.commit()
        raise self.retry(exc=exc, countdown=120)


def _build_report_html(
    year, month, completed_treks, total_bookings, cancelled_bookings, popular
):
    """Builds a simple HTML email body for the monthly report."""
    month_name = date(year, month, 1).strftime("%B %Y")

    popular_rows = ""
    for trek, count in popular:
        popular_rows += (
            f"<tr><td>{trek.name}</td><td>{trek.location}</td><td>{count}</td></tr>"
        )

    completed_rows = ""
    for t in completed_treks:
        completed_rows += f"<li>{t.name} ({t.location}) — ended {t.end_date}</li>"

    cancellation_rate = (
        f"{(cancelled_bookings / total_bookings * 100):.1f}%"
        if total_bookings > 0
        else "N/A"
    )

    return f"""
<html><body style="font-family: sans-serif; max-width: 600px; margin: auto;">
  <h2>TMA Monthly Report — {month_name}</h2>

  <h3>Summary</h3>
  <table border="1" cellpadding="8" style="border-collapse:collapse; width:100%">
    <tr><td><b>Total Bookings</b></td><td>{total_bookings}</td></tr>
    <tr><td><b>Cancelled Bookings</b></td><td>{cancelled_bookings}</td></tr>
    <tr><td><b>Cancellation Rate</b></td><td>{cancellation_rate}</td></tr>
    <tr><td><b>Treks Completed</b></td><td>{len(completed_treks)}</td></tr>
  </table>

  <h3>Completed Treks This Month</h3>
  <ul>{completed_rows or "<li>None</li>"}</ul>

  <h3>Top 5 Most Popular Treks (All Time)</h3>
  <table border="1" cellpadding="8" style="border-collapse:collapse; width:100%">
    <tr><th>Trek</th><th>Location</th><th>Total Bookings</th></tr>
    {popular_rows or "<tr><td colspan='3'>No data</td></tr>"}
  </table>

  <p style="color:gray; font-size:12px; margin-top:30px;">
    This is an automated report from TMA. Do not reply to this email.
  </p>
</body></html>
"""
