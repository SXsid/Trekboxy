from datetime import datetime

from extensions import db


class Booking(db.Model):

    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    trek_id = db.Column(db.Integer, db.ForeignKey("treks.id"), nullable=False)

    status = db.Column(db.String(20), nullable=False, default="Booked")

    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    __table_args__ = (db.UniqueConstraint("user_id", "trek_id", name="uq_user_trek"),)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "trek_id": self.trek_id,
            "status": self.status,
            "booking_date": (
                self.booking_date.isoformat() if self.booking_date else None
            ),
        }
