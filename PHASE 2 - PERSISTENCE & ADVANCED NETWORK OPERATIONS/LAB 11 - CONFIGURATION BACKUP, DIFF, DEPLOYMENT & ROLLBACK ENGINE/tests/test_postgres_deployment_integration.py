
"""Integration tests for Lab 11 deployment with Lab 10 PostgreSQL backups."""

import os
import sys
from pathlib import Path

import pytest

LAB11_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = LAB11_ROOT.parents[1]
APP_ROOT = PROJECT_ROOT / "PHASE 1 - WEB API & NETWORK OPERATIONS"

sys.path.insert(0, str(LAB11_ROOT / "src"))
sys.path.insert(0, str(APP_ROOT))


from app.configuration_backup_service import ConfigurationBackupService
from persistent_deployment_workflow import (
    PersistentConfigurationDeploymentWorkflow,
)


DEVICE_ID = "LAB10-R1"

ORIGINAL = """! LAB11 integration test - original configuration
hostname LAB10-CORE-R1
interface Loopback0
 ip address 198.51.100.1 255.255.255.255
!
"""

PROPOSED = """! LAB11 integration test - proposed configuration
hostname LAB10-CORE-R1
interface Loopback0
 ip address 198.51.100.2 255.255.255.255
!
"""


class MockDevice:
    """Simulate device configuration operations without network access."""

    def __init__(self, fail_first_apply=False):
        self.configuration = ORIGINAL
        self.apply_calls = []
        self.fail_first_apply = fail_first_apply

    def get_running_configuration(self, device_id):
        assert device_id == DEVICE_ID
        return self.configuration

    def apply_configuration(self, device_id, configuration):
        assert device_id == DEVICE_ID
        self.apply_calls.append(configuration)

        if self.fail_first_apply and len(self.apply_calls) == 1:
            raise RuntimeError("Simulated deployment failure")

        self.configuration = configuration
        return "Mock configuration applied"


@pytest.fixture
def backup_service():
    """Use the actual configured PostgreSQL backup service."""
    if not os.getenv("DB_PASSWORD"):
        pytest.skip("DB_PASSWORD is not configured")

    service = ConfigurationBackupService()

    try:
        # Read-only preflight; do not create or modify inventory.
        from app.database import SessionLocal
        from app.models.network_inventory import NetworkDevice

        with SessionLocal() as session:
            device = session.get(NetworkDevice, DEVICE_ID)
            if device is None:
                pytest.skip(
                    f"Required inventory device {DEVICE_ID} is missing"
                )
    except Exception as exc:
        pytest.skip(f"PostgreSQL preflight failed: {exc}")

    return service


def test_postgres_backup_precedes_successful_deployment(backup_service):
    device = MockDevice()
    workflow = PersistentConfigurationDeploymentWorkflow(
        adapter=device,
        backup_service=backup_service,
        requested_by="lab11-integration-test",
    )

    result = workflow.deploy(
        device_id=DEVICE_ID,
        configuration=PROPOSED,
        version=2,
        verify=lambda device_id: device.configuration == PROPOSED,
    )

    assert result.deployment.success is True
    assert result.deployment.status == "deployed"
    assert result.persistent_backup_id is not None
    assert device.configuration == PROPOSED
    assert device.apply_calls == [PROPOSED]

    stored_backup = backup_service.get_backup(
        result.persistent_backup_id
    )
    assert stored_backup is not None
    assert stored_backup.device_id == DEVICE_ID
    assert stored_backup.configuration == ORIGINAL
    assert stored_backup.requested_by == "lab11-integration-test"


def test_deployment_failure_rolls_back_after_persistent_backup(
    backup_service,
):
    device = MockDevice(fail_first_apply=True)
    workflow = PersistentConfigurationDeploymentWorkflow(
        adapter=device,
        backup_service=backup_service,
        requested_by="lab11-integration-test",
    )

    result = workflow.deploy(
        device_id=DEVICE_ID,
        configuration=PROPOSED,
        version=3,
        verify=lambda device_id: device.configuration == ORIGINAL,
    )

    assert result.persistent_backup_id is not None
    assert result.deployment.success is False
    assert result.deployment.status == "rolled_back"
    assert result.deployment.rollback_attempted is True
    assert result.deployment.rollback_succeeded is True
    assert device.configuration == ORIGINAL
    assert device.apply_calls == [PROPOSED, ORIGINAL]

    stored_backup = backup_service.get_backup(
        result.persistent_backup_id
    )
    assert stored_backup is not None
    assert stored_backup.configuration == ORIGINAL
