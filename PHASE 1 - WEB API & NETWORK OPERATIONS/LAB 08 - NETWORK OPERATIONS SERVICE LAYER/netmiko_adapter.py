from netmiko.exceptions import NetmikoTimeoutException

from app.network.connection import NetworkConnection
from app.network.exceptions import (
    NetworkCommandError,
    NetworkConnectionError,
)


class NetmikoAdapter:
    """Network adapter implementation using Netmiko."""

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    def execute_command(
        self,
        host: str,
        command: str,
        device_type: str = "cisco_ios",
        port: int = 22,
        connect_timeout: int = 10,
        command_timeout: int = 20,
    ) -> str:
        """Connect to a network device and execute a CLI command."""

        try:
            with NetworkConnection(
                host=host,
                username=self.username,
                password=self.password,
                device_type=device_type,
                port=port,
                connect_timeout=connect_timeout,
            ) as connection:

                try:
                    return connection.send_command(
                        command,
                        read_timeout=command_timeout,
                    )

                except NetmikoTimeoutException as exc:
                    raise NetworkCommandError(
                        message="Network command timed out",
                        host=host,
                        operation=command,
                    ) from exc

                except Exception as exc:
                    raise NetworkCommandError(
                        message="Failed to execute network command",
                        host=host,
                        operation=command,
                    ) from exc

        except NetworkCommandError:
            raise

        except Exception as exc:
            raise NetworkConnectionError(
                message="Unable to establish a network connection",
                host=host,
                operation="connect",
            ) from exc
