from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete, UUID

from yukinoise_users.infrastructure.database.connection import Base


class BaseRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.model = Base

    async def get_by_id(self, id: UUID) -> Base | None:
        query = select(self.model).where(self.model.id == id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self, limit: int = 100, offset: int = 0) -> list[Base]:
        query = select(self.model).limit(limit).offset(offset)
        result = await self.session.execute(query)
        return result.scalars().all()  # type: ignore[no-any-return]

    async def get_filtered_by(self, **filters: Any) -> list[Base]:
        query = select(self.model).filter_by(**filters)
        result = await self.session.execute(query)
        return result.scalars().all()  # type: ignore[no-any-return]

    async def add(self, instance: dict) -> None:
        stmt = insert(self.model).values(**instance).returning(self.model)
        await self.session.execute(stmt)

    async def update(self, id: UUID, updates: dict) -> None:
        stmt = (
            update(self.model)
            .where(self.model.id == id)
            .values(**updates)
            .returning(self.model)
        )
        await self.session.execute(stmt)

    async def delete(self, id: UUID) -> None:
        stmt = delete(self.model).where(self.model.id == id)
        await self.session.execute(stmt)
