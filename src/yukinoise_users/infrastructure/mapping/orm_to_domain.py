from yukinoise_users.domain.models import (
    User,
    Profile,
    UserSettings,
    UserAuditLog,
    OutboxEvent,
)
from yukinoise_users.infrastructure.database.models.users_model import UserORM
from yukinoise_users.infrastructure.database.models.outbox_event_model import (
    OutboxEventORM,
)
from yukinoise_users.infrastructure.database.models.profiles_model import ProfileORM
from yukinoise_users.infrastructure.database.models.user_settings_model import (
    UserSettingsORM,
)
from yukinoise_users.infrastructure.database.models.user_audit_logs_model import (
    UserAuditLogORM,
)


def user_orm_to_domain(user_orm: UserORM) -> User:
    profile = None
    if getattr(user_orm, "profile", None) is not None:
        p = user_orm.profile
        profile = Profile(
            user_id=p.user_id,
            display_name=p.display_name,
            bio=p.bio,
            avatar_url=p.avatar_url,
            banner_url=p.banner_url,
            location=p.location,
            social_links=p.social_links,
            preferred_genres=p.preferred_genres,
            contact_email=p.contact_email,
            tags=p.tags,
            monthly_listeners=p.monthly_listeners,
            followers_count=p.followers_count,
            following_count=p.following_count,
            releases_count=p.releases_count,
            featured_in_releases_count=p.featured_in_releases_count,
            verified=p.verified,
            updated_at=p.updated_at,
            deleted_at=p.deleted_at,
        )

    settings = None
    if getattr(user_orm, "settings", None) is not None:
        s = user_orm.settings
        settings = UserSettings(
            user_id=s.user_id,
            dark_mode=s.dark_mode,
            language=s.language,
            playback_quality=s.playback_quality,
            notifications_enabled=s.notifications_enabled,
            autoplay_enabled=s.autoplay_enabled,
            data_consent=s.data_consent,
            privacy_settings=s.privacy_settings,
            updated_at=s.updated_at,
        )

    return User(
        id=user_orm.id,
        status=user_orm.status,
        email_verified=user_orm.email_verified,
        created_at=user_orm.created_at,
        updated_at=user_orm.updated_at,
        last_login_at=user_orm.last_login_at,
        deleted_at=user_orm.deleted_at,
        profile=profile,
        settings=settings,
    )


def profile_orm_to_domain(profile_orm: ProfileORM | None) -> Profile | None:
    if profile_orm is None:
        return None
    p = profile_orm
    return Profile(
        user_id=p.user_id,
        display_name=p.display_name,
        bio=p.bio,
        avatar_url=p.avatar_url,
        banner_url=p.banner_url,
        location=p.location,
        social_links=p.social_links,
        preferred_genres=p.preferred_genres,
        contact_email=p.contact_email,
        tags=p.tags,
        monthly_listeners=p.monthly_listeners,
        followers_count=p.followers_count,
        following_count=p.following_count,
        releases_count=p.releases_count,
        featured_in_releases_count=p.featured_in_releases_count,
        verified=p.verified,
        updated_at=p.updated_at,
        deleted_at=p.deleted_at,
    )


def outbox_orm_to_domain(outbox_orm: OutboxEventORM) -> OutboxEvent:
    return OutboxEvent(
        id=outbox_orm.id,
        event_type=outbox_orm.event_type,
        created_at=outbox_orm.created_at,
        payload=outbox_orm.payload,
        updated_at=outbox_orm.updated_at,
        status=outbox_orm.status,
        retry_count=outbox_orm.retry_count,
        error=outbox_orm.error,
    )


def settings_orm_to_domain(settings_orm: UserSettingsORM | None) -> UserSettings | None:
    if settings_orm is None:
        return None
    s = settings_orm
    return UserSettings(
        user_id=s.user_id,
        dark_mode=s.dark_mode,
        language=s.language,
        playback_quality=s.playback_quality,
        notifications_enabled=s.notifications_enabled,
        autoplay_enabled=s.autoplay_enabled,
        data_consent=s.data_consent,
        privacy_settings=s.privacy_settings,
        updated_at=s.updated_at,
    )


def audit_log_orm_to_domain(log_orm: UserAuditLogORM) -> UserAuditLog:
    return UserAuditLog(
        id=log_orm.id,
        user_id=log_orm.user_id,
        action=log_orm.action,
        changed_by=log_orm.changed_by,
        timestamp=log_orm.timestamp,
        details=log_orm.details,
    )
