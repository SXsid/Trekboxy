from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db


class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    # INFO: valid values: 'admin', 'staff', 'trekker'
    role = db.Column(db.String(20), nullable=False, default="trekker")
    full_name = db.Column(db.String(150))
    phone = db.Column(db.String(20), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_blacklisted = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    bookings = db.relationship(
        "Booking", foreign_keys="Booking.user_id", backref="trekker", lazy=True
    )
    created_treks = db.relationship(
        "Trek", foreign_keys="Trek.created_by", backref="creator", lazy=True
    )
    assigned_treks = db.relationship(
        "Trek",
        foreign_keys="Trek.assigned_staff_id",
        backref="assigned_staff",
        lazy=True,
    )

    def set_password(self, password: str):
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
