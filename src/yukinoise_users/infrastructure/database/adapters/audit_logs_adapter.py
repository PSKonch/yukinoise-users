from typing import Sequence
from uuid import UUID

from yukinoise_users.domain.repositories import (
    UserAuditLogsRepository as AuditRepoProtocol,
)
from yukinoise_users.domain.models import UserAuditLog
from yukinoise_users.domain.value_objects import UserAuditAction, UserChangedBy
from yukinoise_users.infrastructure.database.repositories.user_audit_logs_repo import (
    UserAuditLogsRepository as UserAuditLogsDbRepo,
)
from yukinoise_users.infrastructure.mapping.orm_to_domain import audit_log_orm_to_domain


class UserAuditLogsRepositoryAdapter(AuditRepoProtocol):
    def __init__(self, db_repo: UserAuditLogsDbRepo) -> None:
        self._db = db_repo

    async def create(
        self,
        user_id: UUID,
        action: UserAuditAction,
        changed_by: UserChangedBy,
        details: dict | None = None,
    ) -> UserAuditLog:
        orm = await self._db.create(user_id, action, changed_by, details)
        return audit_log_orm_to_domain(orm)

    async def list_for_user(
        self, user_id: UUID, limit: int = 100
    ) -> Sequence[UserAuditLog]:
        orms = await self._db.list_for_user(user_id, limit)
        return [audit_log_orm_to_domain(o) for o in orms]
