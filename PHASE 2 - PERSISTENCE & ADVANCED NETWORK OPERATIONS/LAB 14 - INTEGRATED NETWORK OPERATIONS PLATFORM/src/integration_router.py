
"""Lab 14 API routes; dry-run only until real adapters are connected."""

from dataclasses import asdict
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from integration_service import IntegrationService
from fastapi import Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.network_inventory import NetworkDevice
router = APIRouter(
    prefix="/integration",
    tags=["Integrated Network Operations"],
)


class DryRunRequest(BaseModel):
    operation_id: str = Field(min_length=3, max_length=100)
    device_id: str = Field(min_length=2, max_length=100)
    requested_configuration: str = Field(min_length=1)
    actor: str = Field(min_length=2, max_length=100)
    dry_run: bool = True


@router.post("/dry-run")
def run_dry_run(request: DryRunRequest) -> dict[str, Any]:
    """Simulate the complete workflow without contacting network devices."""

    if not request.dry_run:
        raise HTTPException(
            status_code=400,
            detail="Live changes are not enabled in the Lab 14 dry-run endpoint.",
        )

    simulated_steps: list[str] = []
    audit_events: list[dict[str, Any]] = []

    def simulate(step: str):
        def handler(context: dict[str, Any]) -> dict[str, Any]:
            simulated_steps.append(step)
            return {
                "status": "simulated",
                "step": step,
                "device_id": context["request"]["device_id"],
            }

        return handler

    service = IntegrationService(
        inventory=simulate("inventory"),
        backup=simulate("backup"),
        configuration_deployment=simulate("configuration_deployment"),
        acl_deployment=simulate("acl_deployment"),
        verification=simulate("verification"),
        rollback=lambda context, error: {
            "status": "not_required_in_successful_dry_run"
        },
        audit=lambda event: audit_events.append(event),
    )

    result = service.execute(
        request.operation_id,
        {
            "device_id": request.device_id,
            "requested_configuration": request.requested_configuration,
            "actor": request.actor,
            "dry_run": True,
        },
    )

    response = asdict(result)
    response["mode"] = "dry_run"
    response["simulated_steps"] = simulated_steps
    return response
@router.get("/inventory-check/{device_id}")
def check_persistent_inventory(
    device_id: str,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Validate a device against the persistent Lab 10 inventory."""

    try:
        device = db.get(NetworkDevice, device_id)
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=503,
            detail="Persistent inventory is unavailable.",
        ) from exc

    if device is None:
        raise HTTPException(
            status_code=404,
            detail=f"Device '{device_id}' was not found in persistent inventory.",
        )

    return {
        "device_id": device.device_id,
        "hostname": device.hostname,
        "device_type": device.device_type,
        "management_ip": device.management_ip,
        "status": device.status,
        "inventory_source": "postgresql",
        "validated": True,
    }
