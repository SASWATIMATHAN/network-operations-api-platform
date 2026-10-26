"""Persistent configuration backups with SHA-256 integrity verification."""

from __future__ import annotations

import hashlib
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.database import SessionLocal
from app.models.network_inventory import NetworkDevice
from app.models.persistence import ConfigurationBackup


class ConfigurationBackupIntegrityError(ValueError):
    """Raised when a stored configuration fails its checksum verification."""


class ConfigurationBackupService:
    """Store, retrieve, and verify device configuration backups."""

    def __init__(self, session_factory: sessionmaker | None = None) -> None:
        self._session_factory = session_factory or SessionLocal

    def save_backup(
        self,
        device_id: str,
        configuration: str,
        requested_by: str,
    ) -> ConfigurationBackup:
        """Persist a configuration and calculate its integrity metadata."""

        if not device_id.strip():
            raise ValueError("device_id must not be empty")
        if not requested_by.strip():
            raise ValueError("requested_by must not be empty")
        if not isinstance(configuration, str):
            raise TypeError("configuration must be a string")

        configuration_bytes = configuration.encode("utf-8")
        checksum = hashlib.sha256(configuration_bytes).hexdigest()

        with self._session_factory.begin() as session:
            device = session.get(NetworkDevice, device_id)
            if device is None:
                raise LookupError(f"Network device not found: {device_id}")

            backup = ConfigurationBackup(
                backup_id=str(uuid4()),
                device_id=device.device_id,
                hostname=device.hostname,
                configuration=configuration,
                checksum_sha256=checksum,
                size_bytes=len(configuration_bytes),
                requested_by=requested_by,
            )
            session.add(backup)
            session.flush()

        return backup

    def get_backup(
        self,
        backup_id: str,
    ) -> ConfigurationBackup | None:
        """Retrieve a backup and verify its configuration checksum."""

        with self._session_factory() as session:
            backup = session.get(ConfigurationBackup, backup_id)

            if backup is None:
                return None

            expected_checksum = hashlib.sha256(
                backup.configuration.encode("utf-8")
            ).hexdigest()

            if expected_checksum != backup.checksum_sha256:
                raise ConfigurationBackupIntegrityError(
                    f"Checksum verification failed for backup {backup_id}"
                )

            return backup

    def list_backups(
        self,
        device_id: str | None = None,
    ) -> list[ConfigurationBackup]:
        """List backups, optionally restricted to one device."""

        statement = select(ConfigurationBackup).order_by(
            ConfigurationBackup.captured_at.desc(),
            ConfigurationBackup.backup_id,
        )

        if device_id is not None:
            statement = statement.where(
                ConfigurationBackup.device_id == device_id
            )

        with self._session_factory() as session:
            return list(session.scalars(statement).all())
