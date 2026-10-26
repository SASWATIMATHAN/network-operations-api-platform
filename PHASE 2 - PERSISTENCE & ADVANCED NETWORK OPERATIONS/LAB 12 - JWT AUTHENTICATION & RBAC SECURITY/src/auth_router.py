"""Login and administrator-controlled user management endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db

from auth_models import AuthUser
from dependencies import get_current_user, require_permission
from permissions import Permission, Role
from security import create_access_token, hash_password, verify_password

router = APIRouter(tags=["Authentication and RBAC"])


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=80)
    password: str = Field(min_length=1, max_length=256)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserCreateRequest(BaseModel):
    username: str = Field(min_length=3, max_length=80, pattern=r"^[A-Za-z0-9_.-]+$")
    password: str = Field(min_length=12, max_length=256)
    role: Role


class UserResponse(BaseModel):
    username: str
    role: Role
    is_active: bool


@router.post("/auth/login", response_model=TokenResponse)
def login(
    request: LoginRequest,
    db: Annotated[Session, Depends(get_db)],
) -> TokenResponse:
    """Authenticate an account and issue a signed JWT."""
    user = db.get(AuthUser, request.username)

    if (
        user is None
        or not user.is_active
        or not verify_password(request.password, user.password_hash)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(user.username, user.role)

    from security import JWT_ACCESS_TOKEN_MINUTES

    return TokenResponse(
        access_token=token,
        expires_in=JWT_ACCESS_TOKEN_MINUTES * 60,
    )


@router.get("/auth/me", response_model=UserResponse)
def get_my_account(
    user: Annotated[AuthUser, Depends(get_current_user)],
) -> UserResponse:
    """Return the authenticated user's account details."""
    return UserResponse(
        username=user.username,
        role=Role(user.role),
        is_active=user.is_active,
    )


@router.post(
    "/auth/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    request: UserCreateRequest,
    db: Annotated[Session, Depends(get_db)],
    admin: Annotated[
        AuthUser,
        Depends(require_permission(Permission.USERS_MANAGE)),
    ],
) -> UserResponse:
    """Allow administrators to create accounts and assign roles."""
    if db.get(AuthUser, request.username) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists.",
        )

    user = AuthUser(
        username=request.username,
        password_hash=hash_password(request.password),
        role=request.role.value,
        is_active=True,
    )

    db.add(user)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists.",
        ) from None

    db.refresh(user)

    return UserResponse(
        username=user.username,
        role=Role(user.role),
        is_active=user.is_active,
    )


@router.get(
    "/auth/users",
    response_model=list[UserResponse],
)
def list_users(
    db: Annotated[Session, Depends(get_db)],
    admin: Annotated[
        AuthUser,
        Depends(require_permission(Permission.USERS_READ)),
    ],
) -> list[UserResponse]:
    """Allow administrators to list accounts without exposing password hashes."""
    users = db.scalars(select(AuthUser).order_by(AuthUser.username)).all()

    return [
        UserResponse(
            username=user.username,
            role=Role(user.role),
            is_active=user.is_active,
        )
        for user in users
    ]
