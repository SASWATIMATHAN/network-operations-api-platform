class NetworkOperationError(Exception):
    """Base exception for network operation failures."""

    def __init__(
        self,
        message: str,
        host: str | None = None,
        operation: str | None = None,
    ):
        super().__init__(message)
        self.host = host
        self.operation = operation


class NetworkConnectionError(NetworkOperationError):
    """Raised when a network device cannot be reached or connected to."""


class NetworkCommandError(NetworkOperationError):
    """Raised when a command cannot be executed successfully."""
