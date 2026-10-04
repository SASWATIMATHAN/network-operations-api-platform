from pydantic import BaseModel, Field


class DeviceHealthResponse(BaseModel):
    """API response for live device health."""

    host: str = Field(description="Device management IP address")
    reachable: bool = Field(description="Whether the device was reachable")
    raw_output: str = Field(description="Raw output returned by the network device")
