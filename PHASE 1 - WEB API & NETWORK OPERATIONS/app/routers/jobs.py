from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_network_service
from app.jobs.manager import JobManager
from app.jobs.schemas import (
    JobDeviceResult,
    JobOperationResult,
    JobRequest,
    JobResponse,
)
from app.operations.models import OperationResult
from app.services.network_service import NetworkService


router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"],
)


_job_manager: JobManager | None = None


def get_job_manager(
    network_service: NetworkService = Depends(get_network_service),
) -> JobManager:
    global _job_manager

    if _job_manager is None:
        _job_manager = JobManager(network_service)

    return _job_manager


def build_job_response(job) -> JobResponse:
    result = job.operation_result

    operation_result = None

    if isinstance(result, OperationResult):
        operation_result = JobOperationResult(
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
                JobDeviceResult(
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

    return JobResponse(
        job_id=job.job_id,
        operation_id=job.operation_id,
        status=job.status.value,
        created_at=job.created_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
        error_message=job.error_message,
        result=operation_result,
    )


@router.post(
    "",
    response_model=JobResponse,
    status_code=202,
)
def submit_job(
    request: JobRequest,
    manager: JobManager = Depends(get_job_manager),
) -> JobResponse:
    job = manager.submit(
        operation=request.operation,
        targets=request.targets,
        requested_by=request.requested_by,
    )

    return build_job_response(job)


@router.get(
    "/{job_id}",
    response_model=JobResponse,
)
def get_job(
    job_id: str,
    manager: JobManager = Depends(get_job_manager),
) -> JobResponse:
    job = manager.get_job(job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail=f"Job '{job_id}' not found",
        )

    return build_job_response(job)
