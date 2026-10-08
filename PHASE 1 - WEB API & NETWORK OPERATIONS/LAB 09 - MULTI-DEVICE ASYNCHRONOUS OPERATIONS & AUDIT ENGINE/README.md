# 🚀 LAB 09 — MULTI-DEVICE ASYNCHRONOUS OPERATIONS & AUDIT ENGINE

> **Advanced MTech-Level Network Automation & Operations Platform**
>
> Multi-device execution • Concurrent operations • Async jobs • Failure isolation • Operation tracking • Audit trail

---

# 📌 1. OBJECTIVE

This lab extends the existing **Network Operations API Platform** from single-device network execution into a **multi-device asynchronous operations engine**.

The implementation introduces a structured execution architecture capable of:

- ✅ Multi-device network operations
- ✅ Concurrent execution across multiple devices
- ✅ Unique `operation_id` and `job_id`
- ✅ Per-device execution status
- ✅ Per-device success/failure reporting
- ✅ Independent device failure isolation
- ✅ Partial-success aggregation
- ✅ Asynchronous background jobs
- ✅ Job lifecycle tracking
- ✅ Execution timestamps
- ✅ Execution duration measurement
- ✅ Operation result aggregation
- ✅ Audit trail generation
- ✅ Thread-safe in-memory job and audit stores
- ✅ Real execution against the existing GNS3 Cisco topology

The objective is to move the platform beyond basic REST endpoints into an **operations-oriented network automation backend**.

---

# 🌐 2. EXISTING NETWORK ENVIRONMENT

The lab uses the **existing GNS3 topology** without modifying the established network environment.

| Device | Management IP | Platform | IOS |
|---|---|---|---|
| **R1** | `192.168.40.10` | Cisco 3745 | `12.4(25d)` |
| **R2** | `192.168.40.11` | Cisco 3745 | `12.4(25d)` |
| **R3** | `192.168.40.12` | Cisco 3745 | `12.4(25d)` |

### Technology Stack

| Component | Technology |
|---|---|
| API Framework | **FastAPI** |
| Language | **Python 3.12** |
| Network Automation | **Netmiko** |
| Transport | **SSH** |
| Network Simulator | **GNS3** |
| Router Platform | **Cisco 3745** |
| Concurrency | **ThreadPoolExecutor** |
| State Management | **Thread-safe in-memory stores** |
| API Documentation | **OpenAPI / Swagger UI** |

---

# 🏗️ 3. SYSTEM ARCHITECTURE

    Client
      │
      ▼
    FastAPI Routers
      │
      ├── /operations
      ├── /jobs
      └── /audit
             │
             ▼
    ┌──────────────────────┐
    │   OperationService   │
    │ Multi-device         │
    │ orchestration        │
    └──────────┬───────────┘
               │
               ▼
    ┌──────────────────────┐
    │      JobManager      │
    │ Background execution │
    │ Job lifecycle        │
    └──────────┬───────────┘
               │
               ▼
    ┌──────────────────────┐
    │    NetworkService    │
    │       Lab 08         │
    └──────────┬───────────┘
               │
               ▼
    ┌──────────────────────┐
    │    NetmikoAdapter    │
    └──────────┬───────────┘
               │
               ▼
    ┌──────────────────────┐
    │  NetworkConnection   │
    └──────────┬───────────┘
               │
               ▼
             Netmiko
               │
       ┌───────┼───────┐
       ▼       ▼       ▼
      R1      R2      R3
    .40.10  .40.11  .40.12
       │       │       │
       └───────┼───────┘
               ▼
        OperationResult
               │
               ▼
        AuditService
               │
               ▼
          AuditStore

---

# ⚙️ 4. SUPPORTED OPERATIONS

The multi-device engine currently supports four controlled network operations.

| Operation | Network Action |
|---|---|
| `collect_health` | Device reachability / health verification |
| `collect_interfaces` | `show ip interface brief` |
| `collect_routes` | `show ip route` |
| `collect_version` | `show version` |

The operation type is represented through a controlled enumeration rather than exposing unrestricted command execution through the multi-device API.

---

