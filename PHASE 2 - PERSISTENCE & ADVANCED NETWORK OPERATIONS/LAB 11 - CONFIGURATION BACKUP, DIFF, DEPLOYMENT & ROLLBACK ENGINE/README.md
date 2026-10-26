# Lab 11 — Configuration Backup, Diff, Deployment & Rollback Engine

## 1. Objective

Implement a controlled network configuration change workflow with safety validation, pre-deployment snapshots, deployment verification, rollback handling, and integration with the persistent backup service developed in Lab 10.

## 2. Architecture

The lab contains five source modules:

- `configuration_change_engine.py` — configuration snapshots, change analysis, and safety validation.
- `deployment_workflow.py` — validation, pre-change snapshot creation, deployment, verification, and rollback handling.
- `netmiko_deployment_adapter.py` — device communication through the shared Phase 1 Netmiko connection wrapper.
- `persistent_deployment_workflow.py` — persistent pre-deployment backup integration.
- `postgres_backup_integration.py` — PostgreSQL backup integration.

Tests cover the configuration change engine, deployment workflow, Netmiko adapter, persistent workflow, and PostgreSQL deployment integration.

## 3. Execution Environment

- Platform: Ubuntu under WSL 2
- Language: Python
- Virtual environment: Phase 1 application `venv`
- Network automation: Netmiko
- Database integration: PostgreSQL through the Lab 10 application

The Lab 11 source and tests are maintained in this directory. The existing Phase 1 application provides shared network connection functionality.

## 4. Deployment Safety

The intended workflow is:

1. Validate the proposed configuration.
2. Retrieve the current running configuration.
3. Create a pre-deployment snapshot.
4. Persist the original configuration before attempting deployment.
5. Apply the proposed configuration.
6. Verify the result.
7. Attempt rollback if deployment or verification fails.

Persistent backup failures prevent the persistent workflow from proceeding with deployment. Rollback is best-effort and must itself be verified.

**Important:** Deployment and rollback can modify a live device. They must only be performed with explicit authorization and an approved configuration.

## 5. Validation Results

### Automated tests

The following test command was run with the PostgreSQL integration test excluded because database credentials were not configured in the current shell:

```bash
PYTHONPATH="$APP:$LAB/src" \
pytest -q "$LAB/tests" \
  --ignore="$LAB/tests/test_postgres_deployment_integration.py"
```

Result: **34 passed in 0.45 seconds.**

### Live-device read-only verification

Device: R1
Management address: `192.168.40.10`
Connection method: SSH using the Lab 11 Netmiko adapter

Results:

- SSH connection: successful
- Running configuration retrieval: successful
- Configuration lines retrieved: 120
- Configuration characters retrieved: 1,363
- Configuration changes made during verification: none

The configuration contents were not printed in the verification output.

### PostgreSQL integration

The PostgreSQL integration test has not yet been validated. The application requires `DB_PASSWORD`, which was not configured in the shell during this validation. No database password was invented or added to source code.

## 6. Security and Operational Notes

- Supply device credentials at runtime; do not hard-code them in source files.
- Keep database credentials outside version-controlled source files.
- Do not expose device configurations or credentials in logs or reports.
- Back up the current configuration before an authorized deployment.
- Verify both deployment and rollback outcomes.
- Do not treat a successful SSH connection as proof that deployment or persistent backup has been tested.

## 7. Conclusion

Lab 11's core workflow and adapter tests passed, and the real R1 read-only connection path successfully retrieved its running configuration. PostgreSQL integration and a controlled configuration deployment remain unverified. No live configuration changes were made during device verification.
