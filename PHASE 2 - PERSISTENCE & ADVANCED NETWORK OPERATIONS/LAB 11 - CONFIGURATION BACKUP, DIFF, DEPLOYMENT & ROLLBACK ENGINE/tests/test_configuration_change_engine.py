
import hashlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from configuration_change_engine import (  # noqa: E402
    calculate_checksum,
    compare_configurations,
    create_snapshot,
    validate_configuration,
)


@pytest.fixture
def configuration_versions():
    original = """hostname EDGE-R1
interface GigabitEthernet0/0
 description Uplink
 ip address 192.0.2.1 255.255.255.0
 no shutdown
!
"""
    updated = """hostname EDGE-R1
interface GigabitEthernet0/0
 description Production uplink
 ip address 192.0.2.1 255.255.255.0
 no shutdown
!
interface Loopback0
 ip address 198.51.100.1 255.255.255.255
!
"""
    return original, updated


def test_checksum_matches_sha256(configuration_versions):
    original, _ = configuration_versions

    assert calculate_checksum(original) == hashlib.sha256(
        original.encode("utf-8")
    ).hexdigest()


def test_snapshot_has_version_and_checksum(configuration_versions):
    original, _ = configuration_versions

    snapshot = create_snapshot("EDGE-R1", 1, original)

    assert snapshot.device_id == "EDGE-R1"
    assert snapshot.version == 1
    assert snapshot.checksum_sha256 == calculate_checksum(original)
    assert snapshot.captured_at


def test_snapshot_rejects_empty_device_id():
    with pytest.raises(ValueError, match="device_id"):
        create_snapshot(" ", 1, "hostname EDGE-R1")


def test_snapshot_rejects_invalid_version():
    with pytest.raises(ValueError, match="version"):
        create_snapshot("EDGE-R1", 0, "hostname EDGE-R1")


def test_snapshot_rejects_empty_configuration():
    with pytest.raises(ValueError, match="empty"):
        create_snapshot("EDGE-R1", 1, " \n")


def test_diff_reports_added_and_removed_lines(configuration_versions):
    original, updated = configuration_versions
    before = create_snapshot("EDGE-R1", 1, original)
    after = create_snapshot("EDGE-R1", 2, updated)

    result = compare_configurations(before, after)

    assert result.device_id == "EDGE-R1"
    assert result.from_version == 1
    assert result.to_version == 2
    assert result.additions > 0
    assert result.deletions > 0
    assert "+ description Production uplink" in result.unified_diff
    assert "+interface Loopback0" in result.unified_diff


def test_diff_rejects_different_devices():
    before = create_snapshot("EDGE-R1", 1, "hostname EDGE-R1")
    after = create_snapshot("EDGE-R2", 2, "hostname EDGE-R2")

    with pytest.raises(ValueError, match="different devices"):
        compare_configurations(before, after)


def test_diff_rejects_non_increasing_version():
    before = create_snapshot("EDGE-R1", 2, "hostname EDGE-R1")
    after = create_snapshot("EDGE-R1", 2, "hostname EDGE-R1")

    with pytest.raises(ValueError, match="higher version"):
        compare_configurations(before, after)


@pytest.mark.parametrize(
    "configuration",
    [
        "hostname EDGE-R1\ninterface Loopback0\n ip address 198.51.100.1 255.255.255.255",
        "hostname EDGE-R1\ninterface GigabitEthernet0/0\n no shutdown",
    ],
)
def test_validator_accepts_basic_configuration(configuration):
    result = validate_configuration(configuration)

    assert result.valid
    assert result.errors == ()


def test_validator_rejects_empty_configuration():
    result = validate_configuration(" \n")

    assert not result.valid
    assert any("empty" in error.lower() for error in result.errors)


@pytest.mark.parametrize(
    "command",
    [
        "write erase",
        "erase startup-config",
        "reload",
        "format flash:",
        "delete flash:startup-config",
    ],
)
def test_validator_rejects_destructive_commands(command):
    result = validate_configuration(f"hostname EDGE-R1\n{command}")

    assert not result.valid
    assert result.errors


def test_validator_warns_about_disabling_aaa():
    result = validate_configuration("hostname EDGE-R1\nno aaa new-model")

    assert result.valid
    assert any("AAA" in warning for warning in result.warnings)


def test_checksum_rejects_non_string_input():
    with pytest.raises(TypeError, match="string"):
        calculate_checksum(None)


def test_snapshot_rejects_non_string_configuration():
    with pytest.raises(TypeError, match="string"):
        create_snapshot("EDGE-R1", 1, None)