# 🚀 5. MULTI-DEVICE OPERATION MODEL

A single operation can target multiple network devices.

### Example Request

    {
      "operation": "collect_version",
      "targets": [
        "192.168.40.10",
        "192.168.40.11",
        "192.168.40.12"
      ],
      "requested_by": "admin"
    }

The request is converted into an internal `OperationResult`.

Each operation receives a unique:

    operation_id

The operation records:

- Operation type
- Requesting user
- Target devices
- Creation timestamp
- Start timestamp
- Completion timestamp
- Total execution duration
- Per-device results
- Successful device count
- Failed device count
- Aggregate status

---

# 🔄 6. CONCURRENT EXECUTION

Multi-device operations are executed concurrently using a bounded:

    ThreadPoolExecutor

with a maximum worker count of:

    3

This matches the three-device GNS3 topology:

    R1 ─────┐
            │
    R2 ─────┼──► Concurrent execution
            │
    R3 ─────┘

Instead of executing:

    R1 → wait → R2 → wait → R3

the engine performs:

              ┌──► R1
              │
    Operation ├──► R2
              │
              └──► R3

The aggregate execution time therefore approaches the duration of the slowest participating device rather than the sum of all device execution times.

---

# 🧩 7. PER-DEVICE EXECUTION MODEL

Every target device receives its own execution result.

Possible device states are:

    pending
    running
    success
    failed
    timeout

Each device result can contain:

- Host
- Status
- Start timestamp
- Completion timestamp
- Duration
- Command output
- Error type
- Error message

This provides detailed visibility into individual device execution.

---

# 🛡️ 8. FAILURE ISOLATION

A failure on one device does **not** terminate the complete multi-device operation.

For example:

    R1 → SUCCESS
    R2 → FAILED
    R3 → SUCCESS

produces:

    Operation Status   : completed_with_errors
    Total Devices      : 3
    Successful Devices : 2
    Failed Devices     : 1

This behaviour is important for real network automation environments because individual devices can fail due to:

- Connectivity problems
- SSH failures
- Device unavailability
- Command failures
- Timeouts

The remaining devices can continue executing independently.

---

# 📊 9. AGGREGATE OPERATION STATUS

The operation engine derives an aggregate status from the individual device results.

### Complete Success

    R1 → SUCCESS
    R2 → SUCCESS
    R3 → SUCCESS

    Status = completed

### Partial Failure

    R1 → SUCCESS
    R2 → FAILED
    R3 → SUCCESS

    Status = completed_with_errors

### Complete Failure

    R1 → FAILED
    R2 → FAILED
    R3 → FAILED

    Status = failed

This provides a clear distinction between:

> **Total failure** and **partial operational failure**.

---

# 🆔 10. OPERATION IDENTIFICATION

Every operation receives a unique UUID:

    operation_id

This identifier is propagated through the execution pipeline.

The same identifier can therefore connect:

    API Request
         ↓
    Operation
         ↓
    Job
         ↓
    Operation Result
         ↓
    Audit Record

This provides traceability across the complete execution lifecycle.

---

# ⏳ 11. ASYNCHRONOUS JOB ENGINE

The `/jobs` API separates job submission from network execution.

### Submit Job

    POST /jobs

The API immediately creates:

    job_id
    operation_id

and returns:

    HTTP 202 Accepted

The actual network operation then executes in the background.

---

# 🔄 12. JOB LIFECYCLE

The asynchronous job follows the lifecycle:

              ┌─────────┐
              │ QUEUED  │
              └────┬────┘
                   │
                   ▼
              ┌─────────┐
              │ RUNNING │
              └────┬────┘
                   │
          ┌────────┼─────────┐
          │        │         │
          ▼        ▼         ▼
     COMPLETED   COMPLETED   FAILED
                 WITH_ERRORS

### Job States

    queued
    running
    completed
    completed_with_errors
    failed

The job response contains the final aggregated operation result once execution finishes.

---

# 🔍 13. JOB TRACKING

### Submit

    POST /jobs

### Retrieve

    GET /jobs/{job_id}

The job response provides:

