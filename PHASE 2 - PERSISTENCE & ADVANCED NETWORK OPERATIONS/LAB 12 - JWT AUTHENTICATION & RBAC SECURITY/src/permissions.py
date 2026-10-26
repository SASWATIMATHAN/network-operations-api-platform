"""Role definitions and permission policies for Lab 12 RBAC."""

from enum import StrEnum


class Role(StrEnum):
    ADMIN = "ADMIN"
    OPERATOR = "OPERATOR"
    VIEWER = "VIEWER"


class Permission(StrEnum):
    INVENTORY_READ = "inventory:read"
    OPERATIONS_READ = "operations:read"
    JOBS_READ = "jobs:read"
    JOBS_WRITE = "jobs:write"
    CONFIGURATION_READ = "configuration:read"
    CONFIGURATION_WRITE = "configuration:write"
    USERS_READ = "users:read"
    USERS_MANAGE = "users:manage"
    ADMIN_ACTIONS = "admin:actions"


ROLE_PERMISSIONS: dict[Role, frozenset[Permission]] = {
    Role.ADMIN: frozenset(Permission),
    Role.OPERATOR: frozenset(
        {
            Permission.INVENTORY_READ,
            Permission.OPERATIONS_READ,
            Permission.JOBS_READ,
            Permission.JOBS_WRITE,
            Permission.CONFIGURATION_READ,
            Permission.CONFIGURATION_WRITE,
        }
    ),
    Role.VIEWER: frozenset(
        {
            Permission.INVENTORY_READ,
            Permission.OPERATIONS_READ,
            Permission.JOBS_READ,
            Permission.CONFIGURATION_READ,
        }
    ),
}


def has_permission(role: str | Role, permission: str | Permission) -> bool:
    """Return whether a role is allowed to perform a permission."""
    try:
        normalized_role = Role(role)
        normalized_permission = Permission(permission)
    except ValueError:
        return False

    return normalized_permission in ROLE_PERMISSIONS[normalized_role]
