from typing import Protocol

class EventProducer(Protocol):
    async def produce(self, event_type: str, payload: dict[str, str]) -> None:
        ...


class EventConsumer(Protocol):
    async def consume(self) -> tuple[str, dict[str, str]]:
        ...
    
    async def _on_event_processed(self, event_id: str) -> None:
        ...