- `job_id`
- `operation_id`
- Current job status
- Creation timestamp
- Start timestamp
- Completion timestamp
- Error information
- Final operation result

The important relationship is:

    job_id
       │
       └──────► operation_id
                      │
                      └──────► OperationResult

---

# 🧾 14. AUDIT ENGINE

Every executed operation is recorded through the shared:

    AuditService

The audit layer captures the essential operational dimensions:

| Dimension | Information |
|---|---|
| **WHO** | `requested_by` |
| **WHAT** | Operation type |
| **WHEN** | Creation / start / completion timestamps |
| **WHERE** | Target device IP addresses |
| **RESULT** | Aggregate operation status |
| **DURATION** | Total execution duration |

---

# 🔎 15. AUDIT API

### Retrieve Audit Record

    GET /audit/{operation_id}

Example audit information:

    operation_id : 75a1673e-4762-4c4f-8c27-44102737c42b
    requested_by : admin
    operation    : collect_version
    target_count : 3
    status       : completed
    duration_ms  : 2456.58

The audit record provides an independent operational history for the executed network action.

---

# 🔐 16. THREAD SAFETY

Because network operations and asynchronous jobs execute concurrently, shared state must be protected.

Both:

    JobStore
    AuditStore

use thread locking.

The stores therefore protect their internal dictionaries during:

    create
    get
    update
    add
    list

operations.

This avoids basic race conditions when:

- Background jobs update state
- API requests read job state
- Multiple operations execute concurrently
- Audit records are created from worker threads

---

# 🌐 17. API ENDPOINTS

## Synchronous Multi-Device Operation

    POST /operations

Executes a multi-device operation and returns the aggregate result.

## Asynchronous Operation Submission

    POST /jobs

Creates an asynchronous network operation.

Returns:

    HTTP 202 Accepted

## Job Status / Result

    GET /jobs/{job_id}

Retrieves job lifecycle state and final operation results.

## Audit Record

    GET /audit/{operation_id}

Retrieves the audit record associated with an operation.

---

# 🧪 18. VERIFIED LIVE EXECUTION

The implementation was tested against the **live GNS3 Cisco 3745 topology**.

The tests were not mock-only API tests.

Real Netmiko SSH connections were established to:

    R1 → 192.168.40.10
    R2 → 192.168.40.11
    R3 → 192.168.40.12

---

# ✅ 19. VERIFIED MULTI-DEVICE SYNCHRONOUS EXECUTION

The `collect_version` operation was executed against:

    192.168.40.10
    192.168.40.11
    192.168.40.12

All three devices successfully returned real:

    show version

output.

Concurrent execution was observed, with the aggregate duration remaining close to the slowest individual device execution.

---

# ✅ 20. VERIFIED ASYNCHRONOUS EXECUTION

A complete asynchronous `collect_version` job was verified.

### Job ID

    cb7aad26-1662-4099-9e33-d921998cd9e4

### Operation ID

    75a1673e-4762-4c4f-8c27-44102737c42b

### Result

    Status             : completed
    Total Devices      : 3
    Successful Devices : 3
    Failed Devices     : 0
    Duration           : approximately 2456.58 ms

Real network output was collected from:

    R1
    R2
    R3

---

# ⚠️ 21. VERIFIED PARTIAL FAILURE

Failure isolation was tested using:

    192.168.40.10
    192.168.40.99
    192.168.40.12

where:

    192.168.40.99

was intentionally unreachable.

### Job ID

    02c1c108-c1a4-4189-bd22-53715e5a0416

### Operation ID

    3322ec5b-5632-471b-bc04-010c3922fa44

### Result

    Status             : completed_with_errors
    Total Devices      : 3
    Successful Devices : 2
    Failed Devices     : 1

The invalid device generated a structured:

    NetworkConnectionError

while R1 and R3 completed successfully.

This demonstrates **independent device failure isolation**.

---

# 🧾 22. VERIFIED AUDIT RECORD

The final audit verification used:

    Operation ID:
    75a1673e-4762-4c4f-8c27-44102737c42b

The returned audit record confirmed:

    requested_by : admin
    operation    : collect_version
    target_count : 3
    status       : completed
    duration_ms  : 2456.58

