from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field


app = FastAPI(
    title="Network Operations API",
    description="REST API for network operations and device management",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "System",
            "description": "System and API status operations"
        },
        {
            "name": "Devices",
            "description": "Network device information and filtering"
        }
    ]
)


class DeviceResponse(BaseModel):
    device_id: str = Field(description="Unique device identifier")
    hostname: str = Field(description="Network device hostname")
    device_type: str = Field(description="Type of network device")
    management_ip: str = Field(description="Management IPv4 address")
    status: str = Field(description="Current operational status")

class InterfaceResponse(BaseModel):
    interface_name: str = Field(
        description="Network interface name"
    )
    ip_address: str = Field(
        description="Interface IPv4 address"
    )
    subnet_mask: str = Field(
        description="Interface subnet mask"
    )
    status: str = Field(
        description="Interface operational status"
    )
    description: str = Field(
        description="Interface description"
    )

devices = [
    {
        "device_id": "R1",
        "hostname": "CORE-R1",
        "device_type": "router",
        "management_ip": "192.168.40.10",
        "status": "active"
    },
    {
        "device_id": "R2",
        "hostname": "CORE-R2",
        "device_type": "router",
        "management_ip": "192.168.40.11",
        "status": "active"
    },
    {
        "device_id": "R3",
        "hostname": "CORE-R3",
        "device_type": "router",
        "management_ip": "192.168.40.12",
        "status": "inactive"
    },
    {
        "device_id": "SW1",
        "hostname": "ACCESS-SW1",
        "device_type": "switch",
        "management_ip": "192.168.40.20",
        "status": "active"
    }
]

interfaces = {
    "R1": [
        {
            "interface_name": "FastEthernet0/0",
            "ip_address": "192.168.40.10",
            "subnet_mask": "255.255.255.0",
            "status": "up",
            "description": "Management interface"
        },
        {
            "interface_name": "FastEthernet0/1",
            "ip_address": "10.10.10.1",
            "subnet_mask": "255.255.255.252",
            "status": "up",
            "description": "WAN link to R2"
        }
    ],
    "R2": [
        {
            "interface_name": "FastEthernet0/0",
            "ip_address": "192.168.40.11",
            "subnet_mask": "255.255.255.0",
            "status": "up",
            "description": "Management interface"
        },
        {
            "interface_name": "FastEthernet0/1",
            "ip_address": "10.10.10.2",
            "subnet_mask": "255.255.255.252",
            "status": "up",
            "description": "WAN link to R1"
        }
    ],
    "R3": [
        {
            "interface_name": "FastEthernet0/0",
            "ip_address": "192.168.40.12",
            "subnet_mask": "255.255.255.0",
            "status": "down",
            "description": "Management interface"
        }
    ],
    "SW1": [
        {
            "interface_name": "FastEthernet0/1",
            "ip_address": "192.168.40.20",
            "subnet_mask": "255.255.255.0",
            "status": "up",
            "description": "Management interface"
        }
    ]
}
@app.get(
    "/",
    tags=["System"],
    summary="API root"
)
def root():
    return {
        "message": "Network Operations API is running"
    }


@app.get(
    "/health",
    tags=["System"],
    summary="API health check"
)
def health_check():
    return {
        "status": "healthy"
    }


@app.get(
    "/devices/{device_id}",
    response_model=DeviceResponse,
    tags=["Devices"],
    summary="Get network device information"
)
def get_device(device_id: str):
    for device in devices:
        if device["device_id"].lower() == device_id.lower():
            return device

    raise HTTPException(
        status_code=404,
        detail=f"Device '{device_id}' not found"
    )


@app.get(
    "/devices",
    response_model=list[DeviceResponse],
    tags=["Devices"],
    summary="List and filter network devices"
)
def list_devices(
    device_type: str | None = Query(
        default=None,
        description="Filter by device type, e.g. router or switch"
    ),
    status: str | None = Query(
        default=None,
        description="Filter by operational status, e.g. active or inactive"
    )
):
    filtered_devices = devices

    if device_type:
        filtered_devices = [
            device
            for device in filtered_devices
            if device["device_type"].lower() == device_type.lower()
        ]

    if status:
        filtered_devices = [
            device
            for device in filtered_devices
            if device["status"].lower() == status.lower()
        ]

    return filtered_devices
@app.get(
    "/devices/{device_id}/interfaces",
    response_model=list[InterfaceResponse],
    tags=["Devices"],
    summary="Get network device interfaces"
)
def get_device_interfaces(device_id: str):
    device_exists = any(
        device["device_id"].lower() == device_id.lower()
        for device in devices
    )

    if not device_exists:
        raise HTTPException(
            status_code=404,
            detail=f"Device '{device_id}' not found"
        )

    return interfaces.get(device_id.upper(), [])
