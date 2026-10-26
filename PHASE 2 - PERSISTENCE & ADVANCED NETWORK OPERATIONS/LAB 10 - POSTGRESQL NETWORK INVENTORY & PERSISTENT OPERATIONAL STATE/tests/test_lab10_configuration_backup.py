"""Tests for persistent configuration backups and checksum integrity."""

import hashlib

import pytest
from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models.network_inventory import NetworkDevice, NetworkInterface
from app.models.persistence import (
    ConfigurationBackup,
    PersistentAuditRecord,
    PersistentDeviceOperationResult,
    PersistentJob,
    PersistentOperation,
)
from app.configuration_backup_service import (
    ConfigurationBackupIntegrityError,
    ConfigurationBackupService,
)


@pytest.fixture
def backup_environment():
    """Create an isolated in-memory database for each test."""

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)

    test_sessions = sessionmaker(
        bind=engine,
        expire_on_commit=False,
        autoflush=False,
    )

    with test_sessions.begin() as session:
        session.add(
            NetworkDevice(
                device_id="LAB10-R1",
                hostname="R1",
                device_type="router",
                management_ip="192.0.2.10",
                status="active",
                description="Configuration backup test device",
            )
        )

    service = ConfigurationBackupService(test_sessions)

    yield service, test_sessions

    Base.metadata.drop_all(engine)
    engine.dispose()


def test_save_backup_persists_configuration_and_integrity_metadata(
    backup_environment,
):
    service, sessions = backup_environment
    configuration = (
        "hostname R1\n"
        "interface GigabitEthernet0/0\n"
        " ip address 192.0.2.10 255.255.255.0\n"
    )

    backup = service.save_backup(
        device_id="LAB10-R1",
        configuration=configuration,
        requested_by="lab10-test",
    )

    expected_checksum = hashlib.sha256(
        configuration.encode("utf-8")
    ).hexdigest()

    assert backup.backup_id
    assert backup.device_id == "LAB10-R1"
    assert backup.hostname == "R1"
    assert backup.configuration == configuration
    assert backup.checksum_sha256 == expected_checksum
    assert backup.size_bytes == len(configuration.encode("utf-8"))
    assert backup.requested_by == "lab10-test"

    with sessions() as session:
        stored = session.get(ConfigurationBackup, backup.backup_id)

    assert stored is not None
    assert stored.configuration == configuration
    assert stored.checksum_sha256 == expected_checksum


def test_backup_size_uses_utf8_bytes_not_character_count(
    backup_environment,
):
    service, _ = backup_environment
    configuration = "hostname R1\n! café\n"

    backup = service.save_backup(
        device_id="LAB10-R1",
        configuration=configuration,
        requested_by="lab10-test",
    )

    assert backup.size_bytes == len(configuration.encode("utf-8"))
    assert backup.size_bytes != len(configuration)


def test_get_backup_verifies_checksum_and_missing_backup(
    backup_environment,
):
    service, _ = backup_environment

    backup = service.save_backup(
        device_id="LAB10-R1",
        configuration="hostname R1\n",
        requested_by="lab10-test",
    )

    retrieved = service.get_backup(backup.backup_id)

    assert retrieved is not None
    assert retrieved.configuration == "hostname R1\n"
    assert service.get_backup("nonexistent-backup-id") is None


def test_get_backup_rejects_modified_configuration(
    backup_environment,
):
    service, sessions = backup_environment

    backup = service.save_backup(
        device_id="LAB10-R1",
        configuration="hostname R1\n",
        requested_by="lab10-test",
    )

    with sessions.begin() as session:
        session.execute(
            update(ConfigurationBackup)
            .where(ConfigurationBackup.backup_id == backup.backup_id)
            .values(configuration="hostname TAMPERED\n")
        )

    with pytest.raises(ConfigurationBackupIntegrityError):
        service.get_backup(backup.backup_id)


def test_save_backup_rejects_unknown_device(backup_environment):
    service, _ = backup_environment

    with pytest.raises(LookupError, match="Network device not found"):
        service.save_backup(
            device_id="MISSING-DEVICE",
            configuration="hostname UNKNOWN\n",
            requested_by="lab10-test",
        )


def test_list_backups_can_filter_by_device(backup_environment):
    service, _ = backup_environment

    first = service.save_backup(
        device_id="LAB10-R1",
        configuration="hostname R1\n",
        requested_by="lab10-test",
    )
    second = service.save_backup(
        device_id="LAB10-R1",
        configuration="hostname R1\n! second backup\n",
        requested_by="lab10-test",
    )

    backups = service.list_backups(device_id="LAB10-R1")
    missing_device_backups = service.list_backups(device_id="MISSING")

    backup_ids = {item.backup_id for item in backups}
    assert backup_ids == {first.backup_id, second.backup_id}
    assert missing_device_backups == []


def test_save_backup_rejects_empty_identity_fields(backup_environment):
    service, _ = backup_environment

    with pytest.raises(ValueError, match="device_id"):
        service.save_backup(
            device_id=" ",
            configuration="hostname R1\n",
            requested_by="lab10-test",
        )

    with pytest.raises(ValueError, match="requested_by"):
        service.save_backup(
            device_id="LAB10-R1",
            configuration="hostname R1\n",
            requested_by=" ",
        )
