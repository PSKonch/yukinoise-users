from enum import StrEnum

from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import UUID, Index, func

from infrastructure.database.connection import Base


class UserStatus(StrEnum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BANNED = "banned"


class UserORM(Base):
    __tablename__ = "users"
    __table_args__ = (
        {"schema": "users"},
        Index("idx_users_status", "status"),
        Index("idx_users_last_login_at", "last_login_at"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True)  # No default, from Keycloak

    status: Mapped[UserStatus] = mapped_column(default=UserStatus.ACTIVE, nullable=False)
    email_verified: Mapped[bool] = mapped_column(default=False, nullable=False) # From Keycloak
    
    created_at: Mapped[int] = mapped_column(nullable=False, server_default=func.extract('epoch', func.now()))
    updated_at: Mapped[int] = mapped_column(nullable=False, server_default=func.extract('epoch', func.now()), onupdate=func.extract('epoch', func.now()))
    last_login_at: Mapped[int | None] = mapped_column(nullable=True)
    deleted_at: Mapped[int | None] = mapped_column(nullable=True)

    profile = relationship("ProfileORM", back_populates="user", uselist=False)
    settings = relationship("UserSettingORM", back_populates="user", uselist=False)