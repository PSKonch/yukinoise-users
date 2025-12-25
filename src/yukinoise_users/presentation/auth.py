from fastapi import FastAPI
from yukinoise_auth import init_auth, KeycloakAuthMiddleware

from yukinoise_users.core.conf import keycloak_settings


def setup_auth(app: FastAPI) -> None:
    init_auth(keycloak_settings)
    app.add_middleware(
        KeycloakAuthMiddleware,
        settings=keycloak_settings,
        exclude_paths=[
            "/health",
            "/docs",
            "/openapi.json",
            "/redoc",
        ],
        optional_paths=[
            "/api/v1/profiles",
        ],
    )
