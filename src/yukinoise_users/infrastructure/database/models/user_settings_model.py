from enum import StrEnum

from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import UUID, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
import uuid

from yukinoise_users.infrastructure.database.connection import Base


class UserPlaybackQuality(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    LOSSLESS = "lossless"


class UserSettingsORM(Base):
    __tablename__ = "user_settings"
    __table_args__ = {"schema": "users"}

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.users.id"), primary_key=True
    )

    dark_mode: Mapped[bool] = mapped_column(default=False, nullable=False)
    language: Mapped[str] = mapped_column(default="en", nullable=False)
    playback_quality: Mapped[UserPlaybackQuality] = mapped_column(
        default=UserPlaybackQuality.HIGH, nullable=False
    )
    notifications_enabled: Mapped[bool] = mapped_column(default=True, nullable=False)
    autoplay_enabled: Mapped[bool] = mapped_column(default=True, nullable=False)
    data_consent: Mapped[bool] = mapped_column(default=False, nullable=False)
    privacy_settings: Mapped[dict[str, bool]] = mapped_column(JSONB, nullable=True)

    updated_at: Mapped[int] = mapped_column(
        nullable=False,
        server_default=func.extract("epoch", func.now()),
        onupdate=func.extract("epoch", func.now()),
    )

    user = relationship("UserORM", back_populates="settings")
