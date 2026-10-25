"""PostgreSQL integration tests for the Lab 10 database schema."""

import pytest
from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError

from app.database import engine

EXPECTED_TABLES = {
    "network_devices",
    "network_interfaces",
    "network_operations",
    "network_operation_device_results",
    "network_jobs",
    "network_audit_records",
    "network_configuration_backups",
}


@pytest.fixture(scope="module")
def live_schema():
    try:
        with engine.connect() as connection:
            return set(inspect(connection).get_table_names())
    except SQLAlchemyError as exc:
        pytest.fail(
            "Cannot connect to the configured PostgreSQL database. "
            "Check DB_HOST, DB_PORT, DB_NAME, DB_USER, and DB_PASSWORD. "
            f"Database error: {exc}"
        )


def test_all_lab10_tables_exist(live_schema):
    missing = EXPECTED_TABLES - live_schema
    assert not missing, f"Lab 10 database tables are missing: {sorted(missing)}"


@pytest.mark.parametrize(
    "table_name",
    sorted(EXPECTED_TABLES),
)
def test_each_expected_table_has_columns(live_schema, table_name):
    assert table_name in live_schema
    columns = inspect(engine).get_columns(table_name)
    assert columns, f"Table {table_name!r} has no columns"
