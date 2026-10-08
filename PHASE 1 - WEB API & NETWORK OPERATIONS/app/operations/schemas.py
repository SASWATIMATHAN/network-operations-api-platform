from datetime import datetime

from pydantic import BaseModel, Field

from app.operations.models import OperationType


class OperationRequest(BaseModel):
    operation: OperationType
    targets: list[str] = Field(min_length=1)
    requested_by: str = Field(default="system", min_length=1)


class DeviceOperationResponse(BaseModel):
    host: str
    status: str
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_ms: float | None = None
    output: str | None = None
    error_type: str | None = None
    error_message: str | None = None


class OperationResponse(BaseModel):
    operation_id: str
    operation: OperationType
    status: str
    requested_by: str
    targets: list[str]
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_ms: float | None = None
    total_devices: int
    successful_devices: int
    failed_devices: int
    results: list[DeviceOperationResponse]
