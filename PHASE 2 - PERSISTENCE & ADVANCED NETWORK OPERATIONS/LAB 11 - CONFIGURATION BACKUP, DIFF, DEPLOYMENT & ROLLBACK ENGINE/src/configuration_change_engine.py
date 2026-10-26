
"""Configuration comparison and safety validation for Lab 11."""

from __future__ import annotations

import difflib
import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class ConfigurationSnapshot:
    """An immutable configuration version."""

    device_id: str
    version: int
    configuration: str
    checksum_sha256: str
    captured_at: str


@dataclass(frozen=True)
class ConfigurationDiff:
    """Comparison between two configuration versions."""

    device_id: str
    from_version: int
    to_version: int
    additions: int
    deletions: int
    unified_diff: str


@dataclass(frozen=True)
class ValidationResult:
    """Result of validating a proposed configuration."""

    valid: bool
    errors: tuple[str, ...]
    warnings: tuple[str, ...]


def calculate_checksum(configuration: str) -> str:
    """Return the SHA-256 checksum of a configuration string."""
    if not isinstance(configuration, str):
        raise TypeError("configuration must be a string")

    return hashlib.sha256(configuration.encode("utf-8")).hexdigest()


def create_snapshot(
    device_id: str,
    version: int,
    configuration: str,
) -> ConfigurationSnapshot:
    """Create a versioned snapshot with integrity metadata."""
    if not device_id.strip():
        raise ValueError("device_id must not be empty")
    if version < 1:
        raise ValueError("version must be at least 1")
    if not isinstance(configuration, str):
        raise TypeError("configuration must be a string")
    if not configuration.strip():
        raise ValueError("configuration must not be empty")

    return ConfigurationSnapshot(
        device_id=device_id,
        version=version,
        configuration=configuration,
        checksum_sha256=calculate_checksum(configuration),
        captured_at=datetime.now(timezone.utc).isoformat(),
    )


def compare_configurations(
    earlier: ConfigurationSnapshot,
    later: ConfigurationSnapshot,
) -> ConfigurationDiff:
    """Generate a unified diff between two snapshots."""
    if earlier.device_id != later.device_id:
        raise ValueError("Cannot compare snapshots from different devices")
    if later.version <= earlier.version:
        raise ValueError("The later snapshot must have a higher version")

    old_lines = earlier.configuration.splitlines()
    new_lines = later.configuration.splitlines()

    diff_lines = list(
        difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f"{earlier.device_id}/v{earlier.version}",
            tofile=f"{later.device_id}/v{later.version}",
            lineterm="",
        )
    )

    additions = sum(
        1 for line in diff_lines
        if line.startswith("+") and not line.startswith("+++")
    )
    deletions = sum(
        1 for line in diff_lines
        if line.startswith("-") and not line.startswith("---")
    )

    return ConfigurationDiff(
        device_id=earlier.device_id,
        from_version=earlier.version,
        to_version=later.version,
        additions=additions,
        deletions=deletions,
        unified_diff="\n".join(diff_lines),
    )


def validate_configuration(configuration: str) -> ValidationResult:
    """Perform basic offline safety checks before deployment."""
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(configuration, str):
        raise TypeError("configuration must be a string")

    if not configuration.strip():
        errors.append("Configuration must not be empty")
        return ValidationResult(False, tuple(errors), tuple(warnings))

    lines = [
        line.strip()
        for line in configuration.splitlines()
        if line.strip() and not line.strip().startswith("!")
    ]

    if not lines:
        errors.append("Configuration contains no active commands")

    forbidden_commands = (
        "write erase",
        "erase startup-config",
        "reload",
        "format ",
        "delete ",
    )

    for line_number, line in enumerate(lines, start=1):
        normalized = line.lower()

        if any(
            normalized == command.strip()
            or normalized.startswith(command)
            for command in forbidden_commands
        ):
            errors.append(
                f"Potentially destructive command at active line "
                f"{line_number}: {line}"
            )

    if any(line.lower() == "no aaa new-model" for line in lines):
        warnings.append(
            "Disabling AAA may weaken access controls or disrupt management"
        )

    if any(line.lower() == "no ip access-group" for line in lines):
        warnings.append(
            "An ACL removal command may reduce network protection"
        )

    return ValidationResult(
        valid=not errors,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )
