from enum import StrEnum
from typing import Any

from sqlalchemy import UUID, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import mapped_column, Mapped

from yukinoise_users.infrastructure.database.connection import Base


class OutBoxStatus(StrEnum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class OutBoxEventORM(Base):
    __tablename__ = "outbox_events"
    __table_args__ = ({"schema": "users"},)

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    event_type: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[int] = mapped_column(
        nullable=False, server_default=func.extract("epoch", func.now())
    )
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    updated_at: Mapped[int | None] = mapped_column(nullable=True)
    status: Mapped[OutBoxStatus] = mapped_column(
        nullable=False, server_default=OutBoxStatus.PENDING.value
    )
    retry_count: Mapped[int] = mapped_column(nullable=False, server_default="0")
    error: Mapped[str | None] = mapped_column(nullable=True)
