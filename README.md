# 🌐 NETWORK OPERATIONS API PLATFORM

<p align="center">

```text
███╗   ██╗███████╗████████╗██╗    ██╗ ██████╗ ██████╗ ██╗  ██╗
████╗  ██║██╔════╝╚══██╔══╝██║    ██║██╔═══██╗██╔══██╗██║ ██╔╝
██╔██╗ ██║█████╗     ██║   ██║ █╗ ██║██║   ██║██████╔╝█████╔╝
██║╚██╗██║██╔══╝     ██║   ██║███╗██║██║   ██║██╔═══╝ ██╔═██╗
██║ ╚████║███████╗   ██║   ╚███╔███╔╝╚██████╔╝██║     ██║  ██╗
╚═╝  ╚═══╝╚══════╝   ╚═╝    ╚══╝╚══╝  ╚═════╝ ╚═╝     ╚═╝  ╚═╝
              NETWORK AUTOMATION & OPERATIONS
```

### An API-driven platform for network management, configuration lifecycle automation, security policy enforcement, and operational auditing.

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-REST%20API-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-4169E1?logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-D71F00)
![Alembic](https://img.shields.io/badge/Alembic-Migrations-3775A9)
![Pytest](https://img.shields.io/badge/Pytest-Testing-0A9EDC?logo=pytest&logoColor=white)
![Netmiko](https://img.shields.io/badge/Netmiko-Network%20Automation-orange)
![GNS3](https://img.shields.io/badge/GNS3-Network%20Simulation-4A90E2)
![Ubuntu](https://img.shields.io/badge/Environment-Ubuntu%20%7C%20WSL-E95420?logo=ubuntu&logoColor=white)

**Project Type:** Network Engineering · Python Development · REST API Engineering · Network Automation

**Development Status:** Core modules developed; final integrated workflow and live-device validation remain incomplete.

</p>




## 📌 1. Project Overview

The **Network Operations API Platform** is a modular Python project developed to organize network management and automation tasks through a common application interface.

Network operations involve several interconnected responsibilities: device inventory management, configuration retrieval, configuration changes, security policy enforcement, job execution, operational auditing, and access control. Managing these activities through disconnected scripts and manual procedures can make workflows difficult to standardize and audit.

This project explores a structured software approach to these responsibilities using a FastAPI application, network automation components, persistent database models, configuration management workflows, authentication and authorization, and a final orchestration layer.

The repository is organized into two phases containing fourteen progressively developed labs.

- **Phase 1 — Web API & Network Operations:** Labs 01–09.
- **Phase 2 — Persistence & Advanced Network Operations:** Labs 10–14.

Each lab addresses a specific engineering responsibility. The final lab introduces an integration service intended to coordinate several of the previously developed modules.

## 🎯 2. Project Objectives

The primary objectives are:

- Develop a REST API foundation for network operations.
- Build structured endpoints for inventory, network requests, jobs, and operational activities.
- Introduce reusable network service and device connection components.
- Explore synchronous and asynchronous multi-device operation patterns.
- Record operational events for traceability.
- Store network inventory and operational state in PostgreSQL.
- Manage configuration backups, configuration differences, deployment, and rollback workflows.
- Implement JWT-based authentication and role-based access control.
- Translate validated network security policies into device-oriented ACL configurations.
- Coordinate operational stages through an integration service.
- Apply automated testing and modular software design.
- Maintain documentation, screenshots, and a reproducible development structure.

## 🏗️ 3. High-Level Architecture

```text
                       API CLIENT
                           |
                           v
                 +---------------------+
                 |    FastAPI App      |
                 |  REST API / OpenAPI |
                 +---------------------+
                           |
             +-------------+-------------+
             |             |             |
             v             v             v
        Network API    Inventory API   Operations API
             |             |             |
             +-------------+-------------+
                           |
                           v
                 +---------------------+
                 | Authentication and |
                 | Role-Based Access   |
                 +---------------------+
                           |
                           v
                 +---------------------+
                 | Network Operations  |
                 | Service Layer       |
                 +---------------------+
                           |
             +-------------+-------------+
             |             |             |
             v             v             v
        Device Access   Job Handling   Audit Events
             |             |             |
             +-------------+-------------+
                           |
                           v
                 +---------------------+
                 | PostgreSQL / ORM    |
                 | Persistent State    |
                 +---------------------+
                           |
                           v
                 +---------------------+
                 | Configuration       |
                 | Backup / Diff /     |
                 | Deployment / Rollback|
                 +---------------------+
                           |
                           v
                 +---------------------+
                 | Security Policy and |
                 | ACL Automation      |
                 +---------------------+
                           |
                           v
                 +---------------------+
                 | Integration Service |
                 | Validation /        |
                 | Verification /      |
                 | Rollback / Audit    |
                 +---------------------+
                           |
                           v
                  Network Devices or
                   GNS3 Topology
```

*The diagram represents the project's intended architecture. Not every component has been validated together in a complete end-to-end execution.*

## 🗂️ 4. Repository Organization

The project root contains the main documentation, repository configuration, and the two development phases.

```text
PROJECT 3 - NETWORK OPERATIONS API PLATFORM/
│
├── README.md
├── LICENSE
├── .gitignore
│
├── PHASE 1 - WEB API & NETWORK OPERATIONS/
│   ├── README.md
│   ├── .gitignore
│   ├── requirements.txt
│   │
│   ├── LAB 01 - PYTHON & FASTAPI ENVIRONMENT SETUP/
│   ├── LAB 02 - FASTAPI FUNDAMENTALS/
│   ├── LAB 03 - REST API - GET/
│   ├── LAB 04 - REST API POST/
│   ├── LAB 05 - REST API - PUT & DELETE/
│   ├── LAB 06 - PYDANTIC VALIDATION/
│   ├── LAB 07 - LIVE NETWORK OPERATIONS/
│   ├── LAB 08 - NETWORK OPERATIONS SERVICE LAYER/
│   ├── LAB 09 - MULTI-DEVICE ASYNCHRONOUS OPERATIONS
│   │            & AUDIT ENGINE/
│   │
│   └── app/
│       ├── main.py
│       ├── config.py
│       ├── database.py
│       ├── dependencies.py
│       ├── audit/
│       ├── jobs/
│       ├── models/
│       ├── network/
│       ├── operations/
│       ├── routers/
│       ├── schemas/
│       └── services/
│
└── PHASE 2 - PERSISTENCE & ADVANCED NETWORK OPERATIONS/
    ├── README.md
    │
    ├── LAB 10 - POSTGRESQL NETWORK INVENTORY
    │            & PERSISTENT OPERATIONAL STATE/
    ├── LAB 11 - CONFIGURATION BACKUP, DIFF,
    │            DEPLOYMENT & ROLLBACK ENGINE/
    ├── LAB 12 - JWT AUTHENTICATION & RBAC SECURITY/
    ├── LAB 13 - NETWORK SECURITY POLICY
    │            & ACL AUTOMATION ENGINE/
    └── LAB 14 - INTEGRATED NETWORK OPERATIONS PLATFORM/
```

The repository also contains lab-specific source files, tests, database migrations, example configuration files, screenshots, figures, and development artifacts.

## 🧭 5. Phase 1 — Web API & Network Operations

Phase 1 establishes the API foundation and develops network operations functionality incrementally.

### Lab 01 — Python & FastAPI Environment Setup

**Focus:** Development environment and application initialization.

- Python and FastAPI environment setup.
- Project directory organization.
- Dependency installation and requirements management.
- Initial application entry point.
- Uvicorn server execution and reload workflow.
- Initial API and health-endpoint validation.
- Git configuration and repository hygiene.

**Engineering outcome:** Establishes the application foundation and development workflow.

### Lab 02 — FastAPI Fundamentals

**Focus:** API endpoint design and request handling.

- FastAPI route definitions.
- Request and response behavior.
- Device-related API examples.
- Lookup and filtering patterns.
- HTTP error handling.
- Interactive API documentation through Swagger UI.

**Engineering outcome:** Establishes the basic REST API interaction model.

### Lab 03 — REST API: GET

**Focus:** Resource retrieval.

- HTTP GET operations.
- Reading network-related resource information.
- Device lookup and retrieval patterns.
- API response inspection.
- Validation of retrieval behavior.

**Engineering outcome:** Introduces read-oriented API operations.

### Lab 04 — REST API: POST

**Focus:** Resource creation and submission.

- HTTP POST operations.
- Request body handling.
- Submission of structured data.
- Response validation.
- API contract inspection.

**Engineering outcome:** Introduces create-oriented API behavior.

### Lab 05 — REST API: PUT & DELETE

**Focus:** Resource modification and removal.

- HTTP PUT operations.
- Updating existing resources.
- HTTP DELETE operations.
- Resource lifecycle behavior.
- Response and error handling.

**Engineering outcome:** Extends the API beyond retrieval and creation to resource management.

### Lab 06 — Pydantic Validation

**Focus:** Structured input validation.

- Pydantic data models.
- Request schema validation.
- Field and type constraints.
- Invalid input handling.
- Consistent API data contracts.

**Engineering outcome:** Adds structured validation at the API boundary.

### Lab 07 — Live Network Operations

**Focus:** Network operations beyond static API examples.

- Live network operation concepts.
- Device-oriented request handling.
- Network command execution workflows.
- Operational response inspection.
- Integration concepts for network devices.

**Engineering outcome:** Introduces the device-facing side of network automation.

*Live-device capabilities depend on the configured devices, credentials, connection settings, and available network environment.*

### Lab 08 — Network Operations Service Layer

**Focus:** Separation of API and network logic.

The lab contains dedicated components such as:

- `config.py`
- `connection.py`
- `dependencies.py`
- `netmiko_adapter.py`
- `network_result.py`
- `network_service.py`

The service-layer design separates network connection handling, adapter logic, configuration, and result representation from the HTTP interface.

**Engineering outcome:** Establishes a reusable network operations layer rather than placing all network logic directly in API endpoints.

### Lab 09 — Multi-Device Asynchronous Operations & Audit Engine

**Focus:** Coordinating operations across multiple devices and tracking outcomes.

- Multi-device operation patterns.
- Asynchronous execution concepts.
- Job-oriented processing.
- Operational result handling.
- Audit-related workflows.
- Structured reporting of operational outcomes.

**Engineering outcome:** Introduces the foundations for scalable network operation workflows and auditability.

### Phase 1 summary

Phase 1 establishes the API, validation, network service, device-access, job, and audit foundations used by the advanced modules in Phase 2.

See [`PHASE 1 - WEB API & NETWORK OPERATIONS/README.md`](PHASE%201%20-%20WEB%20API%20%26%20NETWORK%20OPERATIONS/README.md) for phase-level documentation.

---

## 🚀 6. Phase 2 — Persistence & Advanced Network Operations

Phase 2 extends the application with persistent state, configuration lifecycle workflows, security controls, and orchestration.

### Lab 10 — PostgreSQL Network Inventory & Persistent Operational State

**Focus:** Relational persistence for network operations.

The module includes database-related components such as:

- SQLAlchemy models and database access.
- Network inventory persistence.
- Operational record persistence.
- Job and audit persistence.
- Configuration backup persistence integration.
- Alembic migration configuration and revision files.
- Database validation and inventory experiments.

The migration history in the repository includes:

- `3b531f05c920_create_network_inventory_tables.py`
- `ace434e09df0_add_persistent_operations_jobs_audit_.py`

The database configuration and runtime availability must be valid before database-dependent endpoints or tests can succeed.

**Engineering outcome:** Introduces the persistence foundation for inventory and operational state.

### Lab 11 — Configuration Backup, Diff, Deployment & Rollback Engine

**Focus:** Configuration lifecycle management.

The module contains components for:

- Configuration change processing.
- Deployment workflow orchestration.
- Netmiko deployment adapter functionality.
- Persistent deployment workflows.
- PostgreSQL backup integration.
- Automated tests for configuration changes and deployment behavior.

Relevant source files include:

- `configuration_change_engine.py`
- `deployment_workflow.py`
- `netmiko_deployment_adapter.py`
- `persistent_deployment_workflow.py`
- `postgres_backup_integration.py`

**Engineering outcome:** Structures configuration changes around backup, comparison, deployment, and recovery concepts.

### Lab 12 — JWT Authentication & RBAC Security

**Focus:** Authentication and role-based authorization.

The module contains:

- Authentication models.
- Authentication API router.
- Dependency functions.
- Permission definitions.
- Security and token-handling logic.
- Administrative bootstrap functionality.
- Authentication and RBAC tests.

Relevant source files include:

- `auth_models.py`
- `auth_router.py`
- `bootstrap_admin.py`
- `dependencies.py`
- `permissions.py`
- `security.py`

The project's intended permission model distinguishes **ADMIN**, **OPERATOR**, and **VIEWER** roles.

**Engineering outcome:** Introduces token-based identity and role-aware access control.

### Lab 13 — Network Security Policy & ACL Automation Engine

**Focus:** Policy validation and ACL-oriented automation.

The module contains:

- `security_policy.py`
- `ios_acl_generator.py`
- `acl_deployment_workflow.py`

The intended workflow is:

```text
Security Policy
      |
      v
Policy Validation
      |
      v
Device-Specific Translation
      |
      v
Cisco IOS ACL Generation
      |
      v
Deployment Workflow
      |
      v
Verification and Result Handling
```

**Engineering outcome:** Establishes a policy-oriented approach to generating and managing network access control configurations.

### Lab 14 — Integrated Network Operations Platform

**Focus:** Common workflow orchestration.

The integration service coordinates stages intended to cover:

1. Inventory validation.
2. Configuration backup.
3. Configuration deployment.
4. ACL deployment.
5. Verification.
6. Rollback on applicable failures.
7. Audit-event recording.

Implemented components include:

- `src/integration_service.py`
- `src/integration_router.py`
- `tests/test_integration_service.py`
- `tests/test_inventory_safety.py`

The FastAPI integration router exposes:

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/integration/dry-run` | Executes a simulated integration workflow. |
| `GET` | `/integration/inventory-check/{device_id}` | Checks a device against persistent inventory. |

The dry-run endpoint uses simulated handlers. The inventory-check endpoint relies on the PostgreSQL-backed inventory model.

**Recorded validation:** The latest Lab 14 service test run passed all 10 tests, and the simulated API workflow was tested successfully.

**Remaining limitations:** The real Lab 11 and Lab 13 handlers have not been fully connected to the integrated workflow. Complete end-to-end validation with Lab 12 authorization, a running PostgreSQL database, and live GNS3 devices has not been completed.

**Engineering outcome:** Establishes the orchestration structure for a unified network operations workflow.

See [`PHASE 2 - PERSISTENCE & ADVANCED NETWORK OPERATIONS/README.md`](PHASE%202%20-%20PERSISTENCE%20%26%20ADVANCED%20NETWORK%20OPERATIONS/README.md) for the phase-level overview.

---

## 🧰 7. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Primary implementation language |
| FastAPI | REST API framework |
| Pydantic | Request and data validation |
| Uvicorn | ASGI application server |
| SQLAlchemy | Database models and access |
| PostgreSQL | Relational persistence |
| Alembic | Database schema migrations |
| Netmiko | Network device connection and automation support |
| Pytest | Automated testing |
| OpenAPI / Swagger UI | API schema and interactive documentation |
| GNS3 | Network topology simulation |
| Ubuntu on WSL | Development environment |
| Git | Version control |

The presence of a technology in this table describes its role in the project. Actual use depends on the individual module and its runtime configuration.

## 🔐 8. Security and Reliability Design

The project explores several network automation safeguards.

### Authentication and authorization

JWT-based authentication and role-based access control are developed in Lab 12. Full enforcement across the final integrated workflow remains to be validated.

### Inventory validation

Inventory validation checks whether a requested device is represented in persistent inventory before proceeding with applicable operations.

### Configuration backup and rollback

The configuration lifecycle module provides a structure for backing up configurations, processing changes, deploying updates, and handling rollback.

### Policy validation

The ACL automation module separates policy validation from device-specific configuration generation.

### Auditability

Audit functionality provides a way to record operational events and outcomes.

### Failure handling

The Lab 14 integration service is designed to stop when required workflow stages fail and invoke rollback for applicable deployment or verification failures.

These mechanisms require additional end-to-end, security, and infrastructure validation before production use.

## 🧪 9. Testing and Validation

Automated tests are distributed across the project modules.

Examples of test files visible in the repository include:

- Lab 10: `test_lab10_database_schema.py`
- Lab 10: `test_lab10_inventory_api.py`
- Lab 11: `test_configuration_change_engine.py`
- Lab 11: `test_deployment_workflow.py`
- Lab 12: `test_auth_api.py`
- Lab 12: `test_security_rbac.py`
- Lab 13: `test_acl_deployment_workflow.py`
- Lab 13: `test_security_policy.py`
- Lab 14: `test_integration_service.py`
- Lab 14: `test_inventory_safety.py`

The latest recorded Lab 14 service test result was:

**10 passed.**

Other validation work included API endpoint checks, OpenAPI registration checks, database migration work, and module-specific testing.

These results are specific to the tests executed during development. They do not establish that every test across the repository passes in the current environment.

## 💻 10. Development Environment and Setup

The project was developed in Ubuntu on WSL, with the Phase 1 virtual environment located inside the Phase 1 directory.

### Activate the virtual environment

```bash
ROOT="$HOME/NETWORK OPERATIONS/PROJECT 3 - NETWORK OPERATIONS API PLATFORM"
APP="$ROOT/PHASE 1 - WEB API & NETWORK OPERATIONS"

cd "$APP"
source venv/bin/activate
```

### Start the FastAPI application

```bash
uvicorn app.main:app --reload
```

If the application starts successfully, the interactive documentation is available at:

- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

Application startup and endpoint behavior depend on the current dependencies, configuration, environment variables, and availability of required services.

### Run Phase 1 tests

```bash
cd "$APP"
python -m pytest
```

### Database-dependent operations

Lab 10 and related persistent operations require a working PostgreSQL service and valid connection settings. Database-dependent tests may fail when the service is unavailable.

Do not use production credentials or expose secrets in source control. Configure credentials through appropriate environment variables or local configuration files excluded from version control.

## 📁 11. Documentation and Evidence

The repository includes documentation and evidence distributed across the labs.

- Root README: overall project description and architecture.
- Phase 1 README: application foundation and Labs 01–09.
- Phase 2 README: persistence and advanced modules, Labs 10–14.
- Lab-specific READMEs: individual lab objectives and implementation notes.
- Screenshots and figures: development and testing evidence.
- Source directories: implementation modules.
- Test directories: automated test cases.
- Migration files: database schema evolution.

This layered documentation structure makes the repository easier to navigate without placing every implementation detail into the root README.

## 📊 12. Project Status

The project is being closed at its current development state.

| Area | Status |
|---|---|
| Phase 1 API foundation | Developed |
| REST API methods and validation | Developed |
| Network operations service layer | Developed |
| Multi-device operations and audit concepts | Developed |
| PostgreSQL inventory and migrations | Developed; current DB availability must be verified |
| Configuration backup and deployment module | Developed |
| JWT authentication and RBAC module | Developed |
| Security policy and ACL automation module | Developed |
| Lab 14 orchestration service | Implemented and service-tested |
| Lab 14 simulated API workflow | Tested successfully |
| Full real-handler integration | Incomplete |
| Complete integrated RBAC validation | Not completed |
| Live-device end-to-end validation | Not completed |
| Production readiness | Not established |

## ⚠️ 13. Limitations

- The project has not been validated as a complete production network automation platform.
- Lab 14 uses simulated handlers for its dry-run endpoint.
- The real configuration and ACL automation modules are not fully connected to the integration service.
- Complete authorization enforcement across the final integrated workflow remains unverified.
- PostgreSQL was unavailable during the latest recorded Lab 14 development session.
- Full end-to-end testing against a running GNS3 topology has not been completed.
- Production security hardening, operational monitoring, and performance testing have not been established.

These limitations are documented to distinguish implemented functionality from intended future integration.

## 🔭 14. Possible Future Improvements

If the project is resumed, potential next steps include:

1. Connect the actual Lab 11 backup, deployment, and rollback handlers.
2. Connect the Lab 13 ACL deployment workflow.
3. Verify authorization across integrated endpoints.
4. Restore PostgreSQL availability and validate database-dependent tests.
5. Run end-to-end tests against a controlled GNS3 topology.
6. Improve structured logging and operational monitoring.
7. Add continuous integration for automated tests.
8. Review error handling, secrets management, and deployment security.

These items are future extensions, not completed deliverables.

## 🏁 15. Conclusion

The Network Operations API Platform explores the design of a modular network automation application across fourteen labs.

It combines API development, request validation, network service abstraction, multi-device operational concepts, persistence, configuration lifecycle management, authentication, authorization, security policy processing, and workflow orchestration.

The project demonstrates how individual network engineering responsibilities can be organized into structured software modules, supported by automated tests and layered documentation.

The repository is preserved as a development and portfolio project, with its remaining integration and live-device validation work clearly identified.

---

## 🏷️ GitHub Topics and Tags

```text
network-automation
network-engineering
network-operations
python
fastapi
rest-api
postgresql
sqlalchemy
alembic
netmiko
gns3
network-inventory
configuration-management
configuration-backup
configuration-rollback
jwt-authentication
rbac
network-security
acl-automation
pytest
api-development
```

## 📄 License

The repository contains a root `LICENSE` file. Refer to that file for the applicable license terms before using, modifying, or redistributing the project.

## 👩‍💻 Author

**Saswati Anupama Mathan**
**M.Tech in Electronics & Communication Engineering**
**Specialisation: Communication**

**Project:** Network Operations API Platform
**Domain:** Network Automation and API Engineering
**Primary Language:** Python
**Development Environment:** Ubuntu on WSL
