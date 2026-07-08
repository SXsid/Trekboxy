from flask import current_app

from extensions import db
from models import User


def seed_admin():

    existing_admin = User.query.filter_by(role="admin").first()

    if existing_admin:
        print(f"[seed] Admin already exists: {existing_admin.email}")
        return

    # No admin found — create one using credentials from config (which reads from .env)
    admin = User(
        username=current_app.config["ADMIN_USERNAME"],
        email=current_app.config["ADMIN_EMAIL"],
        role="admin",
        full_name="System Administrator",
        is_active=True,
    )

    admin.set_password(current_app.config["ADMIN_PASSWORD"])

    db.session.add(admin)
    db.session.commit()

    print(f"[seed] Admin created: {admin.email}")
