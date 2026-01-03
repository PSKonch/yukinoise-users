from dataclasses import dataclass, field
from uuid import UUID

from yukinoise_users.domain.value_objects import (
    UserStatus,
    UserPlaybackQuality,
    UserAuditAction,
    UserChangedBy,
    OutBoxStatus,
) 


@dataclass
class User:
    id: UUID
    status: UserStatus = UserStatus.ACTIVE
    email_verified: bool = False
    created_at: int | None = None
    updated_at: int | None = None
    last_login_at: int | None = None
    deleted_at: int | None = None
    profile: "Profile" | None = None
    settings: "UserSettings" | None = None


@dataclass
class Profile:
    user_id: UUID
    display_name: str = "anonymous"
    bio: str | None = None
    avatar_url: str | None = None
    banner_url: str | None = None
    location: str | None = None
    social_links: dict[str, str] = field(default_factory=dict)
    preferred_genres: list[str] = field(default_factory=list)
    contact_email: str | None = None
    tags: list[str] = field(default_factory=list)
    monthly_listeners: int | None = None
    followers_count: int = 0
    following_count: int = 0
    releases_count: int = 0
    featured_in_releases_count: int = 0
    verified: bool = False
    updated_at: int | None = None
    deleted_at: int | None = None 


@dataclass
class UserSettings:
    user_id: UUID
    dark_mode: bool = False
    language: str = "en"
    playback_quality: UserPlaybackQuality = UserPlaybackQuality.HIGH
    notifications_enabled: bool = True
    autoplay_enabled: bool = True
    data_consent: bool = False
    privacy_settings: dict[str, bool] = field(default_factory=dict)
    updated_at: int | None = None


@dataclass
class UserAuditLog:
    id: UUID
    user_id: UUID
    action: UserAuditAction
    changed_by: UserChangedBy
    timestamp: int
    details: dict[str, str] = field(default_factory=dict)


@dataclass
class OutBoxEvent:
    id: UUID
    event_type: str
    created_at: int
    payload: dict[str, str] = field(default_factory=dict)
    updated_at: int | None = None
    status: OutBoxStatus = OutBoxStatus.PENDING
    retry_count: int = 0
    error: str | None = None
