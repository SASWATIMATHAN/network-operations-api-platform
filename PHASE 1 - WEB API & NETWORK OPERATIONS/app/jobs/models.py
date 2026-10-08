from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from threading import Lock


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    COMPLETED_WITH_ERRORS = "completed_with_errors"
    FAILED = "failed"


@dataclass
class Job:
    job_id: str
    operation_id: str
    status: JobStatus = JobStatus.QUEUED
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    started_at: datetime | None = None
    completed_at: datetime | None = None
    operation_result: object | None = None
    error_message: str | None = None


class JobStore:
    """Thread-safe in-memory store for asynchronous jobs."""

    def __init__(self):
        self._jobs: dict[str, Job] = {}
        self._lock = Lock()

    def create(self, job: Job) -> None:
        with self._lock:
            self._jobs[job.job_id] = job

    def get(self, job_id: str) -> Job | None:
        with self._lock:
            return self._jobs.get(job_id)

    def update(self, job: Job) -> None:
        with self._lock:
            self._jobs[job.job_id] = job
