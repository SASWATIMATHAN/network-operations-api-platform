# Lab 12 — JWT Authentication & RBAC Security

## 1. Objective

Implement secure authentication and role-based access control (RBAC) for the Network Operations API Platform using JSON Web Tokens (JWT), Argon2 password hashing, and FastAPI dependencies.

## 2. Architecture

```text
Client
  |
  v
POST /auth/login
  |
  v
Credential Verification
  |
  v
JWT Access Token (HS256)
  |
  v
Bearer Token Authentication
  |
  v
Active User and Current Role Validation
  |
  v
Permission Check (RBAC)
  |
  v
Protected API Endpoint
```

## 3. Technology Stack

- Python 3.12
- FastAPI
- PyJWT
- Argon2 password hashing through pwdlib
- SQLAlchemy
- PostgreSQL for persistent application storage
- Pytest
- In-memory SQLite for isolated API integration tests

## 4. Role and Permission Matrix

| Permission | ADMIN | OPERATOR | VIEWER |
|---|---|---|---|
| Read inventory | Yes | Yes | Yes |
| Read operations | Yes | Yes | Yes |
| Read jobs | Yes | Yes | Yes |
| Write jobs | Yes | Yes | No |
| Read configuration | Yes | Yes | Yes |
| Write configuration | Yes | Yes | No |
| List users | Yes | No | No |
| Create users and assign roles | Yes | No | No |
| Administrator-only actions | Yes | No | No |

## 5. API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/auth/login` | Validate credentials and issue a JWT |
| GET | `/auth/me` | Return the authenticated user's account |
| GET | `/auth/users` | List user accounts; ADMIN only |
| POST | `/auth/users` | Create a user and assign a role; ADMIN only |

New users cannot register publicly. An administrator must create their accounts.

## 6. Security Controls

- Passwords are stored as Argon2 hashes rather than plaintext.
- Passwords must contain at least 12 characters.
- JWTs use HS256 signing and have a configurable expiration; the default is 30 minutes.
- Missing, invalid, or expired tokens are rejected with HTTP 401.
- Authenticated users without the required permission receive HTTP 403.
- Inactive users are denied access.
- The user's current database role is checked against the token role, so role changes invalidate tokens carrying the previous role.
- User-management responses do not expose password hashes.
- JWT secrets are supplied through environment variables and must be at least 32 characters long.

## 7. Project Structure

```text
LAB 12 - JWT AUTHENTICATION & RBAC SECURITY/
├── README.md
├── src/
│   ├── security.py
│   ├── auth_models.py
│   ├── permissions.py
│   ├── dependencies.py
│   ├── auth_router.py
│   └── bootstrap_admin.py
├── tests/
│   ├── test_security_rbac.py
│   └── test_auth_api.py
└── figures/
```

## 8. Verification Results

Command used:

```bash
PYTHONPATH="$LAB/src:$APP${PYTHONPATH:+:$PYTHONPATH}" pytest -v "$LAB/tests"
```

**Latest result: 29 passed, 0 failed.**

The test suite verifies password hashing, JWT claims and validation, token expiry, role permissions, login behavior, unauthorized requests, administrator-only user management, and duplicate-user rejection.

The API integration tests use a temporary in-memory SQLite database. PostgreSQL-backed authentication has not yet been verified.

## 9. Outstanding Verification

Before declaring the deployment fully verified:

1. Restore and verify WSL access to the existing Windows PostgreSQL instance without changing the working NAT configuration needed for GNS3.
2. Create the `auth_users` table using the Lab 12 bootstrap script.
3. Provision the first administrator account.
4. Verify login and user management against persistent PostgreSQL storage.
5. Verify that the existing protected operational endpoints enforce their intended permissions.
6. Confirm that the existing GNS3 routers remain reachable when network-device integration is tested.

## 10. Conclusion

Lab 12's JWT security components, role-permission logic, and authentication API integration tests have passed. PostgreSQL-backed authentication and complete authorization coverage across the existing operational endpoints remain outstanding integration checks.
