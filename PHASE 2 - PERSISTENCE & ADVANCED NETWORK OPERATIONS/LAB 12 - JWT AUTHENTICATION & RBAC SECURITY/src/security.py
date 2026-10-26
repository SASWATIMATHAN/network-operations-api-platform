"""JWT token handling and secure password hashing for Lab 12."""

import os
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from pwdlib import PasswordHash

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_MINUTES = int(
    os.getenv("JWT_ACCESS_TOKEN_MINUTES", "30")
)

if not JWT_SECRET_KEY or len(JWT_SECRET_KEY) < 32:
    raise RuntimeError(
        "Set JWT_SECRET_KEY to a securely generated secret "
        "of at least 32 characters."
    )

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Return an Argon2 password hash."""
    if len(password) < 12:
        raise ValueError("Password must contain at least 12 characters.")
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its stored hash."""
    return password_hash.verify(password, hashed_password)


def create_access_token(
    subject: str,
    role: str,
    expires_minutes: int | None = None,
) -> str:
    """Create a signed JWT with subject, role, issue, and expiry claims."""
    now = datetime.now(timezone.utc)
    lifetime = expires_minutes or JWT_ACCESS_TOKEN_MINUTES

    if lifetime <= 0:
        raise ValueError("Token lifetime must be positive.")

    payload: dict[str, Any] = {
        "sub": subject,
        "role": role,
        "iat": now,
        "exp": now + timedelta(minutes=lifetime),
    }

    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    """Validate a JWT signature and expiry before returning its claims."""
    return jwt.decode(
        token,
        JWT_SECRET_KEY,
        algorithms=[JWT_ALGORITHM],
        options={"require": ["sub", "role", "iat", "exp"]},
    )
