from datetime import UTC, date, datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from extensions import db

if TYPE_CHECKING:
    from models.booking import Booking
    from models.user import User


class Trek(db.Model):

    __tablename__ = "treks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    location: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False, default="Easy")
    duration_days: Mapped[int] = mapped_column(Integer, nullable=False)

    total_slots: Mapped[int] = mapped_column(Integer, nullable=False)
    available_slots: Mapped[int] = mapped_column(Integer, nullable=False)

    assigned_staff_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )

    # INFO: valid values: 'Pending', 'Open', 'Closed', 'Completed', 'Cancelled'
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="Pending")

    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    registration_deadline: Mapped[date] = mapped_column(Date, nullable=False)

    price: Mapped[float] = mapped_column(Float, default=0.0)

    created_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    bookings: Mapped[List["Booking"]] = relationship(
        "Booking",
        back_populates="trek",
        lazy="select",
        cascade="all, delete-orphan",
    )

    creator: Mapped["User"] = relationship(
        "User",
        foreign_keys=[created_by],
        back_populates="created_treks",
    )

    assigned_staff: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[assigned_staff_id],
        back_populates="assigned_treks",
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "description": self.description,
            "difficulty": self.difficulty,
            "duration_days": self.duration_days,
            "total_slots": self.total_slots,
            "available_slots": self.available_slots,
            "assigned_staff_id": self.assigned_staff_id,
            "status": self.status,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "registration_deadline": (
                self.registration_deadline.isoformat()
                if self.registration_deadline
                else None
            ),
            "price": self.price,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
