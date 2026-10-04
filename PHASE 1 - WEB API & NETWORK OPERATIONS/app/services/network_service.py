from app.network.exceptions import (
    NetworkConnectionError,
    NetworkOperationError,
)
from app.network.netmiko_adapter import NetmikoAdapter


class NetworkService:
    """Business logic for live network operations."""

    def __init__(self, username: str, password: str):
        self.adapter = NetmikoAdapter(
            username=username,
            password=password,
        )

    def get_device_health(self, host: str) -> dict:
        """Retrieve live operational information from a network device."""

        try:
            output = self.adapter.execute_command(
                host=host,
                command="show version",
            )

        except NetworkConnectionError as exc:
            raise NetworkOperationError(
                message="Network device is unreachable",
                host=exc.host,
                operation=exc.operation,
            ) from exc

        return {
            "host": host,
            "reachable": True,
            "raw_output": output,
        }
