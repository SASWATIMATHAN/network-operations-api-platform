from fastapi import APIRouter, HTTPException

from app.audit.schemas import AuditResponse
from app.audit.service import get_audit_service


router = APIRouter(
    prefix="/audit",
    tags=["Audit"],
)


_audit_service = get_audit_service()


def build_audit_response(record) -> AuditResponse:
    return AuditResponse(
        operation_id=record.operation_id,
        requested_by=record.requested_by,
        operation=record.operation,
        targets=record.targets,
        target_count=record.target_count,
        status=record.status,
        created_at=record.created_at,
        started_at=record.started_at,
        completed_at=record.completed_at,
        duration_ms=record.duration_ms,
    )


@router.get(
    "/{operation_id}",
    response_model=AuditResponse,
)
def get_audit_record(operation_id: str) -> AuditResponse:
    record = _audit_service.get_record(operation_id)

    if record is None:
        raise HTTPException(
            status_code=404,
            detail=f"Audit record '{operation_id}' not found",
        )

    return build_audit_response(record)