It also contained:

    created_at
    started_at
    completed_at

demonstrating that the operation lifecycle is traceable through the audit layer.

---

# 🗂️ 23. PROJECT STRUCTURE

    LAB 09 - MULTI-DEVICE ASYNCHRONOUS OPERATIONS & AUDIT ENGINE/
    │
    ├── README.md
    │
    └── screenshots/
        ├── 1.png
        ├── 2.png
        ├── 3.png
        ├── ...
        └── 84.png

### Application Structure

    app/
    │
    ├── audit/
    │   ├── models.py
    │   ├── router.py
    │   ├── schemas.py
    │   └── service.py
    │
    ├── jobs/
    │   ├── manager.py
    │   ├── models.py
    │   └── schemas.py
    │
    ├── operations/
    │   ├── models.py
    │   ├── schemas.py
    │   └── service.py
    │
    ├── routers/
    │   ├── jobs.py
    │   ├── network.py
    │   └── operations.py
    │
    ├── services/
    │   └── network_service.py
    │
    ├── main.py
    ├── config.py
    └── dependencies.py

---

# 🧠 24. CORE DESIGN COMPONENTS

## Operation Models

Responsible for representing:

- Operation type
- Operation status
- Per-device status
- Device results
- Aggregate results

## Operation Service

Responsible for:

- Generating operation IDs
- Executing operations
- Concurrent device execution
- Collecting results
- Calculating aggregate status
- Measuring execution duration
- Sending completed operations to the audit layer

## Job Manager

Responsible for:

- Job creation
- Background execution
- Job lifecycle
- Job-to-operation mapping
- Final operation result attachment

## Job Store

Provides thread-safe temporary storage for active jobs.

## Audit Service

Responsible for converting operation results into audit records.

## Audit Store

Provides thread-safe temporary storage for audit records.

---

# 🧱 25. ARCHITECTURAL LAYERS

The final Lab 09 execution path is:

    Operation Router
           ↓
    Operation Service
           ↓
    Job / Execution Engine
           ↓
    Network Service
           ↓
    Netmiko Adapter
           ↓
    Network Connection
           ↓
    Netmiko
           ↓
    GNS3 Cisco Router

The audit path is:

    Operation Result
           ↓
    Audit Service
           ↓
    Audit Store
           ↓
    GET /audit/{operation_id}

This maintains the separation introduced in **Lab 08** instead of placing Netmiko logic directly inside FastAPI route handlers.

---

# 🛡️ 26. VALIDATION & ERROR HANDLING

The API uses Pydantic request and response schemas together with controlled operation types.

Network exceptions are converted into structured per-device results.

Examples include:

    Connection failure
    Device unreachable
    Command execution failure
    Timeout
    Partial operation failure

Instead of exposing raw Python exceptions, the API returns machine-readable operational information.

---

# 📈 27. WHY THIS DESIGN IS IMPORTANT

Lab 09 represents the transition from:

    Simple Network API

to:

    Network Operations Engine

The implementation demonstrates:

1. **Multi-device orchestration**
2. **Concurrent execution**
3. **Failure isolation**
4. **Aggregate result modelling**
5. **Asynchronous job execution**
6. **Job lifecycle management**
7. **Operation identity**
8. **Execution timing**
9. **Thread-safe state management**
10. **Operational auditability**

These are foundational concepts for larger network automation and infrastructure operations platforms.

---

# 💼 28. RESUME-LEVEL ENGINEERING VALUE

This lab demonstrates practical backend and network automation capabilities including:

    FastAPI
       +
    Network Automation
       +
    Netmiko
       +
    Concurrent Execution
       +
    Async Job Processing
       +
    Failure Isolation
       +
    Operational State Tracking
       +
    Auditability

The project therefore demonstrates more than simply sending commands to routers.

It implements an **execution and orchestration layer** capable of coordinating operations across multiple network devices.

---

# ⚠️ 29. CURRENT LIMITATION

The current implementation uses:

    In-memory JobStore
    In-memory AuditStore

Therefore:

- Job records are lost when the FastAPI process restarts.
- Audit records are lost when the FastAPI process restarts.
- The current implementation is process-local.
- Long-term historical persistence is not yet implemented.

