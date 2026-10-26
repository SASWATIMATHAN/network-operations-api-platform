
"""Tests for persistent backup integration in Lab 11."""

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from persistent_deployment_workflow import (
    PersistentConfigurationDeploymentWorkflow,
)


ORIGINAL = """hostname EDGE-R1
interface Loopback0
 ip address 198.51.100.1 255.255.255.255
!
"""

PROPOSED = """hostname EDGE-R1
interface Loopback0
 ip address 198.51.100.2 255.255.255.255
!
"""


class MockDevice:
    """Simulate a network device without a real connection."""

    def __init__(self):
        self.configuration = ORIGINAL
        self.apply_calls = []

    def get_running_configuration(self, device_id):
        return self.configuration

    def apply_configuration(self, device_id, configuration):
        self.apply_calls.append(configuration)
        self.configuration = configuration
        return "Mock configuration applied"


class MockBackupService:
    """Simulate Lab 10 persistent backup behavior."""

    def __init__(self, fail=False):
        self.fail = fail
        self.saved_backups = []

    def save_backup(self, device_id, configuration, requested_by):
        if self.fail:
            raise RuntimeError("Simulated PostgreSQL backup failure")

        self.saved_backups.append(
            {
                "device_id": device_id,
                "configuration": configuration,
                "requested_by": requested_by,
            }
        )
        return SimpleNamespace(backup_id="backup-test-001")


def test_persistent_backup_is_saved_before_deployment():
    device = MockDevice()
    backup_service = MockBackupService()

    workflow = PersistentConfigurationDeploymentWorkflow(
        adapter=device,
        backup_service=backup_service,
        requested_by="lab11-test",
    )

    result = workflow.deploy(
        device_id="EDGE-R1",
        configuration=PROPOSED,
        version=2,
        verify=lambda device_id: device.configuration == PROPOSED,
    )

    assert result.deployment.success is True
    assert result.deployment.status == "deployed"
    assert result.persistent_backup_id == "backup-test-001"

    assert len(backup_service.saved_backups) == 1
    assert backup_service.saved_backups[0]["device_id"] == "EDGE-R1"
    assert backup_service.saved_backups[0]["configuration"] == ORIGINAL
    assert backup_service.saved_backups[0]["requested_by"] == "lab11-test"

    assert device.configuration == PROPOSED
    assert device.apply_calls == [PROPOSED]


def test_backup_failure_prevents_configuration_deployment():
    device = MockDevice()
    backup_service = MockBackupService(fail=True)

    workflow = PersistentConfigurationDeploymentWorkflow(
        adapter=device,
        backup_service=backup_service,
    )

    result = workflow.deploy(
        device_id="EDGE-R1",
        configuration=PROPOSED,
        version=2,
        verify=lambda device_id: device.configuration == PROPOSED,
    )

    assert result.deployment.success is False
    assert result.deployment.status == "backup_failed"
    assert "deployment was not attempted" in result.deployment.message
    assert result.persistent_backup_id is None

    assert device.configuration == ORIGINAL
    assert device.apply_calls == []


def test_destructive_configuration_is_rejected_without_backup():
    device = MockDevice()
    backup_service = MockBackupService()

    workflow = PersistentConfigurationDeploymentWorkflow(
        adapter=device,
        backup_service=backup_service,
    )

    result = workflow.deploy(
        device_id="EDGE-R1",
        configuration="hostname EDGE-R1\nwrite erase\n",
        version=2,
        verify=lambda device_id: True,
    )

    assert result.deployment.status == "rejected"
    assert result.persistent_backup_id is None
    assert backup_service.saved_backups == []
    assert device.apply_calls == []
