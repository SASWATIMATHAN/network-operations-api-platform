
"""Lab 14: Integrated Network Operations Platform orchestration."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Mapping


Context = dict[str, Any]
StepHandler = Callable[[Context], Any]
RollbackHandler = Callable[[Context, Exception], Any]
AuditHandler = Callable[[dict[str, Any]], Any]


@dataclass
class IntegrationResult:
    """Outcome of one integrated network operations workflow."""

    operation_id: str
    success: bool
    completed_steps: list[str] = field(default_factory=list)
    failed_step: str | None = None
    rollback_attempted: bool = False
    rollback_success: bool | None = None
    error: str | None = None
    results: dict[str, Any] = field(default_factory=dict)
    audit_events: list[dict[str, Any]] = field(default_factory=list)


class IntegrationService:
    """Coordinate inventory, backups, deployments, verification and audit.

    Each handler receives the same mutable workflow context.
    Handlers can be connected to the existing Lab 10–13 services
    without duplicating their implementation.
    """

    STEPS = (
        "inventory",
        "backup",
        "configuration_deployment",
        "acl_deployment",
        "verification",
    )

    def __init__(
        self,
        *,
        inventory: StepHandler,
        backup: StepHandler,
        configuration_deployment: StepHandler,
        acl_deployment: StepHandler,
        verification: StepHandler,
        rollback: RollbackHandler,
        audit: AuditHandler,
    ) -> None:
        self.handlers: dict[str, StepHandler] = {
            "inventory": inventory,
            "backup": backup,
            "configuration_deployment": configuration_deployment,
            "acl_deployment": acl_deployment,
            "verification": verification,
        }
        self.rollback_handler = rollback
        self.audit_handler = audit

    def execute(
        self,
        operation_id: str,
        request: Mapping[str, Any],
    ) -> IntegrationResult:
        """Execute the workflow and return its complete outcome."""

        context: Context = {
            "operation_id": operation_id,
            "request": dict(request),
            "started_at": datetime.now(timezone.utc).isoformat(),
            "results": {},
        }

        result = IntegrationResult(
            operation_id=operation_id,
            success=False,
        )

        deployment_started = False

        for step in self.STEPS:
            try:
                if step in {
                    "configuration_deployment",
                    "acl_deployment",
                }:
                    deployment_started = True

                step_result = self.handlers[step](context)

                if step_result is False or step_result is None:
                    raise RuntimeError(
                        f"{step} reported an unsuccessful result"
                    )

                result.results[step] = step_result
                context["results"][step] = step_result
                result.completed_steps.append(step)

            except Exception as exc:
                result.failed_step = step
                result.error = f"{type(exc).__name__}: {exc}"
                context["failure"] = result.error

                if deployment_started:
                    result.rollback_attempted = True
                    try:
                        rollback_result = self.rollback_handler(
                            context, exc
                        )
                        result.rollback_success = (
                            rollback_result is not False
                        )
                        result.results["rollback"] = rollback_result
                    except Exception as rollback_exc:
                        result.rollback_success = False
                        result.results["rollback_error"] = (
                            f"{type(rollback_exc).__name__}: "
                            f"{rollback_exc}"
                        )

                break

        result.success = result.failed_step is None

        event = {
            "operation_id": operation_id,
            "event": (
                "workflow_completed"
                if result.success
                else "workflow_failed"
            ),
            "success": result.success,
            "completed_steps": list(result.completed_steps),
            "failed_step": result.failed_step,
            "rollback_attempted": result.rollback_attempted,
            "rollback_success": result.rollback_success,
            "error": result.error,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        result.audit_events.append(event)

        try:
            self.audit_handler(event)
        except Exception as audit_exc:
            result.results["audit_error"] = (
                f"{type(audit_exc).__name__}: {audit_exc}"
            )

        return result
