"""FastAPI dependencies for JWT authentication and RBAC enforcement."""

from typing import Annotated, Callable

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db

from auth_models import AuthUser
from permissions import Permission, Role, has_permission
from security import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
    db: Annotated[Session, Depends(get_db)],
) -> AuthUser:
    """Validate the bearer token and load its active user account."""
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise unauthorized

    try:
        claims = decode_access_token(credentials.credentials)
        username = claims.get("sub")
        token_role = Role(claims.get("role", ""))
    except (jwt.InvalidTokenError, ValueError, TypeError):
        raise unauthorized from None

    if not isinstance(username, str) or not username:
        raise unauthorized

    user = db.get(AuthUser, username)

    if user is None or not user.is_active:
        raise unauthorized

    # Re-check the current database role so role changes take effect
    # immediately rather than trusting a stale role embedded in a JWT.
    if user.role != token_role.value:
        raise unauthorized

    return user


def require_permission(
    permission: Permission,
) -> Callable:
    """Create a dependency that enforces a specific permission."""

    def permission_checker(
        user: Annotated[AuthUser, Depends(get_current_user)],
    ) -> AuthUser:
        if not has_permission(user.role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions for this operation.",
            )
        return user

    return permission_checker
