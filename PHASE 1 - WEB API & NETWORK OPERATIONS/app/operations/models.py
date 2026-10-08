from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class OperationType(str, Enum):
    COLLECT_HEALTH = "collect_health"
    COLLECT_INTERFACES = "collect_interfaces"
    COLLECT_ROUTES = "collect_routes"
    COLLECT_VERSION = "collect_version"


class OperationStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    COMPLETED_WITH_ERRORS = "completed_with_errors"
    FAILED = "failed"


class DeviceOperationStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class DeviceOperationResult:
    host: str
    status: DeviceOperationStatus
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_ms: float | None = None
    output: str | None = None
    error_type: str | None = None
    error_message: str | None = None


@dataclass
class OperationResult:
    operation_id: str
    operation: OperationType
    status: OperationStatus
    requested_by: str
    targets: list[str]
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_ms: float | None = None
    results: list[DeviceOperationResult] = field(default_factory=list)

    @property
    def successful_devices(self) -> int:
        return sum(
            result.status == DeviceOperationStatus.SUCCESS
            for result in self.results
        )

    @property
    def failed_devices(self) -> int:
        return sum(
            result.status in {
                DeviceOperationStatus.FAILED,
                DeviceOperationStatus.TIMEOUT,
            }
            for result in self.results
        )

    @property
    def total_devices(self) -> int:
        return len(self.targets)

    def finalize_status(self) -> None:
        if self.successful_devices == self.total_devices:
            self.status = OperationStatus.COMPLETED
        elif self.successful_devices > 0:
            self.status = OperationStatus.COMPLETED_WITH_ERRORS
        else:
            self.status = OperationStatus.FAILED
