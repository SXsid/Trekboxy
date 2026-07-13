from datetime import UTC, datetime, timezone
from typing import TYPE_CHECKING, Optional

from extensions import db
from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from models.trek import Trek
    from models.user import User


class Booking(db.Model):

    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )

    trek_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("treks.id"), nullable=False
    )

    # INFO: valid values: 'Booked', 'Cancelled', 'Completed'
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="Booked")
    # TODO: remot that  before updalod
    payment_status: Mapped[str] = mapped_column(String(26), nullable=False)

    booking_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    trek: Mapped["Trek"] = relationship(
        "Trek",
        back_populates="bookings",
    )

    trekker: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="bookings",
    )

    __table_args__ = (
        Index(
            "uq_user_trek_active",
            "user_id",
            "trek_id",
            unique=True,
            sqlite_where=(status == "Booked"),
        ),
    )

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
