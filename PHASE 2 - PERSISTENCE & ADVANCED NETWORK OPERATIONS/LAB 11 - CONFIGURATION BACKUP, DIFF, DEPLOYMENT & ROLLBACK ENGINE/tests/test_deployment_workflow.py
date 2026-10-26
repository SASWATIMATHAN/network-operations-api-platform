
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from deployment_workflow import ConfigurationDeploymentWorkflow  # noqa: E402


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
    """In-memory device adapter for deterministic workflow tests."""

    def __init__(self, configuration=ORIGINAL, fail_on_apply_number=None):
        self.configuration = configuration
        self.apply_calls = []
        self.fail_on_apply_number = fail_on_apply_number

    def get_running_configuration(self, device_id):
        return self.configuration

    def apply_configuration(self, device_id, configuration):
        self.apply_calls.append(configuration)

        if len(self.apply_calls) == self.fail_on_apply_number:
            raise RuntimeError("Simulated device configuration error")

        self.configuration = configuration
        return "Mock configuration applied"


def test_successful_deployment_captures_prechange_snapshot():
    device = MockDevice()
    workflow = ConfigurationDeploymentWorkflow(device)

    result = workflow.deploy(
        device_id="EDGE-R1",
        configuration=PROPOSED,
        version=2,
        verify=lambda device_id: device.configuration == PROPOSED,
    )

    assert result.success
    assert result.status == "deployed"
    assert result.pre_deployment_snapshot is not None
    assert result.pre_deployment_snapshot.configuration == ORIGINAL
    assert result.pre_deployment_snapshot.version == 2
    assert not result.rollback_attempted
    assert device.configuration == PROPOSED
    assert len(device.apply_calls) == 1


def test_destructive_configuration_is_rejected_before_device_access():
    device = MockDevice()
    workflow = ConfigurationDeploymentWorkflow(device)

    result = workflow.deploy(
        device_id="EDGE-R1",
        configuration="hostname EDGE-R1\nwrite erase\n",
        version=2,
        verify=lambda device_id: True,
    )

    assert not result.success
    assert result.status == "rejected"
    assert result.validation_errors
    assert result.pre_deployment_snapshot is None
    assert device.apply_calls == []
    assert device.configuration == ORIGINAL


def test_failed_postcheck_rolls_back_and_verifies_original():
    device = MockDevice()
    workflow = ConfigurationDeploymentWorkflow(device)
    verification_calls = 0

    def verify(device_id):
        nonlocal verification_calls
        verification_calls += 1
        return verification_calls > 1 and device.configuration == ORIGINAL

    result = workflow.deploy(
        device_id="EDGE-R1",
        configuration=PROPOSED,
        version=2,
        verify=verify,
    )

    assert not result.success
    assert result.status == "rolled_back"
    assert result.rollback_attempted
    assert result.rollback_succeeded is True
    assert device.configuration == ORIGINAL
    assert device.apply_calls == [PROPOSED, ORIGINAL]


def test_deployment_exception_triggers_rollback():
    device = MockDevice(fail_on_apply_number=1)
    workflow = ConfigurationDeploymentWorkflow(device)

    result = workflow.deploy(
        device_id="EDGE-R1",
        configuration=PROPOSED,
        version=2,
        verify=lambda device_id: True,
    )

    assert not result.success
    assert result.status == "rolled_back"
    assert result.rollback_attempted
    assert result.rollback_succeeded is True
    assert device.configuration == ORIGINAL
    assert device.apply_calls == [PROPOSED, ORIGINAL]


def test_rollback_failure_is_reported_explicitly():
    device = MockDevice(fail_on_apply_number=2)
    workflow = ConfigurationDeploymentWorkflow(device)

    result = workflow.deploy(
        device_id="EDGE-R1",
        configuration=PROPOSED,
        version=2,
        verify=lambda device_id: False,
    )

    assert not result.success
    assert result.status == "rollback_failed"
    assert result.rollback_attempted
    assert result.rollback_succeeded is False
    assert "rollback also failed" in result.message.lower()


def test_read_failure_stops_before_configuration_change():
    class UnavailableDevice(MockDevice):
        def get_running_configuration(self, device_id):
            raise RuntimeError("Simulated connection failure")

    device = UnavailableDevice()
    workflow = ConfigurationDeploymentWorkflow(device)

    result = workflow.deploy(
        device_id="EDGE-R1",
        configuration=PROPOSED,
        version=2,
        verify=lambda device_id: True,
    )

    assert not result.success
    assert result.status == "precheck_failed"
    assert not result.rollback_attempted
    assert device.apply_calls == []
