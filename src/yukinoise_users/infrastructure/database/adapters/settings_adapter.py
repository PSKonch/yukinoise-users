from typing import Sequence, Any
from uuid import UUID

from yukinoise_users.domain.repositories import (
    UserSettingsRepository as SettingsRepoProtocol,
)
from yukinoise_users.domain.models import UserSettings
from yukinoise_users.infrastructure.database.repositories.user_settings_repo import (
    UserSettingsRepository as UserSettingsDbRepo,
)
from yukinoise_users.infrastructure.mapping.orm_to_domain import settings_orm_to_domain


class UserSettingsRepositoryAdapter(SettingsRepoProtocol):
    """Adapter for `UserSettingsRepository` protocol."""

    def __init__(self, db_repo: UserSettingsDbRepo) -> None:
        self._db = db_repo

    async def get(self, user_id: UUID) -> UserSettings | None:
        orm = await self._db.get_by_user_id(user_id)
        return settings_orm_to_domain(orm)

    async def create(self, user_id: UUID, **settings: Any) -> UserSettings:
        orm = await self._db.create(user_id, **settings)
        return settings_orm_to_domain(orm)

    async def create_default(self, user_id: UUID) -> UserSettings:
        orm = await self._db.create_default(user_id)
        return settings_orm_to_domain(orm)

    async def get_by_user_id(self, user_id: UUID) -> UserSettings | None:
        orm = await self._db.get_by_user_id(user_id)
        return settings_orm_to_domain(orm)

    async def get_by_user_ids(self, user_ids: list[UUID]) -> Sequence[UserSettings]:
        orms = await self._db.get_by_user_ids(user_ids)
        return [settings_orm_to_domain(o) for o in orms]

    async def exists(self, user_id: UUID) -> bool:
        return bool(await self._db.exists(user_id))

    async def update(self, user_id: UUID, **updates: Any) -> None:
        await self._db.update_settings(user_id, **updates)

    async def update_settings(self, user_id: UUID, **updates: Any) -> None:
        await self._db.update_settings(user_id, **updates)

    async def set_dark_mode(self, user_id: UUID, enabled: bool) -> None:
        await self._db.set_dark_mode(user_id, enabled)

    async def set_language(self, user_id: UUID, language: str) -> None:
        await self._db.set_language(user_id, language)

    async def set_playback_quality(self, user_id: UUID, quality: Any) -> None:
        await self._db.set_playback_quality(user_id, quality)

    async def set_notifications_enabled(self, user_id: UUID, enabled: bool) -> None:
        await self._db.set_notifications_enabled(user_id, enabled)

    async def set_autoplay_enabled(self, user_id: UUID, enabled: bool) -> None:
        await self._db.set_autoplay_enabled(user_id, enabled)

    async def set_data_consent(self, user_id: UUID, consent: bool) -> None:
        await self._db.set_data_consent(user_id, consent)

    async def set_privacy_settings(self, user_id: UUID, privacy: dict[str, bool]) -> None:
        await self._db.set_privacy_settings(user_id, privacy)

    async def update_privacy_setting(self, user_id: UUID, key: str, value: bool) -> None:
        await self._db.update_privacy_setting(user_id, key, value)

    async def get_by_language(self, language: str, limit: int = 100) -> Sequence[UserSettings]:
        orms = await self._db.get_by_language(language, limit)
        return [settings_orm_to_domain(o) for o in orms]

    async def get_with_data_consent(self, limit: int = 100, offset: int = 0) -> Sequence[UserSettings]:
        orms = await self._db.get_with_data_consent(limit, offset)
        return [settings_orm_to_domain(o) for o in orms]

    async def count_by_language(self, language: str) -> int:
        return int(await self._db.count_by_language(language))

    async def count_with_notifications_enabled(self) -> int:
        return int(await self._db.count_with_notifications_enabled())