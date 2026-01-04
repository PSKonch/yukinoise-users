from typing import Sequence, Any
from uuid import UUID

from yukinoise_users.domain.repositories import (
    ProfilesRepository as ProfilesRepoProtocol,
)
from yukinoise_users.domain.models import Profile
from yukinoise_users.infrastructure.database.repositories.profiles_repo import (
    ProfilesRepository as ProfilesDbRepo,
)
from yukinoise_users.infrastructure.mapping.orm_to_domain import profile_orm_to_domain


class ProfilesRepositoryAdapter(ProfilesRepoProtocol):
    def __init__(self, db_repo: ProfilesDbRepo) -> None:
        self._db = db_repo

    async def create(self, user_id: UUID, **profile_data: Any) -> Profile:
        profile_orm = await self._db.create(user_id, **profile_data)
        return profile_orm_to_domain(profile_orm)

    async def get_by_user_id(self, user_id: UUID) -> Profile | None:
        profile_orm = await self._db.get_by_user_id(user_id)
        return profile_orm_to_domain(profile_orm) if profile_orm is not None else None

    async def get_by_user_ids(self, user_ids: list[UUID]) -> Sequence[Profile]:
        profile_orms = await self._db.get_by_user_ids(user_ids)
        return [profile_orm_to_domain(p) for p in profile_orms]

    async def get_by_display_name(self, display_name: str) -> Profile | None:
        profile_orm = await self._db.get_by_display_name(display_name)
        return profile_orm_to_domain(profile_orm) if profile_orm is not None else None

    async def get_by_display_name_ilike(
        self, pattern: str, limit: int = 100
    ) -> Sequence[Profile]:
        profile_orms = await self._db.get_by_display_name_ilike(pattern, limit)
        return [profile_orm_to_domain(p) for p in profile_orms]

    async def exists_display_name(self, display_name: str) -> bool:
        return bool(await self._db.exists_display_name(display_name))

    async def search_fulltext(
        self, query_text: str, limit: int = 100
    ) -> Sequence[Profile]:
        profile_orms = await self._db.search_fulltext(query_text, limit)
        return [profile_orm_to_domain(p) for p in profile_orms]

    async def get_by_genres(
        self, genres: list[str], limit: int = 100
    ) -> Sequence[Profile]:
        profile_orms = await self._db.get_by_genres(genres, limit)
        return [profile_orm_to_domain(p) for p in profile_orms]

    async def get_by_tags(self, tags: list[str], limit: int = 100) -> Sequence[Profile]:
        profile_orms = await self._db.get_by_tags(tags, limit)
        return [profile_orm_to_domain(p) for p in profile_orms]

    async def get_verified(
        self, limit: int = 100, offset: int = 0
    ) -> Sequence[Profile]:
        profile_orms = await self._db.get_verified(limit, offset)
        return [profile_orm_to_domain(p) for p in profile_orms]

    async def get_top_by_monthly_listeners(
        self, limit: int = 100, offset: int = 0
    ) -> Sequence[Profile]:
        profile_orms = await self._db.get_top_by_monthly_listeners(limit, offset)
        return [profile_orm_to_domain(p) for p in profile_orms]

    async def get_top_by_followers(
        self, limit: int = 100, offset: int = 0
    ) -> Sequence[Profile]:
        profile_orms = await self._db.get_top_by_followers(limit, offset)
        return [profile_orm_to_domain(p) for p in profile_orms]

    async def update_profile(self, user_id: UUID, **updates: Any) -> None:
        await self._db.update_profile(user_id, **updates)

    async def update_avatar(self, user_id: UUID, avatar_url: str | None) -> None:
        await self._db.update_avatar(user_id, avatar_url)

    async def update_banner(self, user_id: UUID, banner_url: str | None) -> None:
        await self._db.update_banner(user_id, banner_url)

    async def increment_followers(self, user_id: UUID) -> None:
        await self._db.increment_followers(user_id)

    async def decrement_followers(self, user_id: UUID) -> None:
        await self._db.decrement_followers(user_id)

    async def increment_following(self, user_id: UUID) -> None:
        await self._db.increment_following(user_id)

    async def decrement_following(self, user_id: UUID) -> None:
        await self._db.decrement_following(user_id)

    async def increment_releases(self, user_id: UUID) -> None:
        await self._db.increment_releases(user_id)

    async def decrement_releases(self, user_id: UUID) -> None:
        await self._db.decrement_releases(user_id)

    async def increment_featured_in_releases(self, user_id: UUID) -> None:
        await self._db.increment_featured_in_releases(user_id)

    async def decrement_featured_in_releases(self, user_id: UUID) -> None:
        await self._db.decrement_featured_in_releases(user_id)

    async def set_verified(self, user_id: UUID, verified: bool) -> None:
        await self._db.set_verified(user_id, verified)

    async def update_monthly_listeners(self, user_id: UUID, count: int) -> None:
        await self._db.update_monthly_listeners(user_id, count)

    async def soft_delete(self, user_id: UUID, timestamp: int) -> None:
        await self._db.soft_delete(user_id, timestamp)

    async def restore(self, user_id: UUID) -> None:
        await self._db.restore(user_id)
