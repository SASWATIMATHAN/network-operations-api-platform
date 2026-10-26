
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from app.audit.service import AuditService
from app.models.persistence import (
    PersistentAuditRecord,
    PersistentDeviceOperationResult,
    PersistentOperation,
)


def make_result():
    """Build a representative completed operation result."""
    from app.operations.models import (
        DeviceOperationResult,
        DeviceOperationStatus,
        OperationResult,
        OperationStatus,
        OperationType,
    )

    now = datetime.now(timezone.utc)
    device_result = DeviceOperationResult(
        host="R1",
        status=DeviceOperationStatus.SUCCESS,
        started_at=now,
        completed_at=now,
        duration_ms=125.4,
        output={"hostname": "R1", "status": "reachable"},
        error_type=None,
        error_message=None,
    )

    return OperationResult(
        operation_id="lab10-audit-test-001",
        operation=next(iter(OperationType)),
        status=OperationStatus.COMPLETED,
        requested_by="lab10-test",
        targets=["R1"],
        created_at=now,
        started_at=now,
        completed_at=now,
        duration_ms=130.6,
        results=[device_result],
    )


def test_record_operation_persists_operation_device_result_and_audit():
    result = make_result()
    service = AuditService()

    with patch("app.audit.service.SessionLocal.begin") as begin:
        session = begin.return_value.__enter__.return_value
        session.get.return_value = None
        session.scalar.return_value = None

        record = service.record_operation(result)

    added = [call.args[0] for call in session.add.call_args_list]

    operation_rows = [
        row for row in added if isinstance(row, PersistentOperation)
    ]
    audit_rows = [
        row for row in added if isinstance(row, PersistentAuditRecord)
    ]

    assert record.operation_id == result.operation_id
    assert record.requested_by == result.requested_by

    assert len(operation_rows) == 1
    operation_row = operation_rows[0]
    assert operation_row.operation_id == result.operation_id
    assert operation_row.targets == ["R1"]
    assert operation_row.total_count == 1
    assert operation_row.success_count == 1
    assert operation_row.failed_count == 0

    assert len(operation_row.device_results) == 1
    device_row = operation_row.device_results[0]
    assert isinstance(device_row, PersistentDeviceOperationResult)
    assert device_row.host == "R1"
    assert device_row.output == {
        "hostname": "R1",
        "status": "reachable",
    }

    assert len(audit_rows) == 1
    assert audit_rows[0].operation_id == result.operation_id
    assert audit_rows[0].requested_by == "lab10-test"

    session.flush.assert_called_once()


def test_get_record_returns_none_when_operation_is_not_audited():
    service = AuditService()

    with patch("app.audit.service.SessionLocal") as session_factory:
        session = session_factory.return_value.__enter__.return_value
        session.scalar.return_value = None

        record = service.get_record("missing-operation")

    assert record is None


def test_list_records_returns_empty_list_when_audit_table_is_empty():
    service = AuditService()

    with patch("app.audit.service.SessionLocal") as session_factory:
        session = session_factory.return_value.__enter__.return_value
        session.scalars.return_value.all.return_value = []

        records = service.list_records()

    assert records == []
