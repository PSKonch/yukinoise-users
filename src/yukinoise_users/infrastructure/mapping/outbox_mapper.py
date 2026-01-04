from uuid import UUID
from typing import Any

from yukinoise_users.domain.events import DomainEvent, EventType


def outbox_to_domain(outbox_event: Any) -> DomainEvent:
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
