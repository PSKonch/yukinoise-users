from uuid import UUID
from typing import Sequence

from sqlalchemy import select, update, insert, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from yukinoise_users.infrastructure.database.models.users_model import UserORM, UserStatus
from yukinoise_users.infrastructure.database.repositories.base_repo import BaseRepository


class UsersRepository(BaseRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.model = UserORM

    async def create_from_keycloak(
        self,
        keycloak_id: UUID,
        email_verified: bool = False,
    ) -> UserORM:
        stmt = (
            insert(UserORM)
            .values(
                id=keycloak_id,
                email_verified=email_verified,
            )
            .returning(UserORM)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_by_id(self, user_id: UUID) -> UserORM | None:
        query = select(UserORM).where(
            UserORM.id == user_id,
            UserORM.deleted_at.is_(None),
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_id_with_profile(self, user_id: UUID) -> UserORM | None:
        query = (
            select(UserORM)
            .options(selectinload(UserORM.profile))
            .where(
                UserORM.id == user_id,
                UserORM.deleted_at.is_(None),
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_id_full(self, user_id: UUID) -> UserORM | None:
        query = (
            select(UserORM)
            .options(
                selectinload(UserORM.profile),
                selectinload(UserORM.settings),
            )
            .where(
                UserORM.id == user_id,
                UserORM.deleted_at.is_(None),
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_ids(self, user_ids: list[UUID]) -> Sequence[UserORM]:
        if not user_ids:
            return []
        query = select(UserORM).where(
            UserORM.id.in_(user_ids),
            UserORM.deleted_at.is_(None),
        )
        result = await self.session.execute(query)
        return result.scalars().all()  # type: ignore[no-any-return]

    async def exists(self, user_id: UUID) -> bool:
        query = select(func.count()).select_from(UserORM).where(
            UserORM.id == user_id,
            UserORM.deleted_at.is_(None),
        )
        result = await self.session.execute(query)
        return (result.scalar() or 0) > 0

    async def get_by_status(
        self,
        status: UserStatus,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[UserORM]:
        query = (
            select(UserORM)
            .where(
                UserORM.status == status,
                UserORM.deleted_at.is_(None),
            )
            .order_by(UserORM.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        return result.scalars().all()  # type: ignore[no-any-return]

    async def get_active_users(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[UserORM]:
        return await self.get_by_status(UserStatus.ACTIVE, limit, offset)

    async def get_recently_active(
        self,
        since_timestamp: int,
        limit: int = 100,
    ) -> Sequence[UserORM]:
        query = (
            select(UserORM)
            .where(
                UserORM.last_login_at >= since_timestamp,
                UserORM.deleted_at.is_(None),
            )
            .order_by(UserORM.last_login_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()  # type: ignore[no-any-return]

    async def update_last_login(self, user_id: UUID, timestamp: int) -> None:
        stmt = (
            update(UserORM)
            .where(UserORM.id == user_id)
            .values(last_login_at=timestamp)
        )
        await self.session.execute(stmt)

    async def update_email_verified(
        self,
        user_id: UUID,
        verified: bool,
    ) -> None:
        stmt = (
            update(UserORM)
            .where(UserORM.id == user_id)
            .values(email_verified=verified)
        )
        await self.session.execute(stmt)

    async def update_status(
        self,
        user_id: UUID,
        status: UserStatus,
    ) -> None:
        stmt = (
            update(UserORM)
            .where(UserORM.id == user_id)
            .values(status=status)
        )
        await self.session.execute(stmt)

    async def suspend_user(self, user_id: UUID) -> None:
        await self.update_status(user_id, UserStatus.SUSPENDED)

    async def ban_user(self, user_id: UUID) -> None:
        await self.update_status(user_id, UserStatus.BANNED)

    async def activate_user(self, user_id: UUID) -> None:
        await self.update_status(user_id, UserStatus.ACTIVE)

    async def soft_delete(self, user_id: UUID, timestamp: int) -> None:
        stmt = (
            update(UserORM)
            .where(UserORM.id == user_id)
            .values(deleted_at=timestamp)
        )
        await self.session.execute(stmt)

    async def restore(self, user_id: UUID) -> None:
        stmt = (
            update(UserORM)
            .where(UserORM.id == user_id)
            .values(deleted_at=None)
        )
        await self.session.execute(stmt)

    async def count_by_status(self, status: UserStatus) -> int:
        query = select(func.count()).select_from(UserORM).where(
            UserORM.status == status,
            UserORM.deleted_at.is_(None),
        )
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def count_total_active(self) -> int:
        return await self.count_by_status(UserStatus.ACTIVE)

    async def count_registered_since(self, since_timestamp: int) -> int:
        query = select(func.count()).select_from(UserORM).where(
            UserORM.created_at >= since_timestamp,
            UserORM.deleted_at.is_(None),
        )
        result = await self.session.execute(query)
        return result.scalar() or 0

