import json
import logging
from typing import AsyncIterator, Callable, Awaitable
from uuid import uuid4

from aio_pika import connect_robust, ExchangeType
from aio_pika.abc import (
    AbstractRobustConnection,
    AbstractChannel,
    AbstractQueue,
    AbstractIncomingMessage,
)

from yukinoise_users.domain.events import IncomingEvent


logger = logging.getLogger(__name__)


class RabbitMQEventConsumer:
    def __init__(
        self,
        amqp_url: str,
        exchange_name: str = "yukinoise.events",
        queue_name: str = "yukinoise-users",
        prefetch_count: int = 10,
        connection_name: str = "yukinoise-users-consumer",
    ) -> None:
        self.amqp_url = amqp_url
        self.exchange_name = exchange_name
        self.queue_name = queue_name
        self.prefetch_count = prefetch_count
        self.connection_name = connection_name

        self._connection: AbstractRobustConnection | None = None
        self._channel: AbstractChannel | None = None
        self._queue: AbstractQueue | None = None
        self._pending_messages: dict[str, AbstractIncomingMessage] = {}

    async def connect(self) -> None:
        if self._connection is not None and not self._connection.is_closed:
            return

        self._connection = await connect_robust(
            self.amqp_url,
            client_properties={"connection_name": self.connection_name},
        )
        self._channel = await self._connection.channel()
        await self._channel.set_qos(prefetch_count=self.prefetch_count)

        await self._channel.declare_exchange(
            self.exchange_name,
            ExchangeType.TOPIC,
            durable=True,
        )

        self._queue = await self._channel.declare_queue(
            self.queue_name,
            durable=True,
            arguments={
                "x-dead-letter-exchange": f"{self.exchange_name}.dlx",
                "x-dead-letter-routing-key": "dead-letter",
            },
        )

        logger.info(f"Connected to RabbitMQ queue: {self.queue_name}")

    async def disconnect(self) -> None:
        if self._channel and not self._channel.is_closed:
            await self._channel.close()
        if self._connection and not self._connection.is_closed:
            await self._connection.close()
        self._connection = None
        self._channel = None
        self._queue = None
        self._pending_messages.clear()
        logger.info("Disconnected from RabbitMQ")

    async def subscribe(self, routing_keys: list[str]) -> None:
        if self._queue is None or self._channel is None:
            await self.connect()

        exchange = await self._channel.declare_exchange(  # type: ignore
            self.exchange_name,
            ExchangeType.TOPIC,
            durable=True,
        )

        for routing_key in routing_keys:
            await self._queue.bind(exchange, routing_key=routing_key)  # type: ignore
            logger.info(f"Subscribed to routing key: {routing_key}")

    async def consume(self) -> AsyncIterator[IncomingEvent]:
        if self._queue is None:
            await self.connect()

        async with self._queue.iterator() as queue_iter:  # type: ignore
            async for message in queue_iter:
                event = self._parse_message(message)
                self._pending_messages[event.event_id] = message
                yield event

    async def ack(self, event_id: str) -> None:
        message = self._pending_messages.pop(event_id, None)
        if message:
            await message.ack()
            logger.debug(f"Acknowledged event: {event_id}")

    async def nack(self, event_id: str, requeue: bool = True) -> None:
        message = self._pending_messages.pop(event_id, None)
        if message:
            await message.nack(requeue=requeue)
            logger.debug(f"Rejected event: {event_id}, requeue={requeue}")

    def _parse_message(self, message: AbstractIncomingMessage) -> IncomingEvent:
        body = json.loads(message.body.decode("utf-8"))
        headers = dict(message.headers) if message.headers else {}

        event_id = message.message_id or str(uuid4())
        event_type = headers.get("event_type", body.get("event_type", "unknown"))

        return IncomingEvent(
            event_id=event_id,
            event_type=event_type,
            payload=body.get("payload", body),
            routing_key=message.routing_key or "",
            headers=headers,
        )

    async def consume_with_handler(
        self,
        handler: Callable[[IncomingEvent], Awaitable[bool]],
        auto_ack: bool = True,
    ) -> None:
        async for event in self.consume():
            try:
                success = await handler(event)
                if auto_ack:
                    if success:
                        await self.ack(event.event_id)
                    else:
                        await self.nack(event.event_id, requeue=True)
            except Exception as e:
                logger.exception(f"Error processing event {event.event_id}: {e}")
                if auto_ack:
                    await self.nack(event.event_id, requeue=False)

    async def __aenter__(self) -> "RabbitMQEventConsumer":
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore
        await self.disconnect()
