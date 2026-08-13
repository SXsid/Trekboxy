from extensions import db
from logger import get_logger
from models import User

logger = get_logger(__name__)


def seed_admin():
    existing_admin = User.query.filter_by(role="admin").first()
    if existing_admin:
        logger.info("Admin already exists: %s", existing_admin.email)
        return

    from flask import current_app
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
    logger.info("Admin seeded: %s", admin.email)
