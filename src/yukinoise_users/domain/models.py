from dataclasses import dataclass
from typing import Optional, List, Dict
from uuid import UUID

from yukinoise_users.domain.value_objects import (
    UserStatus,
    UserPlaybackQuality,
    UserAuditAction,
    UserChangedBy,
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
    profile: Optional["Profile"] = None
    settings: Optional["UserSettings"] = None


@dataclass
class Profile:
    user_id: UUID
    display_name: str = "anonymous"
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    banner_url: Optional[str] = None
    location: Optional[str] = None
    social_links: Optional[Dict[str, str]] = None
    preferred_genres: Optional[List[str]] = None
    contact_email: Optional[str] = None
    tags: Optional[List[str]] = None
    monthly_listeners: Optional[int] = None
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
    privacy_settings: Optional[Dict[str, bool]] = None
    updated_at: int | None = None


@dataclass
class UserAuditLog:
    id: UUID
    user_id: UUID
    action: UserAuditAction
    changed_by: UserChangedBy
    timestamp: int
    details: Optional[Dict[str, str]] = None
