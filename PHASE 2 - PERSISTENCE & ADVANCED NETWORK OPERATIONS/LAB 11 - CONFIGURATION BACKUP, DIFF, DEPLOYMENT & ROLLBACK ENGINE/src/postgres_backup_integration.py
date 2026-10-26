
"""Bridge Lab 11 deployment workflows to the Lab 10 PostgreSQL backup service."""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Locate the existing Phase 1 application without copying its code.
_THIS_FILE = Path(__file__).resolve()
_PROJECT_ROOT = next(
    (
        parent
        for parent in _THIS_FILE.parents
        if parent.name == "PROJECT 3 - NETWORK OPERATIONS API PLATFORM"
    ),
    None,
)

if _PROJECT_ROOT is None:
    raise RuntimeError("Could not locate the network operations project root")

_APP_DIR = _PROJECT_ROOT / "PHASE 1 - WEB API & NETWORK OPERATIONS"

if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))


def create_postgres_backup_service():
    """Create the existing Lab 10 backup service.

    The application's normal DB_* environment variables must be configured.
    This function does not create tables or modify the database schema.
    """
    from app.configuration_backup_service import ConfigurationBackupService

    return ConfigurationBackupService()


def create_persistent_deployment_workflow(
    adapter,
    requested_by: str = "lab11-deployment",
):
    """Create Lab 11's persistent deployment workflow using Lab 10 backups."""
    from persistent_deployment_workflow import (
        PersistentConfigurationDeploymentWorkflow,
    )

    backup_service = create_postgres_backup_service()

    return PersistentConfigurationDeploymentWorkflow(
        adapter=adapter,
        backup_service=backup_service,
        requested_by=requested_by,
    )


def check_database_configuration() -> dict[str, str]:
    """Report database connection settings without revealing credentials."""
    return {
        "DB_HOST": os.getenv("DB_HOST", "127.0.0.1"),
        "DB_PORT": os.getenv("DB_PORT", "5432"),
        "DB_NAME": os.getenv("DB_NAME", "network_operations"),
        "DB_USER": os.getenv("DB_USER", "network_operations_app"),
        "DB_PASSWORD": (
            "configured" if os.getenv("DB_PASSWORD") else "missing"
        ),
    }
