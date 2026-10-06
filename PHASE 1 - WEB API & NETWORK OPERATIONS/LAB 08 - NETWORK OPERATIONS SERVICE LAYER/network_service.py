from time import perf_counter

from app.network.exceptions import (
    NetworkConnectionError,
    NetworkOperationError,
)
from app.network.netmiko_adapter import NetmikoAdapter
from app.schemas.network import DeviceHealthResponse
from app.schemas.network_result import NetworkResult


class NetworkService:
    """Business logic for live network operations."""

    def __init__(
        self,
        username: str,
        password: str,
        connect_timeout: int = 10,
        command_timeout: int = 20,
    ):
        self.adapter = NetmikoAdapter(
            username=username,
            password=password,
        )
        self.connect_timeout = connect_timeout
        self.command_timeout = command_timeout

    def get_device_health(self, host: str) -> DeviceHealthResponse:
        """Retrieve live operational information from a network device."""

        result = self._execute_health_check(host)

        return DeviceHealthResponse(
            host=result.host,
            reachable=result.success,
            raw_output=result.output or "",
        )

    def _execute_health_check(self, host: str) -> NetworkResult:
        """Execute the underlying network health operation."""

        start_time = perf_counter()

        try:
            output = self.adapter.execute_command(
                host=host,
                command="show version",
                connect_timeout=self.connect_timeout,
                command_timeout=self.command_timeout,
            )

            duration_ms = (perf_counter() - start_time) * 1000

            return NetworkResult(
                success=True,
                host=host,
                operation="show version",
                output=output,
                duration_ms=round(duration_ms, 2),
            )

        except NetworkConnectionError as exc:
            duration_ms = (perf_counter() - start_time) * 1000

            raise NetworkOperationError(
                message="Network device is unreachable",
                host=exc.host,
                operation=exc.operation,
            ) from exc
