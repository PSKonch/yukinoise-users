from typing import Any
from uuid import UUID

from sqlalchemy import select, insert, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from yukinoise_users.infrastructure.database.models.outbox_event_model import OutBoxEventORM, OutBoxStatus
from yukinoise_users.infrastructure.database.repositories.base_repo import BaseRepository


class OutBoxEventRepository(BaseRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.model = OutBoxEventORM

    async def create_event(self, event_type: str, payload: dict[str, Any]) -> OutBoxEventORM:
        stmt = (
            insert(OutBoxEventORM)
            .values(event_type=event_type, payload=payload)
            .returning(OutBoxEventORM)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_pending_events(self, limit: int = 100) -> list[OutBoxEventORM]:
        query = (
            select(OutBoxEventORM)
            .where(OutBoxEventORM.status == OutBoxStatus.PENDING)
            .order_by(OutBoxEventORM.created_at)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()  # type: ignore[no-any-return]

    async def mark_event_sent(self, event_id: UUID) -> None:
        stmt = (
            update(OutBoxEventORM)
            .where(OutBoxEventORM.id == event_id)
            .values(status=OutBoxStatus.SENT, updated_at=func.extract("epoch", func.now()))
        )
        await self.session.execute(stmt)

    async def mark_event_failed(self, event_id: UUID, error: str) -> None:
        stmt = (
            update(OutBoxEventORM)
            .where(OutBoxEventORM.id == event_id)
            .values(
                status=OutBoxStatus.FAILED,
                error=error,
                updated_at=func.extract("epoch", func.now()),
            )
        )
        await self.session.execute(stmt)

    async def increment_retry_count(self, event_id: UUID) -> None:
        stmt = (
            update(OutBoxEventORM)
            .where(OutBoxEventORM.id == event_id)
            .values(
                retry_count=OutBoxEventORM.retry_count + 1,
                updated_at=func.extract("epoch", func.now()),
            )
        )
        await self.session.execute(stmt)

    async def delete_event(self, event_id: UUID, older_than: int) -> None:
        stmt = (
            delete(OutBoxEventORM)
            .where(
                OutBoxEventORM.id == event_id,
                OutBoxEventORM.updated_at < older_than,
            )
        )
        await self.session.execute(stmt)