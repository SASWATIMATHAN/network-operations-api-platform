
"""Unit tests for Lab 12 password security, JWTs, and RBAC."""

from datetime import datetime, timedelta, timezone

import jwt
import pytest

from permissions import Permission, Role, has_permission
from security import (
    JWT_ALGORITHM,
    JWT_SECRET_KEY,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_hash_and_verification():
    password = "Secure-Test-Password-2026!"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("Wrong-Password-2026!", hashed)


def test_short_password_is_rejected():
    with pytest.raises(ValueError, match="at least 12 characters"):
        hash_password("short")


def test_valid_jwt_contains_required_claims():
    token = create_access_token("test_admin", Role.ADMIN.value)
    claims = decode_access_token(token)

    assert claims["sub"] == "test_admin"
    assert claims["role"] == "ADMIN"
    assert "iat" in claims
    assert "exp" in claims
    assert claims["exp"] > claims["iat"]


def test_invalid_signature_is_rejected():
    token = jwt.encode(
        {
            "sub": "test_admin",
            "role": "ADMIN",
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        },
        "incorrect-signing-secret-that-is-not-the-real-key",
        algorithm=JWT_ALGORITHM,
    )

    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token(token)


def test_expired_jwt_is_rejected():
    now = datetime.now(timezone.utc)
    token = jwt.encode(
        {
            "sub": "test_admin",
            "role": "ADMIN",
            "iat": now - timedelta(minutes=10),
            "exp": now - timedelta(minutes=5),
        },
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )

    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(token)


@pytest.mark.parametrize(
    ("role", "permission", "expected"),
    [
        (Role.ADMIN, Permission.USERS_MANAGE, True),
        (Role.ADMIN, Permission.ADMIN_ACTIONS, True),
        (Role.OPERATOR, Permission.JOBS_WRITE, True),
        (Role.OPERATOR, Permission.CONFIGURATION_WRITE, True),
        (Role.OPERATOR, Permission.USERS_MANAGE, False),
        (Role.OPERATOR, Permission.ADMIN_ACTIONS, False),
        (Role.VIEWER, Permission.INVENTORY_READ, True),
        (Role.VIEWER, Permission.OPERATIONS_READ, True),
        (Role.VIEWER, Permission.JOBS_READ, True),
        (Role.VIEWER, Permission.JOBS_WRITE, False),
        (Role.VIEWER, Permission.CONFIGURATION_WRITE, False),
        (Role.VIEWER, Permission.USERS_MANAGE, False),
    ],
)
def test_role_permission_matrix(role, permission, expected):
    assert has_permission(role, permission) is expected


def test_unknown_role_and_permission_are_denied():
    assert not has_permission("UNKNOWN_ROLE", Permission.JOBS_READ)
    assert not has_permission(Role.ADMIN, "unknown:permission")
