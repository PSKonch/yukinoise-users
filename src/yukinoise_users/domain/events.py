from typing import Protocol, Any, AsyncIterator
from dataclasses import dataclass, field
from uuid import UUID
from enum import StrEnum


class EventType(StrEnum):
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"
    USER_SUSPENDED = "user.suspended"
    USER_BANNED = "user.banned"
    USER_ACTIVATED = "user.activated"
    USER_RESTORED = "user.restored"
    USER_LOGIN = "user.login"
    USER_EMAIL_VERIFIED = "user.email_verified"

    PROFILE_CREATED = "profile.created"
    PROFILE_UPDATED = "profile.updated"
    PROFILE_DELETED = "profile.deleted"
    PROFILE_VERIFIED = "profile.verified"

    SETTINGS_UPDATED = "settings.updated"

    USER_FOLLOWED = "user.followed"
    USER_UNFOLLOWED = "user.unfollowed"


@dataclass
class DomainEvent:
    event_type: EventType
    aggregate_id: UUID
    payload: dict[str, Any] = field(default_factory=dict)
    correlation_id: str | None = None
    causation_id: str | None = None


@dataclass
class IncomingEvent:
    event_id: str
    event_type: str
    payload: dict[str, Any]
    routing_key: str
    headers: dict[str, Any] = field(default_factory=dict)


class EventProducer(Protocol):
    async def publish(self, event: DomainEvent) -> None: ...

    async def publish_batch(self, events: list[DomainEvent]) -> None: ...

    async def connect(self) -> None: ...

    async def disconnect(self) -> None: ...


class EventConsumer(Protocol):
    async def subscribe(self, routing_keys: list[str]) -> None: ...

    async def consume(self) -> AsyncIterator[IncomingEvent]: ...

    async def ack(self, event_id: str) -> None: ...

    async def nack(self, event_id: str, requeue: bool = True) -> None: ...

    async def connect(self) -> None: ...

    async def disconnect(self) -> None: ...
