from netmiko import ConnectHandler
from netmiko.exceptions import (
    NetmikoAuthenticationException,
    NetmikoTimeoutException,
)

from app.network.exceptions import (
    NetworkCommandError,
    NetworkConnectionError,
)


class NetmikoAdapter:
    """Low-level network connection adapter using Netmiko."""

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    def execute_command(
        self,
        host: str,
        command: str,
        device_type: str = "cisco_ios",
        port: int = 22,
    ) -> str:
        """Connect to a network device and execute a CLI command."""

        device = {
            "device_type": device_type,
            "host": host,
            "username": self.username,
            "password": self.password,
            "port": port,
            "conn_timeout": 10,
        }

        try:
            connection = ConnectHandler(**device)

        except (
            NetmikoTimeoutException,
            NetmikoAuthenticationException,
        ) as exc:
            raise NetworkConnectionError(
                message="Unable to establish a network connection",
                host=host,
                operation="connect",
            ) from exc

        try:
            try:
                output = connection.send_command(
                    command,
                    read_timeout=20,
                )
            except Exception as exc:
                raise NetworkCommandError(
                    message="Failed to execute network command",
                    host=host,
                    operation=command,
                ) from exc

            return output

        finally:
            connection.disconnect()