This is an intentional architectural stage rather than an accidental omission.

---

# 🗄️ 30. FUTURE PERSISTENCE LAYER

PostgreSQL persistence will be introduced in a later phase.

The future architecture can replace:

    JobStore
    AuditStore

with:

    PostgreSQL
         │
         ├── Operations
         ├── Jobs
         ├── Device Results
         └── Audit Records

without requiring the fundamental operation orchestration model to be redesigned.

---

# 🔮 31. FUTURE EXTENSIONS

The architecture established here provides a foundation for:

- PostgreSQL-backed persistent jobs
- Persistent audit history
- JWT authentication
- RBAC
- Scheduled operations
- Retry policies
- Configurable timeouts
- Job cancellation
- Job prioritization
- Historical execution queries
- Observability
- Metrics
- Structured logging
- Distributed workers
- Event-driven execution

These features can be added as subsequent phases without collapsing the existing service boundaries.

---

# 📸 32. EVIDENCE SCREENSHOTS

The Lab 09 evidence directory contains:

    84 screenshots

The screenshots document the implementation, API execution, asynchronous jobs, multi-device results, failure handling, audit verification and supporting development evidence.

All captured evidence has been retained without manual segregation or deletion.

---

# 🧪 33. FINAL LAB VERIFICATION

| Capability | Status |
|---|---|
| Multi-device operations | ✅ VERIFIED |
| R1/R2/R3 concurrent execution | ✅ VERIFIED |
| Operation IDs | ✅ VERIFIED |
| Job IDs | ✅ VERIFIED |
| Job lifecycle | ✅ VERIFIED |
| Per-device results | ✅ VERIFIED |
| Successful execution | ✅ VERIFIED |
| Partial failure | ✅ VERIFIED |
| Failure isolation | ✅ VERIFIED |
| Aggregate status | ✅ VERIFIED |
| Execution duration | ✅ VERIFIED |
| Audit record generation | ✅ VERIFIED |
| Audit retrieval | ✅ VERIFIED |
| Thread-safe job store | ✅ IMPLEMENTED |
| Thread-safe audit store | ✅ IMPLEMENTED |
| Live GNS3 execution | ✅ VERIFIED |
| Real Netmiko SSH execution | ✅ VERIFIED |

---

# 🏁 34. LAB OUTCOME

Lab 09 successfully transforms the existing Network Service Layer into a:

> **Multi-Device Asynchronous Network Operations & Audit Engine**

The completed execution pipeline is:

                       CLIENT
                         │
                         ▼
                  FASTAPI API LAYER
                         │
              ┌──────────┴──────────┐
              │                     │
              ▼                     ▼
         OPERATIONS              ASYNC JOBS
              │                     │
              └──────────┬──────────┘
                         ▼
                 OPERATION ENGINE
                         │
                         ▼
              CONCURRENT EXECUTION
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
             R1         R2         R3
              │          │          │
              └──────────┼──────────┘
                         ▼
                  AGGREGATED RESULT
                         │
                         ▼
                   AUDIT SERVICE
                         │
                         ▼
                    AUDIT RECORD

The lab therefore establishes the core execution architecture required for a more advanced, persistent and secure **Network Operations API Platform**.

---

# 🎯 FINAL STATUS

    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║   LAB 09 — MULTI-DEVICE ASYNCHRONOUS OPERATIONS         ║
    ║             & AUDIT ENGINE                              ║
    ║                                                          ║
    ║   STATUS: ✅ COMPLETED                                  ║
    ║                                                          ║
    ║   Devices Tested       : R1 / R2 / R3                  ║
    ║   Concurrent Execution : ✅                             ║
    ║   Async Jobs           : ✅                             ║
    ║   Failure Isolation    : ✅                             ║
    ║   Partial Failure      : ✅                             ║
    ║   Operation Tracking   : ✅                             ║
    ║   Audit Trail          : ✅                             ║
    ║   Live GNS3 Testing    : ✅                             ║
    ║   Evidence Screenshots: 84                              ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝

**Lab 09 complete.**
