import asyncio
import time
from uuid import UUID
import logging
from typing import Any

from yukinoise_users.domain.repositories import OutboxRepository
from yukinoise_users.domain.events import DomainEvent, EventType
from yukinoise_users.infrastructure.events.producer import RabbitMQEventProducer


logger = logging.getLogger(__name__)


class OutboxProcessor:
    def __init__(
        self,
        outbox_repo: OutboxRepository,
        event_producer: RabbitMQEventProducer,
        batch_size: int = 100,
        max_retries: int = 5,
        retry_delay_seconds: float = 1.0,
    ) -> None:
        self._outbox_repo = outbox_repo
        self._event_producer = event_producer
        self._batch_size = batch_size
        self._max_retries = max_retries
        self._retry_delay = retry_delay_seconds
        self._running = False

    async def process_pending_events(self) -> int:
        events = await self._outbox_repo.get_pending_events(limit=self._batch_size)

        if not events:
            return 0

        processed_count = 0

        for event in events:
            try:
                domain_event = self._convert_to_domain_event(event)

                await self._event_producer.publish(domain_event)

                await self._outbox_repo.mark_event_sent(event.id)
                processed_count += 1

                logger.debug(f"Successfully published event {event.id}")

            except Exception as e:
                logger.error(f"Failed to publish event {event.id}: {e}")

                await self._outbox_repo.increment_retry_count(event.id)

                if event.retry_count + 1 >= self._max_retries:
                    await self._outbox_repo.mark_event_failed(event.id, error=str(e))
                    logger.warning(
                        f"Event {event.id} marked as failed after "
                        f"{self._max_retries} retries"
                    )

        return processed_count

    def _convert_to_domain_event(self, outbox_event: Any) -> DomainEvent:
        try:
            event_type = EventType(outbox_event.event_type)
        except ValueError:
            event_type = EventType.USER_UPDATED

        aggregate_id = outbox_event.payload.get("user_id")
        if aggregate_id:
            aggregate_id = (
                UUID(aggregate_id) if isinstance(aggregate_id, str) else aggregate_id
            )
        else:
            aggregate_id = outbox_event.id

        return DomainEvent(
            event_type=event_type,
            aggregate_id=aggregate_id,
            payload=outbox_event.payload,
        )

    async def start(self, interval_seconds: float = 5.0) -> None:
        self._running = True
        logger.info("Starting outbox processor")

        await self._event_producer.connect()

        while self._running:
            try:
                processed = await self.process_pending_events()
                if processed > 0:
                    logger.info(f"Processed {processed} outbox events")
            except Exception as e:
                logger.exception(f"Error in outbox processor: {e}")

            await asyncio.sleep(interval_seconds)

    async def stop(self) -> None:
        self._running = False
        await self._event_producer.disconnect()
        logger.info("Stopped outbox processor")

    async def cleanup_old_events(self, older_than_days: int = 7) -> None:
        cutoff_timestamp = int(time.time()) - (older_than_days * 24 * 60 * 60)
        await self._outbox_repo.delete_events_older_than(cutoff_timestamp)
        logger.info(f"Cleaned up outbox events older than {older_than_days} days")
