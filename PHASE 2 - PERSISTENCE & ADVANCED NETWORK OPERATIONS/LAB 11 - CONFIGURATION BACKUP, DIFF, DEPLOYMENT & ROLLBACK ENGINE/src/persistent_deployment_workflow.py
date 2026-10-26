
"""Persistent pre-deployment backup integration for Lab 11."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol

from configuration_change_engine import (
    ConfigurationSnapshot,
    create_snapshot,
    validate_configuration,
)
from deployment_workflow import DeploymentAdapter, DeploymentResult


class PersistentBackupService(Protocol):
    """Interface implemented by the Lab 10 backup service."""

    def save_backup(
        self,
        device_id: str,
        configuration: str,
        requested_by: str,
    ) -> object:
        """Persist the original configuration before deployment."""
        ...


@dataclass(frozen=True)
class PersistentDeploymentResult:
    """Deployment outcome including persistent backup information."""

    deployment: DeploymentResult
    persistent_backup_id: str | None


class PersistentConfigurationDeploymentWorkflow:
    """Persist the original configuration before invoking deployment."""

    def __init__(
        self,
        adapter: DeploymentAdapter,
        backup_service: PersistentBackupService,
        requested_by: str = "lab11-deployment",
    ) -> None:
        if not requested_by.strip():
            raise ValueError("requested_by must not be empty")

        self.adapter = adapter
        self.backup_service = backup_service
        self.requested_by = requested_by

    def deploy(
        self,
        device_id: str,
        configuration: str,
        version: int,
        verify: Callable[[str], bool],
    ) -> PersistentDeploymentResult:
        """Back up the current configuration before changing the device."""

        validation = validate_configuration(configuration)

        if not validation.valid:
            return PersistentDeploymentResult(
                deployment=DeploymentResult(
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
                ),
                persistent_backup_id=None,
            )

        try:
            original_configuration = self.adapter.get_running_configuration(
                device_id
            )
        except Exception as exc:
            return self._failure(
                device_id=device_id,
                status="precheck_failed",
                message=f"Could not retrieve current configuration: {exc}",
                warnings=validation.warnings,
            )

        try:
            snapshot = create_snapshot(
                device_id=device_id,
                version=version,
                configuration=original_configuration,
            )
        except (TypeError, ValueError) as exc:
            return self._failure(
                device_id=device_id,
                status="backup_failed",
                message=f"Could not create pre-deployment snapshot: {exc}",
                warnings=validation.warnings,
            )

        try:
            backup = self.backup_service.save_backup(
                device_id=device_id,
                configuration=original_configuration,
                requested_by=self.requested_by,
            )
            backup_id = getattr(backup, "backup_id", None)

            if not backup_id:
                raise RuntimeError("Backup service returned no backup_id")

        except Exception as exc:
            return PersistentDeploymentResult(
                deployment=DeploymentResult(
                    device_id=device_id,
                    success=False,
                    status="backup_failed",
                    message=(
                        "Persistent backup failed; deployment was not "
                        f"attempted: {exc}"
                    ),
                    pre_deployment_snapshot=snapshot,
                    rollback_attempted=False,
                    rollback_succeeded=None,
                    validation_errors=(),
                    validation_warnings=validation.warnings,
                    device_response="",
                ),
                persistent_backup_id=None,
            )

        # Import locally to avoid changing the existing workflow or its tests.
        from deployment_workflow import ConfigurationDeploymentWorkflow

        workflow = ConfigurationDeploymentWorkflow(self.adapter)

        result = workflow.deploy(
            device_id=device_id,
            configuration=configuration,
            version=version,
            verify=verify,
        )

        return PersistentDeploymentResult(
            deployment=result,
            persistent_backup_id=backup_id,
        )

    @staticmethod
    def _failure(
        device_id: str,
        status: str,
        message: str,
        warnings: tuple[str, ...],
    ) -> PersistentDeploymentResult:
        return PersistentDeploymentResult(
            deployment=DeploymentResult(
                device_id=device_id,
                success=False,
                status=status,
                message=message,
                pre_deployment_snapshot=None,
                rollback_attempted=False,
                rollback_succeeded=None,
                validation_errors=(),
                validation_warnings=warnings,
                device_response="",
            ),
            persistent_backup_id=None,
        )
