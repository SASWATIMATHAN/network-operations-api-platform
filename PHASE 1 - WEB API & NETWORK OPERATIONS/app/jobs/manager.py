from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from threading import Lock
from uuid import uuid4

from sqlalchemy import select

from app.database import SessionLocal
from app.jobs.models import Job, JobStatus, JobStore
from app.models.persistence import (
    PersistentDeviceOperationResult,
    PersistentJob,
    PersistentOperation,
)
from app.operations.models import (
    DeviceOperationResult,
    DeviceOperationStatus,
    OperationResult,
    OperationStatus,
    OperationType,
)
from app.operations.service import OperationService
from app.services.network_service import NetworkService


class JobManager:
    """Manage asynchronous network jobs with PostgreSQL persistence."""

    def __init__(self, network_service: NetworkService, max_workers: int = 3):
        self.job_store = JobStore()
        self.operation_service = OperationService(
            network_service=network_service,
            max_workers=max_workers,
        )
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._lock = Lock()



    def submit(
        self,
        operation: OperationType,
        targets: list[str],
        requested_by: str,
    ) -> Job:
        job_id = str(uuid4())
        operation_id = str(uuid4())
        job = Job(
            job_id=job_id,
            operation_id=operation_id,
        )

        now = datetime.now(timezone.utc)
        target_list = list(targets)

        with SessionLocal.begin() as db:
            db.add(
                PersistentOperation(
                    operation_id=operation_id,
                    operation=operation.value,
                    status=OperationStatus.QUEUED.value,
                    requested_by=requested_by,
                    targets=target_list,
                    created_at=now,
                    success_count=0,
                    failed_count=0,
                    total_count=len(target_list),
                )
            )
            db.add(
                PersistentJob(
                    job_id=job_id,
                    operation_id=operation_id,
                    status=job.status.value,
                    created_at=job.created_at,
                )
            )

        self.job_store.create(job)

        try:
            self.executor.submit(
                self._run_job,
                job,
                operation,
                target_list,
                requested_by,
            )
        except Exception as exc:
            job.status = JobStatus.FAILED
            job.error_message = str(exc)
            job.completed_at = datetime.now(timezone.utc)
            self.job_store.update(job)
            self._persist_job(job)

            with SessionLocal.begin() as db:
                operation_row = db.get(PersistentOperation, operation_id)
                if operation_row is not None:
                    operation_row.status = OperationStatus.FAILED.value
                    operation_row.completed_at = job.completed_at
                    operation_row.error_message = str(exc)

            raise

        return job



    def get_job(self, job_id: str) -> Job | None:
        cached = self.job_store.get(job_id)
        if cached is not None:
            return cached

        with SessionLocal() as db:
            row = db.scalar(
                select(PersistentJob).where(
                    PersistentJob.job_id == job_id
                )
            )
            if row is None:
                return None

            job = Job(
                job_id=row.job_id,
                operation_id=row.operation_id or "",
                status=JobStatus(row.status),
                created_at=row.created_at,
                started_at=row.started_at,
                completed_at=row.completed_at,
                error_message=row.error_message,
            )

            if row.operation_record is not None:
                operation = row.operation_record
                job.operation_id = operation.operation_id
                job.operation_result = OperationResult(
                    operation_id=operation.operation_id,
                    operation=OperationType(operation.operation),
                    status=OperationStatus(operation.status),
                    requested_by=operation.requested_by,
                    targets=list(operation.targets),
                    created_at=operation.created_at,
                    started_at=operation.started_at,
                    completed_at=operation.completed_at,
                    duration_ms=operation.duration_ms,
                    results=[
                        DeviceOperationResult(
                            host=device.host,
                            status=DeviceOperationStatus(device.status),
                            started_at=device.started_at,
                            completed_at=device.completed_at,
                            duration_ms=device.duration_ms,
                            output=device.output,
                            error_type=device.error_type,
                            error_message=device.error_message,
                        )
                        for device in operation.device_results
                    ],
                )

        self.job_store.create(job)
        return job

    def _persist_job(self, job: Job) -> None:
        with SessionLocal.begin() as db:
            row = db.get(PersistentJob, job.job_id)

            if row is None:
                row = PersistentJob(
                    job_id=job.job_id,
                    status=job.status.value,
                    created_at=job.created_at,
                )
                db.add(row)

            row.operation_id = job.operation_id or None
            row.status = job.status.value
            row.created_at = job.created_at
            row.started_at = job.started_at
            row.completed_at = job.completed_at
            row.error_message = job.error_message

    def _run_job(
        self,
        job: Job,
        operation: OperationType,
        targets: list[str],
        requested_by: str,
    ) -> None:
        job.status = JobStatus.RUNNING
        job.started_at = datetime.now(timezone.utc)
        self.job_store.update(job)
        self._persist_job(job)

        try:
            result = self.operation_service.execute(
                operation=operation,
                targets=targets,
                requested_by=requested_by,
                operation_id=job.operation_id,
            )

            job.operation_result = result

            if result.status == OperationStatus.COMPLETED:
                job.status = JobStatus.COMPLETED
            elif result.status == OperationStatus.COMPLETED_WITH_ERRORS:
                job.status = JobStatus.COMPLETED_WITH_ERRORS
            else:
                job.status = JobStatus.FAILED

        except Exception as exc:
            job.status = JobStatus.FAILED
            job.error_message = str(exc)

        finally:
            job.completed_at = datetime.now(timezone.utc)
            self.job_store.update(job)
            self._persist_job(job)
