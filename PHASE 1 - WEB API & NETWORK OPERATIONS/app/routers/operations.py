from fastapi import APIRouter, Depends

from app.dependencies import get_network_service
from app.operations.schemas import (
    DeviceOperationResponse,
    OperationRequest,
    OperationResponse,
)
from app.operations.service import OperationService
from app.services.network_service import NetworkService


router = APIRouter(
    prefix="/operations",
    tags=["Operations"],
)


def get_operation_service(
    network_service: NetworkService = Depends(get_network_service),
) -> OperationService:
    return OperationService(network_service)


@router.post(
    "",
    response_model=OperationResponse,
)
def execute_operation(
    request: OperationRequest,
    service: OperationService = Depends(get_operation_service),
) -> OperationResponse:
    result = service.execute(
        operation=request.operation,
        targets=request.targets,
        requested_by=request.requested_by,
    )

    return OperationResponse(
        operation_id=result.operation_id,
        operation=result.operation,
        status=result.status.value,
        requested_by=result.requested_by,
        targets=result.targets,
        created_at=result.created_at,
        started_at=result.started_at,
        completed_at=result.completed_at,
        duration_ms=result.duration_ms,
        total_devices=result.total_devices,
        successful_devices=result.successful_devices,
        failed_devices=result.failed_devices,
        results=[
            DeviceOperationResponse(
                host=device_result.host,
                status=device_result.status.value,
                started_at=device_result.started_at,
                completed_at=device_result.completed_at,
                duration_ms=device_result.duration_ms,
                output=device_result.output,
                error_type=device_result.error_type,
                error_message=device_result.error_message,
            )
            for device_result in result.results
        ],
    )
