from datetime import datetime

from pydantic import BaseModel


class AuditResponse(BaseModel):
    operation_id: str
    requested_by: str
    operation: str
    targets: list[str]
    target_count: int
    status: str
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_ms: float | None = None
