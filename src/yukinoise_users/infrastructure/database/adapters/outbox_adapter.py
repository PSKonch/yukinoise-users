from typing import List, Any
from uuid import UUID

from yukinoise_users.domain.repositories import OutboxRepository as OutboxRepoProtocol
from yukinoise_users.domain.models import OutboxEvent
from yukinoise_users.infrastructure.database.repositories.outbox_event_repo import (
    OutboxEventRepository as OutboxDbRepo,
)
from yukinoise_users.infrastructure.mapping.orm_to_domain import outbox_orm_to_domain


class OutboxRepositoryAdapter(OutboxRepoProtocol):
    def __init__(self, db_repo: OutboxDbRepo) -> None:
        self._db = db_repo

    async def create_event(
        self, event_type: str, payload: dict[str, Any]
    ) -> OutboxEvent:
        outbox_orm = await self._db.create_event(event_type, payload)
        return outbox_orm_to_domain(outbox_orm)

    async def get_pending_events(self, limit: int = 100) -> List[OutboxEvent]:
        outbox_orms = await self._db.get_pending_events(limit)
        return [outbox_orm_to_domain(o) for o in outbox_orms]

    async def mark_event_sent(self, event_id: UUID) -> None:
        await self._db.mark_event_sent(event_id)

    async def mark_event_failed(self, event_id: UUID, error: str) -> None:
        await self._db.mark_event_failed(event_id, error)

    async def increment_retry_count(self, event_id: UUID) -> None:
        await self._db.increment_retry_count(event_id)

    async def delete_event(self, event_id: UUID) -> None:
        await self._db.delete_event(event_id)

    async def delete_events_older_than(self, timestamp: int) -> None:
        await self._db.delete_events_older_than(timestamp)
