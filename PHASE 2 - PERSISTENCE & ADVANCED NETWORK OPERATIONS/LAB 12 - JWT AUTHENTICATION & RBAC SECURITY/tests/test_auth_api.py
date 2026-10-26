"""API integration tests for Lab 12 JWT authentication and RBAC."""

import os

os.environ.setdefault(
    "JWT_SECRET_KEY",
    "lab12-test-secret-key-at-least-32-characters-long",
)

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from auth_models import AuthUser
from security import hash_password, create_access_token


test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)


@pytest.fixture
def client():
    """Create an isolated SQLite database for each API test."""
    Base.metadata.create_all(bind=test_engine)

    with TestSessionLocal() as db:
        db.add_all(
            [
                AuthUser(
                    username="admin_test",
                    password_hash=hash_password("AdminPassword123!"),
                    role="ADMIN",
                    is_active=True,
                ),
                AuthUser(
                    username="operator_test",
                    password_hash=hash_password("OperatorPassword123!"),
                    role="OPERATOR",
                    is_active=True,
                ),
                AuthUser(
                    username="viewer_test",
                    password_hash=hash_password("ViewerPassword123!"),
                    role="VIEWER",
                    is_active=True,
                ),
            ]
        )
        db.commit()

    def override_get_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


def login(client, username, password):
    """Return a JWT for a test account."""
    response = client.post(
        "/auth/login",
        json={"username": username, "password": password},
    )
    return response


def bearer(token):
    """Build an HTTP Bearer authorization header."""
    return {"Authorization": f"Bearer {token}"}


def test_login_returns_access_token(client):
    response = login(client, "admin_test", "AdminPassword123!")

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["expires_in"] == 1800
    assert body["access_token"]


def test_login_rejects_wrong_password(client):
    response = login(client, "admin_test", "WrongPassword123!")

    assert response.status_code == 401


def test_login_rejects_unknown_user(client):
    response = login(client, "unknown_test", "SomePassword123!")

    assert response.status_code == 401


def test_me_rejects_missing_token(client):
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_me_accepts_valid_admin_token(client):
    token = login(client, "admin_test", "AdminPassword123!").json()[
        "access_token"
    ]

    response = client.get("/auth/me", headers=bearer(token))

    assert response.status_code == 200
    assert response.json()["username"] == "admin_test"
    assert response.json()["role"] == "ADMIN"


def test_me_rejects_invalid_token(client):
    response = client.get(
        "/auth/me",
        headers=bearer("not.a.valid.token"),
    )

    assert response.status_code == 401


def test_viewer_cannot_list_users(client):
    token = login(
        client, "viewer_test", "ViewerPassword123!"
    ).json()["access_token"]

    response = client.get("/auth/users", headers=bearer(token))

    assert response.status_code == 403


def test_operator_cannot_create_users(client):
    token = login(
        client, "operator_test", "OperatorPassword123!"
    ).json()["access_token"]

    response = client.post(
        "/auth/users",
        headers=bearer(token),
        json={
            "username": "new_viewer",
            "password": "NewViewerPassword123!",
            "role": "VIEWER",
        },
    )

    assert response.status_code == 403


def test_admin_can_list_users(client):
    token = login(
        client, "admin_test", "AdminPassword123!"
    ).json()["access_token"]

    response = client.get("/auth/users", headers=bearer(token))

    assert response.status_code == 200
    assert {user["username"] for user in response.json()} == {
        "admin_test",
        "operator_test",
        "viewer_test",
    }
    assert all("password_hash" not in user for user in response.json())


def test_admin_can_create_user(client):
    token = login(
        client, "admin_test", "AdminPassword123!"
    ).json()["access_token"]

    response = client.post(
        "/auth/users",
        headers=bearer(token),
        json={
            "username": "new_viewer",
            "password": "NewViewerPassword123!",
            "role": "VIEWER",
        },
    )

    assert response.status_code == 201
    assert response.json()["username"] == "new_viewer"
    assert response.json()["role"] == "VIEWER"


def test_duplicate_username_is_rejected(client):
    token = login(
        client, "admin_test", "AdminPassword123!"
    ).json()["access_token"]

    response = client.post(
        "/auth/users",
        headers=bearer(token),
        json={
            "username": "viewer_test",
            "password": "AnotherPassword123!",
            "role": "VIEWER",
        },
    )

    assert response.status_code == 409
