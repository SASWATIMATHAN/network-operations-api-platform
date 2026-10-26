from unittest.mock import MagicMock

import pytest

from netmiko_deployment_adapter import NetmikoDeploymentAdapter


@pytest.fixture
def mock_connection():
    connection = MagicMock()
    connection.__enter__.return_value = connection
    connection.__exit__.return_value = False
    connection.send_command.return_value = "hostname LAB11-R1\n"
    connection.send_config_set.return_value = "configuration applied"
    return connection


@pytest.fixture
def adapter(mock_connection):
    return NetmikoDeploymentAdapter(
        username="test-user",
        password="test-password",
        device_registry={
            "LAB11-R1": {
                "host": "192.0.2.10",
                "device_type": "cisco_ios",
                "port": 22,
            }
        },
        connection_factory=lambda **kwargs: mock_connection,
    )


def test_reads_running_configuration(adapter, mock_connection):
    result = adapter.get_running_configuration("LAB11-R1")

    assert result == "hostname LAB11-R1\n"
    mock_connection.send_command.assert_called_once_with(
        "show running-config",
        read_timeout=30,
    )
    mock_connection.__exit__.assert_called_once()


def test_applies_configuration_lines(adapter, mock_connection):
    result = adapter.apply_configuration(
        "LAB11-R1",
        "interface Loopback99\n description LAB11-TEST\n!",
    )

    assert result == "configuration applied"
    mock_connection.send_config_set.assert_called_once_with(
        ["interface Loopback99", "description LAB11-TEST"],
        read_timeout=30,
    )
    mock_connection.__exit__.assert_called_once()


def test_rejects_unknown_device(adapter, mock_connection):
    with pytest.raises(ValueError, match="Unknown device_id"):
        adapter.get_running_configuration("UNKNOWN")

    mock_connection.send_command.assert_not_called()


def test_rejects_empty_configuration(adapter, mock_connection):
    with pytest.raises(ValueError, match="non-empty"):
        adapter.apply_configuration("LAB11-R1", "  \n ")

    mock_connection.send_config_set.assert_not_called()


def test_rejects_device_without_management_host(mock_connection):
    adapter = NetmikoDeploymentAdapter(
        username="test-user",
        password="test-password",
        device_registry={"LAB11-R1": {"device_type": "cisco_ios"}},
        connection_factory=lambda **kwargs: mock_connection,
    )

    with pytest.raises(ValueError, match="no management host"):
        adapter.get_running_configuration("LAB11-R1")

    mock_connection.send_command.assert_not_called()


def test_connection_factory_receives_registered_settings(mock_connection):
    captured = {}

    def factory(**kwargs):
        captured.update(kwargs)
        return mock_connection

    adapter = NetmikoDeploymentAdapter(
        username="test-user",
        password="test-password",
        device_registry={
            "LAB11-R1": {
                "host": "192.0.2.10",
                "device_type": "cisco_ios",
                "port": 2222,
                "connect_timeout": 7,
            }
        },
        connection_factory=factory,
    )

    adapter.get_running_configuration("LAB11-R1")

    assert captured == {
        "host": "192.0.2.10",
        "username": "test-user",
        "password": "test-password",
        "device_type": "cisco_ios",
        "port": 2222,
        "connect_timeout": 7,
    }
