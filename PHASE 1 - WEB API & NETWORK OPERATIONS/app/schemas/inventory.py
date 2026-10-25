from datetime import datetime

from ipaddress import IPv4Address, IPv6Address
from pydantic import BaseModel, ConfigDict, Field


class DeviceCreate(BaseModel):
    device_id: str = Field(min_length=2, max_length=30)
    hostname: str = Field(min_length=1, max_length=30)
    device_type: str = Field(min_length=1, max_length=20)
    management_ip: IPv4Address | IPv6Address
    status: str = Field(min_length=1, max_length=30)
    description: str | None = Field(default=None, max_length=500)


class DeviceUpdate(BaseModel):
    hostname: str = Field(min_length=1, max_length=30)
    device_type: str = Field(min_length=1, max_length=20)
    management_ip: IPv4Address | IPv6Address
    status: str = Field(min_length=1, max_length=30)
    description: str | None = Field(default=None, max_length=500)


class DeviceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    device_id: str
    hostname: str
    device_type: str
    management_ip: str
    status: str
    description: str | None
    created_at: datetime
    updated_at: datetime


class InterfaceCreate(BaseModel):
    interface_name: str = Field(min_length=1, max_length=80)
    ip_address: IPv4Address | IPv6Address
    subnet_mask: str = Field(min_length=1, max_length=45)
    status: str = Field(min_length=1, max_length=30)
    description: str = Field(default="", max_length=255)


class InterfaceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    device_id: str
    interface_name: str
    ip_address: str
    subnet_mask: str
    status: str
    description: str
