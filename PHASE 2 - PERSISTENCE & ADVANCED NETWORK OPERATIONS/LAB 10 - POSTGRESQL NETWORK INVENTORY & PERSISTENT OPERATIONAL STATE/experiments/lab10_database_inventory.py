"""Capture a reproducible snapshot of the Lab 10 PostgreSQL schema."""

import csv
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
APP = ROOT / "PHASE 1 - WEB API & NETWORK OPERATIONS"
LAB = ROOT / "PHASE 2 - PERSISTENCE & ADVANCED NETWORK OPERATIONS" / (
    "LAB 10 - POSTGRESQL NETWORK INVENTORY & PERSISTENT OPERATIONAL STATE"
)
sys.path.insert(0, str(APP))

from sqlalchemy import inspect, select, func  # noqa: E402
from app.database import SessionLocal, engine  # noqa: E402
from app.models import Base  # noqa: E402

EXPECTED_TABLES = {
    "network_devices",
    "network_interfaces",
    "network_operations",
    "network_operation_device_results",
    "network_jobs",
    "network_audit_records",
    "network_configuration_backups",
}


def main() -> int:
    timestamp = datetime.now(timezone.utc).isoformat()
    inspector = inspect(engine)

    with engine.connect() as connection:
        live_tables = set(inspector.get_table_names())
        missing = sorted(EXPECTED_TABLES - live_tables)
        rows = []

        for table_name in sorted(EXPECTED_TABLES & live_tables):
            table = Base.metadata.tables.get(table_name)
            count = (
                connection.execute(select(func.count()).select_from(table)).scalar_one()
                if table is not None
                else None
            )
            rows.append({"table": table_name, "row_count": count})

    snapshot = {
        "captured_at_utc": timestamp,
        "database": os.getenv("DB_NAME", "configured database"),
        "expected_tables": sorted(EXPECTED_TABLES),
        "available_tables": sorted(live_tables),
        "missing_tables": missing,
        "table_counts": rows,
        "status": "passed" if not missing else "failed",
    }

    raw_path = LAB / "data" / "raw" / "database_snapshot.json"
    processed_json = LAB / "data" / "processed" / "database_validation.json"
    processed_csv = LAB / "data" / "processed" / "database_table_counts.csv"

    for path in (raw_path, processed_json, processed_csv):
        path.parent.mkdir(parents=True, exist_ok=True)

    raw_path.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
    processed_json.write_text(
        json.dumps(snapshot, indent=2) + "\n", encoding="utf-8"
    )
    with processed_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["table", "row_count"])
        writer.writeheader()
        writer.writerows(rows)

    print(json.dumps(snapshot, indent=2))
    print(f"\nRaw snapshot: {raw_path}")
    print(f"Processed results: {processed_json}")
    print(f"Table counts: {processed_csv}")
    return 0 if not missing else 1


if __name__ == "__main__":
    raise SystemExit(main())
