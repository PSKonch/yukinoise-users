from typing import Any, Sequence
from uuid import UUID

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from yukinoise_users.infrastructure.database.models.profiles_model import ProfileORM
from yukinoise_users.infrastructure.database.repositories.base_repo import BaseRepository


class ProfilesRepository(BaseRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.model = ProfileORM

    async def create(self, user_id: UUID, **profile_data: Any) -> ProfileORM:
        profile = ProfileORM(user_id=user_id, **profile_data)
        self.session.add(profile)
        await self.session.flush()
        return profile

    async def get_by_user_id(self, user_id: UUID) -> ProfileORM | None:
        query = select(ProfileORM).where(
            ProfileORM.user_id == user_id,
            ProfileORM.deleted_at.is_(None),
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_user_ids(self, user_ids: list[UUID]) -> Sequence[ProfileORM]:
        if not user_ids:
            return []
        query = select(ProfileORM).where(
            ProfileORM.user_id.in_(user_ids),
            ProfileORM.deleted_at.is_(None),
        )
        result = await self.session.execute(query)
        return result.scalars().all()  # type: ignore[no-any-return]

    async def get_by_display_name(self, display_name: str) -> ProfileORM | None:
        query = select(ProfileORM).where(
            ProfileORM.display_name == display_name,
            ProfileORM.deleted_at.is_(None),
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_display_name_ilike(self, pattern: str, limit: int = 100) -> Sequence[ProfileORM]:
        query = (
            select(ProfileORM)
            .where(
                ProfileORM.display_name.ilike(f"%{pattern}%"),
                ProfileORM.deleted_at.is_(None),
            )
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()  # type: ignore[no-any-return]

    async def exists_display_name(self, display_name: str) -> bool:
        query = select(func.count()).select_from(ProfileORM).where(
            ProfileORM.display_name == display_name,
            ProfileORM.deleted_at.is_(None),
        )
        result = await self.session.execute(query)
        return (result.scalar() or 0) > 0

    async def search_fulltext(self, query_text: str, limit: int = 100) -> Sequence[ProfileORM]:
        query = (
            select(ProfileORM)
            .where(
                ProfileORM.search_vector.match(query_text),
                ProfileORM.deleted_at.is_(None),
            )
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()  # type: ignore[no-any-return]

    async def get_by_genres(self, genres: list[str], limit: int = 100) -> Sequence[ProfileORM]:
        query = (
            select(ProfileORM)
            .where(
                ProfileORM.preferred_genres.overlap(genres),
                ProfileORM.deleted_at.is_(None),
            )
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()  # type: ignore[no-any-return]

    async def get_by_tags(self, tags: list[str], limit: int = 100) -> Sequence[ProfileORM]:
        query = (
            select(ProfileORM)
            .where(
                ProfileORM.tags.overlap(tags),
                ProfileORM.deleted_at.is_(None),
            )
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()  # type: ignore[no-any-return]

    async def get_verified(self, limit: int = 100, offset: int = 0) -> Sequence[ProfileORM]:
        query = (
            select(ProfileORM)
            .where(
                ProfileORM.verified.is_(True),
                ProfileORM.deleted_at.is_(None),
            )
            .order_by(ProfileORM.followers_count.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        return result.scalars().all()  # type: ignore[no-any-return]

    async def get_top_by_monthly_listeners(self, limit: int = 100, offset: int = 0) -> Sequence[ProfileORM]:
        query = (
            select(ProfileORM)
            .where(ProfileORM.deleted_at.is_(None))
            .order_by(ProfileORM.monthly_listeners.desc().nullslast())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        return result.scalars().all()  # type: ignore[no-any-return]

    async def get_top_by_followers(self, limit: int = 100, offset: int = 0) -> Sequence[ProfileORM]:
        query = (
            select(ProfileORM)
            .where(ProfileORM.deleted_at.is_(None))
            .order_by(ProfileORM.followers_count.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        return result.scalars().all()  # type: ignore[no-any-return]

    async def update_profile(self, user_id: UUID, **updates: Any) -> None:
        stmt = (
            update(ProfileORM)
            .where(ProfileORM.user_id == user_id)
            .values(**updates)
        )
        await self.session.execute(stmt)

    async def update_avatar(self, user_id: UUID, avatar_url: str | None) -> None:
        await self.update_profile(user_id, avatar_url=avatar_url)

    async def update_banner(self, user_id: UUID, banner_url: str | None) -> None:
        await self.update_profile(user_id, banner_url=banner_url)

    async def increment_followers(self, user_id: UUID) -> None:
        stmt = (
            update(ProfileORM)
            .where(ProfileORM.user_id == user_id)
            .values(followers_count=ProfileORM.followers_count + 1)
        )
        await self.session.execute(stmt)

    async def decrement_followers(self, user_id: UUID) -> None:
        stmt = (
            update(ProfileORM)
            .where(ProfileORM.user_id == user_id)
            .values(followers_count=ProfileORM.followers_count - 1)
        )
        await self.session.execute(stmt)

    async def increment_following(self, user_id: UUID) -> None:
        stmt = (
            update(ProfileORM)
            .where(ProfileORM.user_id == user_id)
            .values(following_count=ProfileORM.following_count + 1)
        )
        await self.session.execute(stmt)

    async def decrement_following(self, user_id: UUID) -> None:
        stmt = (
            update(ProfileORM)
            .where(ProfileORM.user_id == user_id)
            .values(following_count=ProfileORM.following_count - 1)
        )
        await self.session.execute(stmt)

    async def increment_releases(self, user_id: UUID) -> None:
        stmt = (
            update(ProfileORM)
            .where(ProfileORM.user_id == user_id)
            .values(releases_count=ProfileORM.releases_count + 1)
        )
        await self.session.execute(stmt)

    async def decrement_releases(self, user_id: UUID) -> None:
        stmt = (
            update(ProfileORM)
            .where(ProfileORM.user_id == user_id)
            .values(releases_count=ProfileORM.releases_count - 1)
        )
        await self.session.execute(stmt)

    async def increment_featured_in_releases(self, user_id: UUID) -> None:
        stmt = (
            update(ProfileORM)
            .where(ProfileORM.user_id == user_id)
            .values(featured_in_releases_count=ProfileORM.featured_in_releases_count + 1)
        )
        await self.session.execute(stmt)

    async def decrement_featured_in_releases(self, user_id: UUID) -> None:
        stmt = (
            update(ProfileORM)
            .where(ProfileORM.user_id == user_id)
            .values(featured_in_releases_count=ProfileORM.featured_in_releases_count - 1)
        )
        await self.session.execute(stmt)

    async def set_verified(self, user_id: UUID, verified: bool) -> None:
        await self.update_profile(user_id, verified=verified)

    async def update_monthly_listeners(self, user_id: UUID, count: int) -> None:
        await self.update_profile(user_id, monthly_listeners=count)

    async def soft_delete(self, user_id: UUID, timestamp: int) -> None:
        stmt = (
            update(ProfileORM)
            .where(ProfileORM.user_id == user_id)
            .values(deleted_at=timestamp)
        )
        await self.session.execute(stmt)

    async def restore(self, user_id: UUID) -> None:
        stmt = (
            update(ProfileORM)
            .where(ProfileORM.user_id == user_id)
            .values(deleted_at=None)
        )
        await self.session.execute(stmt)
    
    