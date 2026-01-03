import json
from typing import Any
from aio_pika import connect_robust, Message, DeliveryMode, ExchangeType


class EventProducer:
    def __init__(self, amqp_url: str, exchange_name: str = "yukinoise.events"):
        self.amqp_url = amqp_url
        self.exchange_name = exchange_name

    async def produce(self, event_type: str, payload: dict[str, Any]) -> None:
        connection = await connect_robust(self.amqp_url)
        async with connection:
            channel = await connection.channel()
            exchange = await channel.declare_exchange(
                self.exchange_name, ExchangeType.TOPIC, durable=True
            )
            await exchange.publish(
                Message(
                    body=json.dumps(payload).encode("utf-8"),
                    headers={"event_type": event_type},
                    delivery_mode=DeliveryMode.PERSISTENT,
                ),
                routing_key=event_type,
            )
