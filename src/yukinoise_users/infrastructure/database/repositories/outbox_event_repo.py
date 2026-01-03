from typing import Any
from uuid import UUID

from sqlalchemy import select, insert, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from yukinoise_users.infrastructure.database.models.outbox_event_model import (
    OutboxEventORM,
    OutboxStatus,
)
from yukinoise_users.infrastructure.database.repositories.base_repo import (
    BaseRepository,
)


class OutboxEventRepository(BaseRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.model = OutboxEventORM

    async def create_event(
        self, event_type: str, payload: dict[str, Any]
    ) -> OutboxEventORM:
        stmt = (
            insert(OutboxEventORM)
            .values(event_type=event_type, payload=payload)
            .returning(OutboxEventORM)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_pending_events(self, limit: int = 100) -> list[OutboxEventORM]:
        query = (
            select(OutboxEventORM)
            .where(OutboxEventORM.status == OutboxStatus.PENDING)
            .order_by(OutboxEventORM.created_at)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()  # type: ignore[no-any-return]

    async def mark_event_sent(self, event_id: UUID) -> None:
        stmt = (
            update(OutboxEventORM)
            .where(OutboxEventORM.id == event_id)
            .values(
                status=OutboxStatus.SENT, updated_at=func.extract("epoch", func.now())
            )
        )
        await self.session.execute(stmt)

    async def mark_event_failed(self, event_id: UUID, error: str) -> None:
        stmt = (
            update(OutboxEventORM)
            .where(OutboxEventORM.id == event_id)
            .values(
                status=OutboxStatus.FAILED,
                error=error,
                updated_at=func.extract("epoch", func.now()),
            )
        )
        await self.session.execute(stmt)

    async def increment_retry_count(self, event_id: UUID) -> None:
        stmt = (
            update(OutboxEventORM)
            .where(OutboxEventORM.id == event_id)
            .values(
                retry_count=OutboxEventORM.retry_count + 1,
                updated_at=func.extract("epoch", func.now()),
            )
        )
        await self.session.execute(stmt)

    async def delete_event(self, event_id: UUID) -> None:
        stmt = delete(OutboxEventORM).where(
            OutboxEventORM.id == event_id,
        )
        await self.session.execute(stmt)

    async def delete_events_older_than(self, timestamp: int) -> None:
        stmt = delete(OutboxEventORM).where(
            OutboxEventORM.updated_at < timestamp,
        )
        await self.session.execute(stmt)
