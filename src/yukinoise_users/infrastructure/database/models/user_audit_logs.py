from enum import StrEnum

from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import ForeignKey, Index, func
from sqlalchemy.dialects.postgresql import JSONB
import uuid

from yukinoise_users.infrastructure.database.connection import Base


class UserAuditAction(StrEnum):
    LOGIN = "login"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"
    PROFILE_UPDATE = "profile_update"
    ACCOUNT_DELETION = "account_deletion"


class UserChangedBy(StrEnum):
    USER = "user"
    ADMIN = "admin"
    SYSTEM = "system"


class UserAuditLogORM(Base):
    __tablename__ = "user_audit_logs"
    __table_args__ = (
        Index("idx_user_audit_logs_user_id", "user_id"),
        Index("idx_user_audit_logs_action", "action"),
        {"schema": "users"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=func.gen_random_uuid()
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.users.id"), nullable=False
    )
    action: Mapped[UserAuditAction] = mapped_column(nullable=False)
    changed_by: Mapped[UserChangedBy] = mapped_column(nullable=False)
    timestamp: Mapped[int] = mapped_column(
        nullable=False, server_default=func.extract("epoch", func.now())
    )
    details: Mapped[dict[str, str] | None] = mapped_column(JSONB, nullable=True)
