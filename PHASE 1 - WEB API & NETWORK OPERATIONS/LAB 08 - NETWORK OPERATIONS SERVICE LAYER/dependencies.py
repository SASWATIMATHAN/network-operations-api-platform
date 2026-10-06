from app.config import settings
from app.services.network_service import NetworkService


def get_network_service() -> NetworkService:
    """Provide a configured network service for API requests."""

    return NetworkService(
        username=settings.network_username,
        password=settings.network_password,
        connect_timeout=settings.network_connect_timeout,
        command_timeout=settings.network_command_timeout,
    )
