
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from acl_deployment_workflow import ACLDeploymentWorkflow
from security_policy import ACLAction, ACLProtocol, ACLRule, SecurityPolicy


class FakeRouter:
    """In-memory router simulator; never connects to a real device."""

    def __init__(self, configuration=None, fail_apply=False):
        self.configuration = configuration or (
            "hostname R1\n"
            "interface GigabitEthernet0/0\n"
            " no shutdown\n"
            "!\n"
        )
        self.fail_apply = fail_apply
        self.apply_calls = []
        self.read_calls = 0

    def get_running_configuration(self, device_id):
        self.read_calls += 1
        return self.configuration

    def apply_configuration(self, device_id, configuration):
        self.apply_calls.append(configuration)

        if self.fail_apply:
            raise RuntimeError("Simulated device configuration failure")

        # Simulate IOS accepting the proposed configuration.
        self.configuration = (
            self.configuration.rstrip()
            + "\n"
            + configuration
            + "\n"
        )
        return "Simulated configuration accepted"


class FakeBackupService:
    def __init__(self, fail=False):
        self.fail = fail
        self.saved = []

    def save_backup(self, device_id, configuration, requested_by):
        if self.fail:
            raise RuntimeError("Simulated persistent backup failure")

        self.saved.append(
            {
                "device_id": device_id,
                "configuration": configuration,
                "requested_by": requested_by,
            }
        )
        return SimpleNamespace(backup_id="test-backup-001")


def make_policy(action=ACLAction.PERMIT):
    return SecurityPolicy(
        policy_id="WEB-ACCESS",
        device_id="R1",
        acl_name="LAB13_WEB_FILTER",
        interface="GigabitEthernet0/0",
        direction="in",
        rules=(
            ACLRule(
                sequence=10,
                action=action,
                protocol=ACLProtocol.TCP,
                source="192.0.2.0/24",
                destination="198.51.100.10",
                destination_port=443,
            ),
        ),
    )


def test_successful_deployment_saves_backup():
    router = FakeRouter()
    backups = FakeBackupService()

    result = ACLDeploymentWorkflow(router, backups).deploy(make_policy())

    assert result.success
    assert result.status == "deployed"
    assert result.persistent_backup_id == "test-backup-001"
    assert len(backups.saved) == 1
    assert len(router.apply_calls) == 1
    assert "ip access-group LAB13_WEB_FILTER in" in router.configuration


def test_existing_acl_is_rejected_before_backup_or_deployment():
    router = FakeRouter(
        configuration=(
            "hostname R1\n"
            "ip access-list extended LAB13_WEB_FILTER\n"
            " 10 permit ip any any\n"
            "!\n"
        )
    )
    backups = FakeBackupService()

    result = ACLDeploymentWorkflow(router, backups).deploy(make_policy())

    assert not result.success
    assert result.status == "rejected"
    assert "already exists" in result.message
    assert backups.saved == []
    assert router.apply_calls == []


def test_existing_interface_acl_binding_is_rejected():
    router = FakeRouter(
        configuration=(
            "hostname R1\n"
            "interface GigabitEthernet0/0\n"
            " ip access-group EXISTING_FILTER in\n"
            "!\n"
        )
    )
    backups = FakeBackupService()

    result = ACLDeploymentWorkflow(router, backups).deploy(make_policy())

    assert not result.success
    assert result.status == "rejected"
    assert "already has an ACL" in result.message
    assert backups.saved == []
    assert router.apply_calls == []


def test_backup_failure_prevents_deployment():
    router = FakeRouter()
    backups = FakeBackupService(fail=True)

    result = ACLDeploymentWorkflow(router, backups).deploy(make_policy())

    assert not result.success
    assert result.status == "backup_failed"
    assert result.persistent_backup_id is None
    assert router.apply_calls == []


def test_contradictory_policy_is_rejected():
    policy = SecurityPolicy(
        policy_id="CONFLICT",
        device_id="R1",
        acl_name="CONFLICT_FILTER",
        interface="GigabitEthernet0/0",
        direction="in",
        rules=(
            ACLRule(
                sequence=10,
                action=ACLAction.PERMIT,
                protocol=ACLProtocol.TCP,
                source="192.0.2.1",
                destination="198.51.100.10",
                destination_port=443,
            ),
            ACLRule(
                sequence=20,
                action=ACLAction.DENY,
                protocol=ACLProtocol.TCP,
                source="192.0.2.1",
                destination="198.51.100.10",
                destination_port=443,
            ),
        ),
    )

    router = FakeRouter()
    backups = FakeBackupService()
    result = ACLDeploymentWorkflow(router, backups).deploy(policy)

    assert not result.success
    assert result.status == "rejected"
    assert "contradictory rules" in result.message
    assert router.apply_calls == []
    assert backups.saved == []


def test_precheck_failure_prevents_backup_and_deployment():
    class UnreachableRouter(FakeRouter):
        def get_running_configuration(self, device_id):
            raise RuntimeError("Simulated connection failure")

    router = UnreachableRouter()
    backups = FakeBackupService()

    result = ACLDeploymentWorkflow(router, backups).deploy(make_policy())

    assert not result.success
    assert result.status == "rejected"
    assert "Pre-deployment read failed" in result.message
    assert backups.saved == []
    assert router.apply_calls == []
