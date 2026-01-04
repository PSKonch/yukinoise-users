from typing import TYPE_CHECKING, Type, Any

from sqlalchemy.ext.asyncio import AsyncSession

from yukinoise_users.infrastructure.database.connection import async_session_factory
from yukinoise_users.infrastructure.database.repositories import (
    UsersRepository as UsersDbRepository,
    ProfilesRepository as ProfilesDbRepository,
    UserSettingsRepository as UserSettingsDbRepository,
    UserAuditLogsRepository as UserAuditLogsDbRepository,
    OutboxEventRepository as OutboxEventDbRepository,
)
from yukinoise_users.infrastructure.database.adapters.users_adapter import (
    UsersRepositoryAdapter,
)
from yukinoise_users.infrastructure.database.adapters.profiles_adapter import (
    ProfilesRepositoryAdapter,
)
from yukinoise_users.infrastructure.database.adapters.settings_adapter import (
    UserSettingsRepositoryAdapter,
)
from yukinoise_users.infrastructure.database.adapters.audit_logs_adapter import (
    UserAuditLogsRepositoryAdapter,
)
from yukinoise_users.infrastructure.database.adapters.outbox_adapter import (
    OutboxRepositoryAdapter,
)

if TYPE_CHECKING:
    from yukinoise_users.domain.repositories import (
        UsersRepository,
        ProfilesRepository,
        UserSettingsRepository,
        UserAuditLogsRepository,
        OutboxRepository,
    )

    session: AsyncSession
    users: UsersRepository
    profiles: ProfilesRepository
    settings: UserSettingsRepository
    audit_logs: UserAuditLogsRepository
    outbox: OutboxRepository


class UnitOfWork:
    def __init__(
        self, session_factory: Type[async_session_factory] = async_session_factory
    ) -> None:
        self._session_factory = session_factory
        self._session: AsyncSession | None = None

        # repository instances (private until context entered)
        self._users: UsersRepository | None = None
        self._profiles: ProfilesRepository | None = None
        self._settings: UserSettingsRepository | None = None
        self._audit_logs: UserAuditLogsRepository | None = None
        self._outbox: OutboxRepository | None = None

        self._txn: Any | None = None

    async def __aenter__(self) -> "UnitOfWork":
        self._session = self._session_factory()
        self._txn = self._session.begin()
        # mypy cannot infer transaction context type; treat as Any
        await self._txn.__aenter__()

        _db_users = UsersDbRepository(self._session)
        _db_profiles = ProfilesDbRepository(self._session)
        _db_settings = UserSettingsDbRepository(self._session)
        _db_audit_logs = UserAuditLogsDbRepository(self._session)
        _db_outbox = OutboxEventDbRepository(self._session)

        self._users = UsersRepositoryAdapter(_db_users)
        self._profiles = ProfilesRepositoryAdapter(_db_profiles)
        self._settings = UserSettingsRepositoryAdapter(_db_settings)
        self._audit_logs = UserAuditLogsRepositoryAdapter(_db_audit_logs)
        self._outbox = OutboxRepositoryAdapter(_db_outbox)

        return self

    async def __aexit__(
        self, exc_type: type | None, exc: BaseException | None, tb: object | None
    ) -> None:
        # delegate to the transaction context manager which will commit or rollback
        if self._txn is not None:
            await self._txn.__aexit__(exc_type, exc, tb)

        # close and clear the session and repos
        if self._session is not None:
            await self._session.close()
        self._session = None
        self._users = None
        self._profiles = None
        self._settings = None
        self._audit_logs = None
        self._outbox = None

    @property
    def session(self) -> AsyncSession:
        if self._session is None:
            raise RuntimeError("UnitOfWork has no active session")
        return self._session

    @property
    def users(self) -> UsersRepository:
        if self._users is None:
            raise RuntimeError("UnitOfWork has no active session")
        return self._users

    @property
    def profiles(self) -> ProfilesRepository:
        if self._profiles is None:
            raise RuntimeError("UnitOfWork has no active session")
        return self._profiles

    @property
    def settings(self) -> UserSettingsRepository:
        if self._settings is None:
            raise RuntimeError("UnitOfWork has no active session")
        return self._settings

    @property
    def audit_logs(self) -> UserAuditLogsRepository:
        if self._audit_logs is None:
            raise RuntimeError("UnitOfWork has no active session")
        return self._audit_logs

    @property
    def outbox(self) -> OutboxRepository:
        if self._outbox is None:
            raise RuntimeError("UnitOfWork has no active session")
        return self._outbox

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()
