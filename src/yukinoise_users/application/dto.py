from __future__ import annotations

from typing import Dict, List, Optional, TypeVar, Generic
from uuid import UUID

from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

from yukinoise_users.domain.value_objects import (
    UserStatus,
    UserPlaybackQuality,
    UserAuditAction,
    UserChangedBy,
)


T = TypeVar("T")


class CreateUserDTO(BaseModel):
    keycloak_id: UUID
    email_verified: bool = False


class UserDTO(BaseModel):
    id: UUID
    status: UserStatus
    email_verified: bool
    created_at: Optional[int] = None
    updated_at: Optional[int] = None
    last_login_at: Optional[int] = None


class ProfileDTO(BaseModel):
    user_id: UUID
    display_name: str = "anonymous"
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    banner_url: Optional[str] = None
    location: Optional[str] = None
    social_links: Dict[str, str] = Field(default_factory=dict)
    preferred_genres: List[str] = Field(default_factory=list)
    contact_email: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    monthly_listeners: Optional[int] = None
    followers_count: int = 0
    following_count: int = 0
    releases_count: int = 0
    featured_in_releases_count: int = 0
    verified: bool = False


class CreateProfileDTO(BaseModel):
    user_id: UUID
    display_name: str = "anonymous"
    bio: Optional[str] = None
    location: Optional[str] = None
    contact_email: Optional[str] = None


class UpdateProfileDTO(BaseModel):
    display_name: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    social_links: Optional[Dict[str, str]] = None
    preferred_genres: Optional[List[str]] = None
    contact_email: Optional[str] = None
    tags: Optional[List[str]] = None


class UserSettingsDTO(BaseModel):
    user_id: UUID
    dark_mode: bool = False
    language: str = "en"
    playback_quality: UserPlaybackQuality = UserPlaybackQuality.HIGH
    notifications_enabled: bool = True
    autoplay_enabled: bool = True
    data_consent: bool = False
    privacy_settings: Dict[str, bool] = Field(default_factory=dict)


class UpdateUserSettingsDTO(BaseModel):
    dark_mode: Optional[bool] = None
    language: Optional[str] = None
    playback_quality: Optional[UserPlaybackQuality] = None
    notifications_enabled: Optional[bool] = None
    autoplay_enabled: Optional[bool] = None
    data_consent: Optional[bool] = None
    privacy_settings: Optional[Dict[str, bool]] = None


class UserAuditLogDTO(BaseModel):
    id: UUID
    user_id: UUID
    action: UserAuditAction
    changed_by: UserChangedBy
    timestamp: int
    details: Dict[str, str] = Field(default_factory=dict)


class CreateAuditLogDTO(BaseModel):
    user_id: UUID
    action: UserAuditAction
    changed_by: UserChangedBy
    details: Optional[Dict[str, str]] = None


class PaginationParams(BaseModel):
    limit: int = 100
    offset: int = 0


class PaginatedResultDTO(GenericModel, Generic[T]):
    items: List[T]
    total: int
    limit: int
    offset: int

    @property
    def has_next(self) -> bool:
        return self.offset + len(self.items) < self.total

    @property
    def has_prev(self) -> bool:
        return self.offset > 0
