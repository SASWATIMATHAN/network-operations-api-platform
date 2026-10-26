# Lab 14 — Integrated Network Operations Platform

## 1. Overview

Lab 14 is the integration layer for the Network Operations API Platform. It demonstrates how inventory validation, configuration backup, configuration deployment, ACL deployment, verification, rollback, and audit recording can be coordinated through a single workflow.

The objective is to provide a common orchestration service for network operations while maintaining separation between individual operational modules.

## 2. Architecture

```text
Network Operations Request
           |
           v
   Integration Service
           |
           v
    Inventory Validation
           |
           v
   Configuration Backup
           |
           v
 Configuration Deployment
           |
           v
      ACL Deployment
           |
           v
       Verification
           |
      +----+----+
      |         |
    Success   Failure
      |         |
      v         v
   Complete   Rollback
      |         |
      +----+----+
           |
           v
       Audit Event
```

## 3. Implemented Components

### Integration Service

File: `src/integration_service.py`

- Coordinates workflow stages through configurable handlers.
- Records the failed stage and workflow result.
- Stops execution when inventory validation fails.
- Invokes rollback when deployment or verification fails.
- Handles audit-recording errors separately from the primary workflow result.

### FastAPI Integration Router

File: `src/integration_router.py`

Implemented endpoints:

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/integration/dry-run` | Executes a simulated integration workflow. |
| GET | `/integration/inventory-check/{device_id}` | Checks a device against persistent inventory. |

The dry-run endpoint uses simulated handlers and does not perform live network configuration changes.

The inventory-check endpoint queries the Lab 10 SQLAlchemy inventory model. It returns device details when found, HTTP 404 when the device is absent, and HTTP 503 when the database is unavailable.

### Application Registration

The integration router is registered with the main FastAPI application in the Phase 1 application directory.

## 4. Directory Structure

```text
LAB 14 - INTEGRATED NETWORK OPERATIONS PLATFORM/
├── README.md
├── src/
│   ├── integration_service.py
│   └── integration_router.py
├── tests/
│   ├── test_integration_service.py
│   └── test_inventory_safety.py
└── figures/
```

## 5. Testing and Validation

The latest recorded test result was **10 tests passed**.

Test coverage includes:

- Successful workflow execution.
- Inventory validation failures and exceptions.
- Deployment failure and rollback handling.
- Verification failure and rollback handling.
- Rollback failure reporting.
- Audit-recording failure handling.
- Passing request details to handlers.
- Handling unsuccessful inventory results, including `False` and `None`.

The FastAPI dry-run endpoint was also tested successfully, and the integration routes were confirmed in the application's OpenAPI schema.

## 6. Technology Stack

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- PostgreSQL
- Pytest
- Existing network automation modules from earlier project labs

## 7. Current Limitations

- The integration service has been tested with simulated handlers.
- Full connection to the actual Lab 11 configuration backup/deployment/rollback and Lab 13 ACL automation workflows remains unfinished.
- Live-device validation through GNS3 has not been completed.
- PostgreSQL was unavailable during the latest development session, so the persistent inventory endpoint was not validated against a running database in that session.
- The integration workflow has not been validated as a complete production deployment.

## 8. Conclusion

Lab 14 establishes the orchestration structure for a unified network operations workflow. It demonstrates stage coordination, failure handling, rollback invocation, audit handling, API registration, and persistent inventory validation.

The service-level tests and simulated API workflow passed. Completing the remaining module connections and live infrastructure validation would be required before describing the platform as fully integrated or production-ready.
