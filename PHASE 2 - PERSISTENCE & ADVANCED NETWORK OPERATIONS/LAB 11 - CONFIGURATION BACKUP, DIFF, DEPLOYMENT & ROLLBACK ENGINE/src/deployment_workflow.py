
"""Controlled configuration deployment and best-effort rollback workflow."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol

from configuration_change_engine import (
    ConfigurationSnapshot,
    create_snapshot,
    validate_configuration,
)


class DeploymentAdapter(Protocol):
    """Interface required by the deployment workflow."""

    def get_running_configuration(self, device_id: str) -> str:
        """Return the current running configuration."""
        ...

    def apply_configuration(
        self, device_id: str, configuration: str
    ) -> str:
        """Apply configuration and return the device response."""
        ...


@dataclass(frozen=True)
class DeploymentResult:
    """Outcome of a deployment attempt."""

    device_id: str
    success: bool
    status: str
    message: str
    pre_deployment_snapshot: ConfigurationSnapshot | None
    rollback_attempted: bool
    rollback_succeeded: bool | None
    validation_errors: tuple[str, ...]
    validation_warnings: tuple[str, ...]
    device_response: str


class ConfigurationDeploymentWorkflow:
    """Validate, back up, deploy, verify, and attempt rollback on failure."""

    def __init__(self, adapter: DeploymentAdapter) -> None:
        self.adapter = adapter

    def deploy(
        self,
        device_id: str,
        configuration: str,
        version: int,
        verify: Callable[[str], bool],
    ) -> DeploymentResult:
        """Deploy a configuration and roll back if deployment or verification fails."""

        validation = validate_configuration(configuration)

        if not validation.valid:
            return DeploymentResult(
                device_id=device_id,
                success=False,
                status="rejected",
                message="Configuration failed safety validation",
                pre_deployment_snapshot=None,
                rollback_attempted=False,
                rollback_succeeded=None,
                validation_errors=validation.errors,
                validation_warnings=validation.warnings,
                device_response="",
            )

        try:
            original_configuration = self.adapter.get_running_configuration(
                device_id
            )
        except Exception as exc:
            return DeploymentResult(
                device_id=device_id,
                success=False,
                status="precheck_failed",
                message=f"Could not retrieve current configuration: {exc}",
                pre_deployment_snapshot=None,
                rollback_attempted=False,
                rollback_succeeded=None,
                validation_errors=(),
                validation_warnings=validation.warnings,
                device_response="",
            )

        try:
            snapshot = create_snapshot(
                device_id=device_id,
                version=version,
                configuration=original_configuration,
            )
        except (TypeError, ValueError) as exc:
            return DeploymentResult(
                device_id=device_id,
                success=False,
                status="backup_failed",
                message=f"Could not create pre-deployment snapshot: {exc}",
                pre_deployment_snapshot=None,
                rollback_attempted=False,
                rollback_succeeded=None,
                validation_errors=(),
                validation_warnings=validation.warnings,
                device_response="",
            )

        try:
            response = self.adapter.apply_configuration(
                device_id, configuration
            )
            if not verify(device_id):
                raise RuntimeError("Post-deployment verification failed")

            return DeploymentResult(
                device_id=device_id,
                success=True,
                status="deployed",
                message="Configuration deployed and verification passed",
                pre_deployment_snapshot=snapshot,
                rollback_attempted=False,
                rollback_succeeded=None,
                validation_errors=(),
                validation_warnings=validation.warnings,
                device_response=response,
            )

        except Exception as exc:
            failure_message = str(exc)

        try:
            rollback_response = self.adapter.apply_configuration(
                device_id, original_configuration
            )
            if not verify(device_id):
                raise RuntimeError(
                    "Rollback was applied but verification failed"
                )

            return DeploymentResult(
                device_id=device_id,
                success=False,
                status="rolled_back",
                message=(
                    f"Deployment failed ({failure_message}); "
                    "original configuration was restored and verified"
                ),
                pre_deployment_snapshot=snapshot,
                rollback_attempted=True,
                rollback_succeeded=True,
                validation_errors=(),
                validation_warnings=validation.warnings,
                device_response=rollback_response,
            )

        except Exception as rollback_exc:
            return DeploymentResult(
                device_id=device_id,
                success=False,
                status="rollback_failed",
                message=(
                    f"Deployment failed ({failure_message}); "
                    f"rollback also failed ({rollback_exc})"
                ),
                pre_deployment_snapshot=snapshot,
                rollback_attempted=True,
                rollback_succeeded=False,
                validation_errors=(),
                validation_warnings=validation.warnings,
                device_response="",
            )
