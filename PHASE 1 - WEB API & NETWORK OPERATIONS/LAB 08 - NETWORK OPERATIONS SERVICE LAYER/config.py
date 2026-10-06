import os


class Settings:
    """Application configuration loaded from environment variables."""

    def __init__(self):
        self.network_username = os.getenv("NETWORK_USERNAME", "admin")
        self.network_password = os.getenv("NETWORK_PASSWORD")

        self.network_connect_timeout = int(
            os.getenv("NETWORK_CONNECT_TIMEOUT", "10")
        )
        self.network_command_timeout = int(
            os.getenv("NETWORK_COMMAND_TIMEOUT", "20")
        )

        if not self.network_password:
            raise RuntimeError(
                "NETWORK_PASSWORD environment variable is not configured"
            )


settings = Settings()
