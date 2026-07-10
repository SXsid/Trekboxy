from datetime import UTC, datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db

if TYPE_CHECKING:
    from models.booking import Booking
    from models.trek import Trek


class User(db.Model):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    # INFO: valid values: 'admin', 'staff', 'trekker'
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="trekker")
    full_name: Mapped[str] = mapped_column(String(150), nullable=False, default="")
    phone: Mapped[str] = mapped_column(String(20), nullable=False, default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_blacklisted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )

    bookings: Mapped[List["Booking"]] = relationship(
        "Booking",
        foreign_keys="Booking.user_id",
        back_populates="trekker",
        lazy="select",
    )

    created_treks: Mapped[List["Trek"]] = relationship(
        "Trek",
        foreign_keys="Trek.created_by",
        back_populates="creator",
        lazy="select",
    )

    assigned_treks: Mapped[List["Trek"]] = relationship(
        "Trek",
        foreign_keys="Trek.assigned_staff_id",
        back_populates="assigned_staff",
        lazy="select",
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "full_name": self.full_name,
            "phone": self.phone,
            "is_active": self.is_active,
            "is_blacklisted": self.is_blacklisted,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
