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
    def __init__(self, db_repo: UserSettingsDbRepo) -> None:
        self._db = db_repo

    async def get(self, user_id: UUID) -> UserSettings | None:
        orm = await self._db.get_by_user_id(user_id)
        return settings_orm_to_domain(orm)

    async def update(self, user_id: UUID, **updates: Any) -> None:
        await self._db.update_settings(user_id, **updates)

    async def create(self, user_id: UUID, **settings: Any) -> UserSettings:
        orm = await self._db.create(user_id, **settings)
        return settings_orm_to_domain(orm)

    async def soft_delete(self, user_id: UUID, timestamp: int) -> None:
        raise NotImplementedError("User settings soft delete is not supported")

    async def restore(self, user_id: UUID) -> None:
        raise NotImplementedError("User settings restore is not supported")
