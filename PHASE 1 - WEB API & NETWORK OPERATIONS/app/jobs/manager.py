from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from uuid import uuid4

from app.jobs.models import Job, JobStatus, JobStore
from app.operations.models import OperationType
from app.operations.service import OperationService
from app.services.network_service import NetworkService


class JobManager:
    """Manage asynchronous network operation jobs."""

    def __init__(self, network_service: NetworkService, max_workers: int = 3):
        self.job_store = JobStore()
        self.operation_service = OperationService(
            network_service=network_service,
            max_workers=max_workers,
        )
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def submit(
        self,
        operation: OperationType,
        targets: list[str],
        requested_by: str,
    ) -> Job:
        job = Job(
            job_id=str(uuid4()),
            operation_id=str(uuid4()),
        )

        self.job_store.create(job)

        self.executor.submit(
            self._run_job,
            job,
            operation,
            targets,
            requested_by,
        )

        return job

    def get_job(self, job_id: str) -> Job | None:
        return self.job_store.get(job_id)

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

        try:
            result = self.operation_service.execute(
                operation=operation,
                targets=targets,
                requested_by=requested_by,
                operation_id=job.operation_id,
            )

            job.operation_result = result

            if result.status.value == "completed":
                job.status = JobStatus.COMPLETED
            elif result.status.value == "completed_with_errors":
                job.status = JobStatus.COMPLETED_WITH_ERRORS
            else:
                job.status = JobStatus.FAILED

        except Exception as exc:
            job.status = JobStatus.FAILED
            job.error_message = str(exc)

        finally:
            job.completed_at = datetime.now(timezone.utc)
            self.job_store.update(job)
