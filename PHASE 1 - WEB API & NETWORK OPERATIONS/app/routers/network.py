from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_network_service
from app.network.exceptions import NetworkOperationError
from app.schemas.network import DeviceHealthResponse
from app.services.network_service import NetworkService


router = APIRouter(
    prefix="/network",
    tags=["Network Operations"],
)


@router.get(
    "/devices/{host}/health",
    response_model=DeviceHealthResponse,
    summary="Get live device health",
    description=(
        "Connect to a network device through Netmiko and "
        "retrieve live operational information."
    ),
)
def get_device_health(
    host: str,
    service: NetworkService = Depends(get_network_service),
) -> DeviceHealthResponse:
    """Retrieve live health information from a network device."""

    try:
        return service.get_device_health(host)

    except NetworkOperationError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "message": str(exc),
                "host": exc.host,
                "operation": exc.operation,
            },
        ) from exc
