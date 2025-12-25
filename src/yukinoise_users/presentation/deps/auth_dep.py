from typing import Annotated

from fastapi import Depends
from yukinoise_auth import (
    Principal,
    get_current_principal,
    get_optional_principal,
    require_realm_role,
    require_any_realm_role,
)

# Principal dependencies
CurrentUser = Annotated[Principal, Depends(get_current_principal)]
OptionalUser = Annotated[Principal | None, Depends(get_optional_principal)]

# Role-based dependencies
AdminUser = Annotated[Principal, Depends(require_realm_role("admin"))]
ModeratorUser = Annotated[Principal, Depends(require_realm_role("moderator"))]
UserRole = Annotated[Principal, Depends(require_realm_role("user"))]

# Multi-role dependency
AdminOrModerator = Annotated[
    Principal, Depends(require_any_realm_role(["admin", "moderator"]))
]
