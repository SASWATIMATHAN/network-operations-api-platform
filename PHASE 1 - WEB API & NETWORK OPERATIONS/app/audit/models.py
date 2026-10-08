from dataclasses import dataclass
from datetime import datetime, timezone
from threading import Lock


@dataclass
class AuditRecord:
    operation_id: str
    requested_by: str
    operation: str
    targets: list[str]
    status: str
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    duration_ms: float | None

    @property
    def target_count(self) -> int:
        return len(self.targets)


class AuditStore:
    """Thread-safe in-memory audit record store."""

    def __init__(self):
        self._records: dict[str, AuditRecord] = {}
        self._lock = Lock()

    def add(self, record: AuditRecord) -> None:
        with self._lock:
            self._records[record.operation_id] = record

    def get(self, operation_id: str) -> AuditRecord | None:
        with self._lock:
            return self._records.get(operation_id)

    def list_all(self) -> list[AuditRecord]:
        with self._lock:
            return list(self._records.values())
