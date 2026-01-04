from typing import Sequence, Any
from uuid import UUID

from yukinoise_users.domain.repositories import UsersRepository as UsersRepoProtocol
from yukinoise_users.domain.models import User
from yukinoise_users.domain.value_objects import UserStatus
from yukinoise_users.infrastructure.database.repositories.users_repo import (
    UsersRepository as UsersDbRepo,
)
from yukinoise_users.infrastructure.mapping.orm_to_domain import user_orm_to_domain


class UsersRepositoryAdapter(UsersRepoProtocol):
    def __init__(self, db_repo: UsersDbRepo) -> None:
        self._db = db_repo

    async def create_from_keycloak(
        self, keycloak_id: UUID, email_verified: bool = False
    ) -> User:
        user_orm = await self._db.create_from_keycloak(keycloak_id, email_verified)
        return user_orm_to_domain(user_orm)

    async def get_by_id(self, user_id: UUID) -> User | None:
        user_orm = await self._db.get_by_id(user_id)
        return user_orm_to_domain(user_orm) if user_orm is not None else None

    async def get_by_id_with_profile(self, user_id: UUID) -> User | None:
        user_orm = await self._db.get_by_id_with_profile(user_id)
        return user_orm_to_domain(user_orm) if user_orm is not None else None

    async def get_by_id_full(self, user_id: UUID) -> User | None:
        user_orm = await self._db.get_by_id_full(user_id)
        return user_orm_to_domain(user_orm) if user_orm is not None else None

    async def get_by_ids(self, user_ids: list[UUID]) -> Sequence[User]:
        user_orms = await self._db.get_by_ids(user_ids)
        return [user_orm_to_domain(u) for u in user_orms]

    async def exists(self, user_id: UUID) -> bool:
        return bool(await self._db.exists(user_id))

    async def get_by_status(
        self, status: UserStatus, limit: int = 100, offset: int = 0
    ) -> Sequence[User]:
        user_orms = await self._db.get_by_status(status, limit, offset)
        return [user_orm_to_domain(u) for u in user_orms]

    async def get_active_users(
        self, limit: int = 100, offset: int = 0
    ) -> Sequence[User]:
        user_orms = await self._db.get_active_users(limit, offset)
        return [user_orm_to_domain(u) for u in user_orms]

    async def get_recently_active(
        self, since_timestamp: int, limit: int = 100
    ) -> Sequence[User]:
        user_orms = await self._db.get_recently_active(since_timestamp, limit)
        return [user_orm_to_domain(u) for u in user_orms]

    async def update_last_login(self, user_id: UUID, timestamp: int) -> None:
        await self._db.update_last_login(user_id, timestamp)

    async def update_email_verified(self, user_id: UUID, verified: bool) -> None:
        await self._db.update_email_verified(user_id, verified)

    async def update_status(self, user_id: UUID, status: UserStatus) -> None:
        await self._db.update_status(user_id, status)

    async def suspend_user(self, user_id: UUID) -> None:
        await self._db.suspend_user(user_id)

    async def ban_user(self, user_id: UUID) -> None:
        await self._db.ban_user(user_id)

    async def activate_user(self, user_id: UUID) -> None:
        await self._db.activate_user(user_id)

    async def soft_delete(self, user_id: UUID, timestamp: int) -> None:
        await self._db.soft_delete(user_id, timestamp)

    async def restore(self, user_id: UUID) -> None:
        await self._db.restore(user_id)

    async def count_by_status(self, status: UserStatus) -> int:
        return int(await self._db.count_by_status(status))

    async def count_total_active(self) -> int:
        return int(await self._db.count_total_active())

    async def count_registered_since(self, since_timestamp: int) -> int:
        return int(await self._db.count_registered_since(since_timestamp))
