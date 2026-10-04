import os


class Settings:
    """Application configuration loaded from environment variables."""

    def __init__(self):
        self.network_username = os.getenv("NETWORK_USERNAME", "admin")
        self.network_password = os.getenv("NETWORK_PASSWORD")

        if not self.network_password:
            raise RuntimeError(
                "NETWORK_PASSWORD environment variable is not configured"
            )


settings = Settings()
