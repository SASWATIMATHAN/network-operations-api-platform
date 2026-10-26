"""Netmiko adapter for controlled configuration deployment and rollback."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from app.network.connection import NetworkConnection


class NetmikoDeploymentAdapter:
    """Adapt Netmiko sessions to the Lab 11 deployment workflow.

    Credentials are supplied at construction time. This adapter does not
    read credentials from source code or automatically connect to devices.
    """

    def __init__(
        self,
        username: str,
        password: str,
        device_registry: dict[str, dict[str, Any]],
        connection_factory: Callable[..., Any] | None = None,
        command_timeout: int = 30,
    ) -> None:
        self.username = username
        self.password = password
        self.device_registry = device_registry
        self.connection_factory = connection_factory or NetworkConnection
        self.command_timeout = command_timeout

    def _device_settings(self, device_id: str) -> dict[str, Any]:
        """Return connection settings for a registered device."""

        settings = self.device_registry.get(device_id)

        if settings is None:
            raise ValueError(f"Unknown device_id: {device_id}")

        host = settings.get("host")
        if not host:
            raise ValueError(
                f"Device {device_id!r} has no management host configured"
            )

        return {
            "host": host,
            "username": self.username,
            "password": self.password,
            "device_type": settings.get("device_type", "cisco_ios"),
            "port": int(settings.get("port", 22)),
            "connect_timeout": int(settings.get("connect_timeout", 10)),
        }

    def _open_connection(self, device_id: str):
        """Open a session using the shared project connection wrapper."""

        settings = self._device_settings(device_id)
        return self.connection_factory(**settings)

    def get_running_configuration(self, device_id: str) -> str:
        """Read the current running configuration without modifying the device."""

        with self._open_connection(device_id) as connection:
            output = connection.send_command(
                "show running-config",
                read_timeout=self.command_timeout,
            )

        if not isinstance(output, str) or not output.strip():
            raise RuntimeError(
                f"Device {device_id!r} returned an empty running configuration"
            )

        return output

    def apply_configuration(
        self,
        device_id: str,
        configuration: str,
    ) -> str:
        """Apply configuration lines to a registered device.

        This method changes device configuration. Use only after the proposed
        configuration has passed validation and the original configuration
        has been persistently backed up.
        """

        if not isinstance(configuration, str) or not configuration.strip():
            raise ValueError("Configuration must be a non-empty string")

        settings = self._device_settings(device_id)

        # Avoid accidentally sending a full show/run output or terminal
        # display commands as configuration input.
        commands = [
            line.strip()
            for line in configuration.splitlines()
            if line.strip() and not line.strip().startswith("!")
        ]

        if not commands:
            raise ValueError("Configuration contains no executable commands")

        with self.connection_factory(**settings) as connection:
            output = connection.send_config_set(
                commands,
                read_timeout=self.command_timeout,
            )

        if not isinstance(output, str):
            raise RuntimeError(
                f"Device {device_id!r} returned an unexpected configuration response"
            )

        return output
