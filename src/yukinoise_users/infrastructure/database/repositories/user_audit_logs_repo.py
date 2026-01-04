from typing import Sequence, List, cast
from uuid import UUID

from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from yukinoise_users.infrastructure.database.models.user_audit_logs import (
    UserAuditLogORM,
    UserAuditAction,
    UserChangedBy,
)
from yukinoise_users.infrastructure.database.repositories.base_repo import (
    BaseRepository,
)


class UserAuditLogsRepository(BaseRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.model = UserAuditLogORM

    async def create(
        self,
        user_id: UUID,
        action: UserAuditAction,
        changed_by: UserChangedBy,
        details: dict[str, str] | None = None,
    ) -> UserAuditLogORM:
        stmt = (
            insert(UserAuditLogORM)
            .values(
                user_id=user_id,
                action=action,
                changed_by=changed_by,
                details=details,
            )
            .returning(UserAuditLogORM)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def list_for_user(
        self,
        user_id: UUID,
        limit: int = 100,
    ) -> Sequence[UserAuditLogORM]:
        query = (
            select(UserAuditLogORM)
            .where(UserAuditLogORM.user_id == user_id)
            .order_by(UserAuditLogORM.timestamp.desc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        return cast(List[UserAuditLogORM], result.scalars().all())

    async def list_by_action(
        self,
        action: UserAuditAction,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[UserAuditLogORM]:
        query = (
            select(UserAuditLogORM)
            .where(UserAuditLogORM.action == action)
            .order_by(UserAuditLogORM.timestamp.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        return cast(List[UserAuditLogORM], result.scalars().all())

    async def list_by_changed_by(
        self,
        changed_by: UserChangedBy,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[UserAuditLogORM]:
        query = (
            select(UserAuditLogORM)
            .where(UserAuditLogORM.changed_by == changed_by)
            .order_by(UserAuditLogORM.timestamp.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        return cast(List[UserAuditLogORM], result.scalars().all())

    async def list_since(
        self,
        since_timestamp: int,
        limit: int = 100,
    ) -> Sequence[UserAuditLogORM]:
        query = (
            select(UserAuditLogORM)
            .where(UserAuditLogORM.timestamp >= since_timestamp)
            .order_by(UserAuditLogORM.timestamp.desc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        return cast(List[UserAuditLogORM], result.scalars().all())

    async def get_user_logins(
        self,
        user_id: UUID,
        limit: int = 100,
    ) -> Sequence[UserAuditLogORM]:
        query = (
            select(UserAuditLogORM)
            .where(
                UserAuditLogORM.user_id == user_id,
                UserAuditLogORM.action == UserAuditAction.LOGIN,
            )
            .order_by(UserAuditLogORM.timestamp.desc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        return cast(List[UserAuditLogORM], result.scalars().all())
