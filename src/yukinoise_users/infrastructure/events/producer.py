import json
import logging
from typing import Any
from uuid import uuid4

from aio_pika import connect_robust, Message, DeliveryMode, ExchangeType
from aio_pika.abc import AbstractRobustConnection, AbstractChannel, AbstractExchange

from yukinoise_users.domain.events import DomainEvent


logger = logging.getLogger(__name__)


class RabbitMQEventProducer:
    def __init__(
        self,
        amqp_url: str,
        exchange_name: str = "yukinoise.events",
        connection_name: str = "yukinoise-users-producer",
    ) -> None:
        self.amqp_url = amqp_url
        self.exchange_name = exchange_name
        self.connection_name = connection_name
        self._connection: AbstractRobustConnection | None = None
        self._channel: AbstractChannel | None = None
        self._exchange: AbstractExchange | None = None

    async def connect(self) -> None:
        if self._connection is not None and not self._connection.is_closed:
            return

        self._connection = await connect_robust(
            self.amqp_url,
            client_properties={"connection_name": self.connection_name},
        )
        self._channel = await self._connection.channel()
        self._exchange = await self._channel.declare_exchange(
            self.exchange_name,
            ExchangeType.TOPIC,
            durable=True,
        )
        logger.info(f"Connected to RabbitMQ exchange: {self.exchange_name}")

    async def disconnect(self) -> None:
        if self._channel and not self._channel.is_closed:
            await self._channel.close()
        if self._connection and not self._connection.is_closed:
            await self._connection.close()
        self._connection = None
        self._channel = None
        self._exchange = None
        logger.info("Disconnected from RabbitMQ")

    async def publish(self, event: DomainEvent) -> None:
        if self._exchange is None:
            await self.connect()

        message_id = str(uuid4())
        payload = self._serialize_event(event)

        message = Message(
            body=json.dumps(payload).encode("utf-8"),
            headers={
                "event_type": event.event_type.value,
                "aggregate_id": str(event.aggregate_id),
                "correlation_id": event.correlation_id,
                "causation_id": event.causation_id,
            },
            message_id=message_id,
            content_type="application/json",
            delivery_mode=DeliveryMode.PERSISTENT,
        )

        await self._exchange.publish(  # type: ignore
            message,
            routing_key=event.event_type.value,
        )
        logger.debug(f"Published event {event.event_type.value} with id {message_id}")

    async def publish_batch(self, events: list[DomainEvent]) -> None:
        for event in events:
            await self.publish(event)

    def _serialize_event(self, event: DomainEvent) -> dict[str, Any]:
        return {
            "event_type": event.event_type.value,
            "aggregate_id": str(event.aggregate_id),
            "payload": event.payload,
            "correlation_id": event.correlation_id,
            "causation_id": event.causation_id,
        }

    async def __aenter__(self) -> "RabbitMQEventProducer":
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore
        await self.disconnect()
