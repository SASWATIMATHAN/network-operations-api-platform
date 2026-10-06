from pydantic import BaseModel, Field


class NetworkResult(BaseModel):
    """Structured result of a network operation."""

    success: bool = Field(
        description="Whether the network operation completed successfully"
    )
    host: str = Field(
        description="Target network device address"
    )
    operation: str = Field(
        description="Network operation that was executed"
    )
    output: str | None = Field(
        default=None,
        description="Output returned by the network device"
    )
    duration_ms: float | None = Field(
        default=None,
        description="Operation duration in milliseconds"
    )
    error_type: str | None = Field(
        default=None,
        description="Classification of the network error"
    )
    error_message: str | None = Field(
        default=None,
        description="Human-readable error description"
    )
