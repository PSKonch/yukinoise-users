from typing import Protocol, Any

class EventProducer(Protocol):
    async def produce(self, event_type: str, payload: dict[str, Any]) -> None:
        ...


class EventConsumer(Protocol):
    async def consume(self) -> tuple[str, dict[str, Any]]:
        ...
    
    async def on_event_processed(self, event_id: str) -> None:
        ...
