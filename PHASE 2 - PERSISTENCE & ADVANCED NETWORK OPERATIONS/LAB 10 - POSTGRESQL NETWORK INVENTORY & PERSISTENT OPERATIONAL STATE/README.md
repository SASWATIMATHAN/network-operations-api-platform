# Lab 10 — PostgreSQL Network Inventory & Persistent Operational State

## 1. Overview

**Status:** Core PostgreSQL persistence implementation and database-schema validation completed. Focused tests have passed for inventory API behavior, job persistence, audit persistence, and configuration backups. Full end-to-end application and network-device integration remain to be completed.

This lab extends the Network Operations API Platform with persistent storage for device inventory and operational records using PostgreSQL, SQLAlchemy, and Alembic.

## 2. Objectives

- Store network devices and interfaces in PostgreSQL.
- Manage schema changes through version-controlled Alembic migrations.
- Support persistent operational records and background jobs.
- Maintain audit records and configuration backups.
- Validate database schema and generate machine-readable evidence.
- Establish a foundation for later integration with network devices.

## 3. Technology Stack

- Python 3.12
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Pytest
- JSON and CSV experiment outputs

## 4. Database Schema

The seven expected application tables are:

| Table | Purpose |
|---|---|
| `network_devices` | Device inventory |
| `network_interfaces` | Device interface inventory |
| `network_operations` | Operational request records |
| `network_operation_device_results` | Per-device operation results |
| `network_jobs` | Persistent job records |
| `network_audit_records` | Audit history |
| `network_configuration_backups` | Stored configuration backups |

Alembic also maintains its `alembic_version` table to track the applied schema revision.

## 5. Implementation

The application components include:

- `app/database.py` — database engine and session configuration.
- `app/models/network_inventory.py` — inventory models.
- `app/models/persistence.py` — persistent operational models.
- `app/routers/inventory.py` — inventory API routes.
- `app/schemas/inventory.py` — inventory schemas.
- `app/jobs/manager.py` — job management.
- `app/audit/service.py` — audit service.
- `app/configuration_backup_service.py` — configuration backup creation and retrieval.
- `alembic/` — database migration history.

The application and Lab 10 tests are maintained in their respective project directories.

## 6. Database Configuration

The application uses environment-based database configuration. Supported settings include:

- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`

Set the password in the environment or an appropriately protected local configuration. Do not commit credentials, print passwords, or include secrets in experiment outputs.

The configured database for the validation experiment is `network_operations`.

## 7. Migration Verification

Activate the Phase 1 application virtual environment and run migration commands from the Lab 10 directory:

```bash
cd "$LAB"
source "$APP/venv/bin/activate"

alembic current
alembic history
```

The latest applied migration is:

`ace434e09df0` — current Alembic head at the time of validation.

The preceding migration is:

`3b531f05c920` — initial network inventory tables.

## 8. Experiment and Evidence

Run the database inventory experiment:

```bash
cd "$LAB"
source "$APP/venv/bin/activate"

PYTHONPATH="$APP" python experiments/lab10_database_inventory.py
```

The experiment checks the expected database tables, records their row counts, and generates the following evidence:

- `data/raw/database_snapshot.json`
- `data/processed/database_validation.json`
- `data/processed/database_table_counts.csv`

### Latest validation result

Captured on 26 October 2026.

- Database: `network_operations`
- Validation status: `passed`
- Expected tables: 7
- Missing expected tables: 0
- Available tables: 8, including `alembic_version`

| Table | Observed row count |
|---|---:|
| `network_audit_records` | 0 |
| `network_configuration_backups` | 1 |
| `network_devices` | 1 |
| `network_interfaces` | 1 |
| `network_jobs` | 0 |
| `network_operation_device_results` | 0 |
| `network_operations` | 0 |

The inventory contains a documentation/test device and interface. The configuration-backup table contains one test backup. The addresses used in this test are documentation-only addresses and do not demonstrate live device connectivity.

## 9. Focused Test Evidence

The following focused test results were recorded:

| Test group | Result |
|---|---:|
| Live PostgreSQL schema validation | 8 passed |
| Inventory API tests | 10 passed |
| Configuration backup tests | 7 passed |
| Combined isolated persistence tests, excluding the live schema test | 21 passed |

These are results from the respective focused test runs. A complete combined test-suite run has not been confirmed, and full end-to-end application verification remains outstanding.

## 10. Security and Limitations

- Database credentials must remain outside version control.
- The database experiment verifies schema presence and row counts; it does not prove that every API workflow works end to end.
- Test inventory data does not represent a live network-device connection.
- Network-device integration with GNS3 or physical equipment has not yet been demonstrated.
- Full application-level end-to-end verification remains outstanding.

## 11. Conclusion

Lab 10 establishes PostgreSQL persistence for network inventory and operational data, applies versioned schema migrations, and generates reproducible database-validation evidence. Focused tests support the inventory, persistence, and configuration-backup components.

The next stage is to complete application-level integration checks and then validate the relevant network operations against the GNS3 topology when device connectivity is actually required.
