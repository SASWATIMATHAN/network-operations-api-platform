
"""Guarded ACL deployment using Lab 11's persistent workflow."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

# Load Lab 11 modules without copying or modifying their implementation.
_LAB11_SRC = (
    Path(__file__).resolve().parents[2]
    / "LAB 11 - CONFIGURATION BACKUP, DIFF, DEPLOYMENT & ROLLBACK ENGINE"
    / "src"
)
if str(_LAB11_SRC) not in sys.path:
    sys.path.insert(0, str(_LAB11_SRC))

from configuration_change_engine import validate_configuration
from persistent_deployment_workflow import (
    PersistentConfigurationDeploymentWorkflow,
)

from ios_acl_generator import generate_ios_acl
from security_policy import SecurityPolicy, find_rule_conflicts


@dataclass(frozen=True)
class ACLDeploymentResult:
    """Structured outcome of an ACL deployment attempt."""

    device_id: str
    policy_id: str
    success: bool
    status: str
    message: str
    generated_commands: tuple[str, ...]
    persistent_backup_id: str | None
    rollback_attempted: bool
    rollback_succeeded: bool | None
    validation_errors: tuple[str, ...]
    warnings: tuple[str, ...]


def _has_acl_name(configuration: str, acl_name: str) -> bool:
    """Return whether the named extended ACL already exists."""
    target = f"ip access-list extended {acl_name}".casefold()
    return any(line.strip().casefold() == target for line in configuration.splitlines())


def _interface_has_acl(
    configuration: str,
    interface: str,
    direction: str,
) -> bool:
    """Check whether an interface already has an ACL in this direction."""
    current_interface = False

    for raw_line in configuration.splitlines():
        line = raw_line.strip()

        if line.startswith("interface "):
            current_interface = line[10:].strip() == interface
            continue

        if not line or line == "!":
            current_interface = False
            continue

        if current_interface and line.startswith("ip access-group "):
            parts = line.split()
            if len(parts) == 4 and parts[3].lower() == direction:
                return True

    return False


def _acl_state(
    configuration: str,
    acl_name: str,
    interface: str,
    direction: str,
) -> tuple[tuple[str, ...], bool]:
    """Extract the ACL entries and attachment state from a configuration."""
    acl_entries: list[str] = []
    inside_acl = False
    current_interface = False
    attached = False
    acl_header = f"ip access-list extended {acl_name}".casefold()

    for raw_line in configuration.splitlines():
        line = raw_line.strip()

        if not line or line == "!":
            inside_acl = False
            current_interface = False
            continue

        if line.casefold() == acl_header:
            inside_acl = True
            current_interface = False
            continue

        if line.startswith("interface "):
            inside_acl = False
            current_interface = line[10:].strip() == interface
            continue

        if line.startswith("ip access-list "):
            inside_acl = False
            current_interface = False
            continue

        if inside_acl:
            # IOS may display ACL sequence numbers. Ignore them when
            # comparing the actual rule content.
            words = line.split()
            if words and words[0].isdigit():
                line = " ".join(words[1:])
            acl_entries.append(line)

        if current_interface and line.startswith("ip access-group "):
            parts = line.split()
            if (
                len(parts) == 4
                and parts[1] == acl_name
                and parts[3].lower() == direction
            ):
                attached = True

    return tuple(acl_entries), attached


class _TrackingAdapter:
    """Track the original and last-applied configuration for verification."""

    def __init__(self, adapter):
        self.adapter = adapter
        self.original_configuration: str | None = None
        self.last_applied_configuration: str | None = None

    def get_running_configuration(self, device_id: str) -> str:
        configuration = self.adapter.get_running_configuration(device_id)
        if self.original_configuration is None:
            self.original_configuration = configuration
        return configuration

    def apply_configuration(self, device_id: str, configuration: str) -> str:
        response = self.adapter.apply_configuration(device_id, configuration)
        self.last_applied_configuration = configuration
        return response


class ACLDeploymentWorkflow:
    """Validate, back up, deploy, verify and roll back an ACL policy."""

    def __init__(
        self,
        adapter,
        backup_service,
        requested_by: str = "lab13-acl-deployment",
    ) -> None:
        self.adapter = adapter
        self.backup_service = backup_service
        self.requested_by = requested_by

    def deploy(
        self,
        policy: SecurityPolicy,
        version: int = 1,
    ) -> ACLDeploymentResult:
        commands = tuple(generate_ios_acl(policy))

        def rejected(message: str, errors: tuple[str, ...] = ()):
            return ACLDeploymentResult(
                device_id=policy.device_id,
                policy_id=policy.policy_id,
                success=False,
                status="rejected",
                message=message,
                generated_commands=commands,
                persistent_backup_id=None,
                rollback_attempted=False,
                rollback_succeeded=None,
                validation_errors=errors,
                warnings=(),
            )

        conflicts = find_rule_conflicts(policy)
        if conflicts:
            return rejected(
                "Policy rejected because contradictory rules were detected",
                tuple(conflicts),
            )

        configuration = "\n".join(commands)
        validation = validate_configuration(configuration)
        if not validation.valid:
            return rejected(
                "Generated ACL failed configuration safety validation",
                validation.errors,
            )

        tracked = _TrackingAdapter(self.adapter)

        # Read-only pre-check before the persistent workflow can deploy.
        try:
            original = tracked.get_running_configuration(policy.device_id)
        except Exception as exc:
            return rejected(f"Pre-deployment read failed: {exc}")

        if _has_acl_name(original, policy.acl_name):
            return rejected(
                f"ACL {policy.acl_name!r} already exists; replacement is "
                "disabled in this version"
            )

        if _interface_has_acl(
            original,
            policy.interface,
            policy.direction,
        ):
            return rejected(
                f"Interface {policy.interface!r} already has an ACL in the "
                f"{policy.direction!r} direction"
            )

        expected_state = _acl_state(
            configuration,
            policy.acl_name,
            policy.interface,
            policy.direction,
        )
        original_state = _acl_state(
            original,
            policy.acl_name,
            policy.interface,
            policy.direction,
        )

        def verify(device_id: str) -> bool:
            current = tracked.get_running_configuration(device_id)

            if tracked.last_applied_configuration == configuration:
                return _acl_state(
                    current,
                    policy.acl_name,
                    policy.interface,
                    policy.direction,
                ) == expected_state

            # During rollback, verify restoration of the original ACL state.
            return _acl_state(
                current,
                policy.acl_name,
                policy.interface,
                policy.direction,
            ) == original_state

        workflow = PersistentConfigurationDeploymentWorkflow(
            adapter=tracked,
            backup_service=self.backup_service,
            requested_by=self.requested_by,
        )

        result = workflow.deploy(
            device_id=policy.device_id,
            configuration=configuration,
            version=version,
            verify=verify,
        )

        deployment = result.deployment
        warnings = list(validation.warnings)

        if not any(
            rule.action.value == "permit"
            and rule.source == "0.0.0.0/0"
            and rule.destination == "0.0.0.0/0"
            and rule.protocol.value == "ip"
            for rule in policy.rules
        ):
            warnings.append(
                "Review the implicit-deny behavior: traffic not matched "
                "by a permit rule will be denied."
            )

        return ACLDeploymentResult(
            device_id=policy.device_id,
            policy_id=policy.policy_id,
            success=deployment.success,
            status=deployment.status,
            message=deployment.message,
            generated_commands=commands,
            persistent_backup_id=result.persistent_backup_id,
            rollback_attempted=deployment.rollback_attempted,
            rollback_succeeded=deployment.rollback_succeeded,
            validation_errors=deployment.validation_errors,
            warnings=tuple(warnings),
        )
