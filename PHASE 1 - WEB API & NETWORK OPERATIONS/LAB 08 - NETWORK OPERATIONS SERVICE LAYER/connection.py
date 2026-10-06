from netmiko import ConnectHandler
from netmiko.exceptions import (
    NetmikoAuthenticationException,
    NetmikoTimeoutException,
)


class NetworkConnection:
    """Manage the lifecycle of a Netmiko network connection."""

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        device_type: str = "cisco_ios",
        port: int = 22,
        connect_timeout: int = 10,
    ):
        self.host = host
        self.username = username
        self.password = password
        self.device_type = device_type
        self.port = port
        self.connect_timeout = connect_timeout
        self.connection = None

    def connect(self):
        """Establish a connection to the network device."""

        device = {
            "device_type": self.device_type,
            "host": self.host,
            "username": self.username,
            "password": self.password,
            "port": self.port,
            "conn_timeout": self.connect_timeout,
        }

        try:
            self.connection = ConnectHandler(**device)

        except (
            NetmikoTimeoutException,
            NetmikoAuthenticationException,
        ):
            self.connection = None
            raise

        return self.connection

    def disconnect(self) -> None:
        """Close the active network connection."""

        if self.connection is not None:
            self.connection.disconnect()
            self.connection = None

    def __enter__(self):
        """Open the connection when entering a context."""

        return self.connect()

    def __exit__(self, exc_type, exc_value, traceback):
        """Guarantee connection cleanup when leaving the context."""

        self.disconnect()
        return False
