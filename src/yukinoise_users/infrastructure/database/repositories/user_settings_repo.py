from typing import Any, Sequence
from uuid import UUID

from sqlalchemy import select, update, insert, func
from sqlalchemy.ext.asyncio import AsyncSession

from yukinoise_users.infrastructure.database.models.user_settings_model import (
    UserSettingsORM,
    UserPlaybackQuality,
)
from yukinoise_users.infrastructure.database.repositories.base_repo import (
    BaseRepository,
)


class UserSettingsRepository(BaseRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.model = UserSettingsORM

    async def create(self, user_id: UUID, **settings: Any) -> UserSettingsORM:
        stmt = (
            insert(UserSettingsORM)
            .values(user_id=user_id, **settings)
            .returning(UserSettingsORM)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def create_default(self, user_id: UUID) -> UserSettingsORM:
        return await self.create(user_id)

    async def get_by_user_id(self, user_id: UUID) -> UserSettingsORM | None:
        query = select(UserSettingsORM).where(UserSettingsORM.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_user_ids(self, user_ids: list[UUID]) -> Sequence[UserSettingsORM]:
        if not user_ids:
            return []
        query = select(UserSettingsORM).where(UserSettingsORM.user_id.in_(user_ids))
        result = await self.session.execute(query)
        return result.scalars().all()  # type: ignore[no-any-return]

    async def exists(self, user_id: UUID) -> bool:
        query = (
            select(func.count())
            .select_from(UserSettingsORM)
            .where(UserSettingsORM.user_id == user_id)
        )
        result = await self.session.execute(query)
        return (result.scalar() or 0) > 0

    async def update_settings(self, user_id: UUID, **updates: Any) -> None:
        stmt = (
            update(UserSettingsORM)
            .where(UserSettingsORM.user_id == user_id)
            .values(**updates)
        )
        await self.session.execute(stmt)

    async def set_dark_mode(self, user_id: UUID, enabled: bool) -> None:
        await self.update_settings(user_id, dark_mode=enabled)

    async def set_language(self, user_id: UUID, language: str) -> None:
        await self.update_settings(user_id, language=language)

    async def set_playback_quality(
        self, user_id: UUID, quality: UserPlaybackQuality
    ) -> None:
        await self.update_settings(user_id, playback_quality=quality)

    async def set_notifications_enabled(self, user_id: UUID, enabled: bool) -> None:
        await self.update_settings(user_id, notifications_enabled=enabled)

    async def set_autoplay_enabled(self, user_id: UUID, enabled: bool) -> None:
        await self.update_settings(user_id, autoplay_enabled=enabled)

    async def set_data_consent(self, user_id: UUID, consent: bool) -> None:
        await self.update_settings(user_id, data_consent=consent)

    async def set_privacy_settings(
        self, user_id: UUID, privacy: dict[str, bool]
    ) -> None:
        await self.update_settings(user_id, privacy_settings=privacy)

    async def update_privacy_setting(
        self, user_id: UUID, key: str, value: bool
    ) -> None:
        settings = await self.get_by_user_id(user_id)
        if settings:
            current = settings.privacy_settings or {}
            current[key] = value
            await self.set_privacy_settings(user_id, current)

    async def get_by_language(
        self, language: str, limit: int = 100
    ) -> Sequence[UserSettingsORM]:
        query = (
            select(UserSettingsORM)
            .where(UserSettingsORM.language == language)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()  # type: ignore[no-any-return]

    async def get_with_data_consent(
        self, limit: int = 100, offset: int = 0
    ) -> Sequence[UserSettingsORM]:
        query = (
            select(UserSettingsORM)
            .where(UserSettingsORM.data_consent.is_(True))
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        return result.scalars().all()  # type: ignore[no-any-return]

    async def count_by_language(self, language: str) -> int:
        query = (
            select(func.count())
            .select_from(UserSettingsORM)
            .where(UserSettingsORM.language == language)
        )
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def count_with_notifications_enabled(self) -> int:
        query = (
            select(func.count())
            .select_from(UserSettingsORM)
            .where(UserSettingsORM.notifications_enabled.is_(True))
        )
        result = await self.session.execute(query)
        return result.scalar() or 0
