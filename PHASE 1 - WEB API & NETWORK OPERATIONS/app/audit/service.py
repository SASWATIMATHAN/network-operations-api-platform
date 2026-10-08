from app.audit.models import AuditRecord, AuditStore
from app.operations.models import OperationResult


class AuditService:
    """Create and retrieve audit records for network operations."""

    def __init__(self, store: AuditStore | None = None):
        self.store = store or AuditStore()

    def record_operation(self, result: OperationResult) -> AuditRecord:
        record = AuditRecord(
            operation_id=result.operation_id,
            requested_by=result.requested_by,
            operation=result.operation.value,
            targets=result.targets,
            status=result.status.value,
            created_at=result.created_at,
            started_at=result.started_at,
            completed_at=result.completed_at,
            duration_ms=result.duration_ms,
        )

        self.store.add(record)
        return record

    def get_record(self, operation_id: str) -> AuditRecord | None:
        return self.store.get(operation_id)

    def list_records(self) -> list[AuditRecord]:
        return self.store.list_all()

_default_audit_service = AuditService()


def get_audit_service() -> AuditService:
    return _default_audit_service
