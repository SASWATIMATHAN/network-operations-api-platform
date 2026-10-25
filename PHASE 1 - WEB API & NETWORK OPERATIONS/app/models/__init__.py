"""SQLAlchemy model registrations."""

from app.models.network_inventory import NetworkDevice, NetworkInterface
from app.models.persistence import (
    ConfigurationBackup,
    PersistentAuditRecord,
    PersistentDeviceOperationResult,
    PersistentJob,
    PersistentOperation,
)

__all__ = [
    "NetworkDevice",
    "NetworkInterface",
    "PersistentOperation",
    "PersistentDeviceOperationResult",
    "PersistentJob",
    "PersistentAuditRecord",
    "ConfigurationBackup",
]
