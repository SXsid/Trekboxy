from datetime import UTC, datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from extensions import db


class TaskOutbox(db.Model):

    __tablename__ = "task_outbox"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    idempotency_key: Mapped[str] = mapped_column(
        String(200), unique=True, nullable=False
    )

    # INFO: valid values: 'CSV_EXPORT', 'DAILY_REMINDER', 'MONTHLY_REPORT'
    task_type: Mapped[str] = mapped_column(String(50), nullable=False)

    payload: Mapped[dict] = mapped_column(db.JSON, nullable=False, default=dict)

    status: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDING")

    celery_task_id: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
