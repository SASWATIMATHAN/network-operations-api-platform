from sqlalchemy import select

from app.audit.models import AuditRecord
from app.database import SessionLocal
from app.models.persistence import (
    PersistentAuditRecord,
    PersistentDeviceOperationResult,
    PersistentOperation,
)
from app.operations.models import OperationResult


def _duration_ms(value: float | None) -> int | None:
    return round(value) if value is not None else None


class AuditService:
    """Persist operation results and audit records in PostgreSQL."""

    def record_operation(self, result: OperationResult) -> AuditRecord:
        record = AuditRecord(
            operation_id=result.operation_id,
            requested_by=result.requested_by,
            operation=result.operation.value,
            targets=list(result.targets),
            status=result.status.value,
            created_at=result.created_at,
            started_at=result.started_at,
            completed_at=result.completed_at,
            duration_ms=result.duration_ms,
        )

        with SessionLocal.begin() as db:
            operation_record = db.get(
                PersistentOperation, result.operation_id
            )

            if operation_record is None:
                operation_record = PersistentOperation(
                    operation_id=result.operation_id,
                    operation=result.operation.value,
                    status=result.status.value,
                    requested_by=result.requested_by,
                    targets=list(result.targets),
                    created_at=result.created_at,
                )
                db.add(operation_record)

            operation_record.operation = result.operation.value
            operation_record.status = result.status.value
            operation_record.requested_by = result.requested_by
            operation_record.targets = list(result.targets)
            operation_record.created_at = result.created_at
            operation_record.started_at = result.started_at
            operation_record.completed_at = result.completed_at
            operation_record.duration_ms = _duration_ms(
                result.duration_ms
            )
            operation_record.success_count = result.successful_devices
            operation_record.failed_count = result.failed_devices
            operation_record.total_count = result.total_devices
            operation_record.error_message = None

            # Replacing prior device results makes repeated recording
            # of the same operation idempotent.
            operation_record.device_results.clear()

            for device_result in result.results:
                operation_record.device_results.append(
                    PersistentDeviceOperationResult(
                        host=device_result.host,
                        status=device_result.status.value,
                        started_at=device_result.started_at,
                        completed_at=device_result.completed_at,
                        duration_ms=_duration_ms(
                            device_result.duration_ms
                        ),
                        output=device_result.output,
                        error_type=device_result.error_type,
                        error_message=device_result.error_message,
                    )
                )

            db.flush()

            audit_record = db.scalar(
                select(PersistentAuditRecord).where(
                    PersistentAuditRecord.operation_id
                    == result.operation_id
                )
            )

            if audit_record is None:
                audit_record = PersistentAuditRecord(
                    operation_id=result.operation_id,
                    requested_by=record.requested_by,
                    operation=record.operation,
                    targets=record.targets,
                    status=record.status,
                    created_at=record.created_at,
                )
                db.add(audit_record)

            audit_record.requested_by = record.requested_by
            audit_record.operation = record.operation
            audit_record.targets = record.targets
            audit_record.status = record.status
            audit_record.created_at = record.created_at
            audit_record.started_at = record.started_at
            audit_record.completed_at = record.completed_at
            audit_record.duration_ms = _duration_ms(
                record.duration_ms
            )

        return record

    @staticmethod
    def _to_record(row: PersistentAuditRecord) -> AuditRecord:
        return AuditRecord(
            operation_id=row.operation_id,
            requested_by=row.requested_by,
            operation=row.operation,
            targets=list(row.targets),
            status=row.status,
            created_at=row.created_at,
            started_at=row.started_at,
            completed_at=row.completed_at,
            duration_ms=row.duration_ms,
        )

    def get_record(self, operation_id: str) -> AuditRecord | None:
        with SessionLocal() as db:
            row = db.scalar(
                select(PersistentAuditRecord).where(
                    PersistentAuditRecord.operation_id == operation_id
                )
            )
            return self._to_record(row) if row is not None else None

    def list_records(self) -> list[AuditRecord]:
        with SessionLocal() as db:
            rows = db.scalars(
                select(PersistentAuditRecord).order_by(
                    PersistentAuditRecord.created_at.desc()
                )
            ).all()
            return [self._to_record(row) for row in rows]


_default_audit_service = AuditService()


def get_audit_service() -> AuditService:
    return _default_audit_service
