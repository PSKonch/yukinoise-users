from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy import UUID, ForeignKey, Index, ARRAY, func, String
from sqlalchemy.dialects.postgresql import JSONB

from yukinoise_users.infrastructure.database.connection import Base


class ProfileORM(Base):
    __tablename__ = "profiles"
    __table_args__ = (
        {"schema": "users"},
        Index("idx_profiles_display_name", "display_name", unique=True),
        Index("idx_profiles_search_vector", "search_vector", postgresql_using="gin"),
        Index(
            "idx_profiles_preferred_genres", "preferred_genres", postgresql_using="gin"
        ),
        Index("idx_profiles_tags", "tags", postgresql_using="gin"),
        Index("idx_profiles_social_links", "social_links", postgresql_using="gin"),
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.users.id"), primary_key=True
    )

    display_name: Mapped[str] = mapped_column(nullable=False, default="anonymous")
    bio: Mapped[str | None] = mapped_column(nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(nullable=True)
    banner_url: Mapped[str | None] = mapped_column(nullable=True)
    location: Mapped[str | None] = mapped_column(nullable=True)
    social_links: Mapped[dict[str, str] | None] = mapped_column(JSONB, nullable=True)
    preferred_genres: Mapped[list[str] | None] = mapped_column(
        ARRAY(String), nullable=True
    )
    contact_email: Mapped[str | None] = mapped_column(nullable=True)
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    monthly_listeners: Mapped[int | None] = mapped_column(nullable=True)
    followers_count: Mapped[int] = mapped_column(default=0, nullable=False)
    following_count: Mapped[int] = mapped_column(default=0, nullable=False)
    releases_count: Mapped[int] = mapped_column(default=0, nullable=False)
    featured_in_releases_count: Mapped[int] = mapped_column(default=0, nullable=False)
    verified: Mapped[bool] = mapped_column(default=False, nullable=False)
    search_vector: Mapped[str | None] = mapped_column(TSVECTOR, nullable=True)

    updated_at: Mapped[int] = mapped_column(
        nullable=False,
        server_default=func.extract("epoch", func.now()),
        onupdate=func.extract("epoch", func.now()),
    )
    deleted_at: Mapped[int | None] = mapped_column(nullable=True)

    user = relationship("UserORM", back_populates="profile")
