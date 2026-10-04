# LAB 07 - LIVE NETWORK OPERATIONS

## 1. Objective

Integrate the FastAPI application with real Cisco network devices running in the GNS3 topology using Netmiko.

The objective of this lab is to establish a clean layered architecture:

```text
Client
   ↓
FastAPI Router
   ↓
Network Service
   ↓
Network Adapter
   ↓
Netmiko
   ↓
Cisco IOS Device
   ↓
GNS3
```

The API should be capable of executing a real operational command against a network device and returning the result through an HTTP API.

---

## 2. Environment

### Software

* Ubuntu 24.04.4 on WSL
* Python 3.12.3
* FastAPI 0.141.1
* Uvicorn
* Netmiko 4.7.0
* Paramiko 4.0.0
* GNS3
* Cisco IOS 12.4(25d)

### Project

```text
PROJECT 3 - NETWORK OPERATIONS API PLATFORM
└── PHASE 1 - WEB API & NETWORK OPERATIONS
```

---

## 3. GNS3 Network Topology

The existing GNS3 topology was retained without modification.

| Device  | IP Address     | Platform   |
| ------- | -------------- | ---------- |
| R1      | 192.168.40.10  | Cisco 3745 |
| R2      | 192.168.40.11  | Cisco 3745 |
| R3      | 192.168.40.12  | Cisco 3745 |
| GNS3 VM | 192.168.40.128 | GNS3 VM    |

Cisco IOS:

```text
C3745-ADVENTERPRISEK9-M
Version 12.4(25d)
```

The project also contains an inventory entry for SW1 at `192.168.40.20`, but SW1 is not part of the live GNS3 testing for this lab.

---

## 4. SSH Compatibility Investigation

The Cisco IOS image uses legacy SSH cryptographic algorithms.

Required algorithms include:

```text
Key Exchange:
diffie-hellman-group1-sha1

Host Key:
ssh-rsa

Cipher:
aes128-cbc
```

The initial Project 3 environment used:

```text
Netmiko 4.8.0
Paramiko 5.0.0
```

The connection failed because the installed Paramiko version no longer provided the required legacy Group1 key-exchange implementation.

Investigation confirmed that:

* `diffie-hellman-group1-sha1` was not available in the Paramiko 5.0.0 preferred KEX list.
* `ssh-rsa` was not available in the preferred host-key list.
* `paramiko.kex_group1` was unavailable.
* `aes128-cbc` was present.

The system OpenSSH client could connect when the required legacy algorithms were explicitly enabled.

The previously working network-automation environment used:

```text
Netmiko 4.7.0
Paramiko 4.0.0
```

Project 3 was therefore aligned with the proven compatible dependency versions:

```text
Netmiko 4.7.0
Paramiko 4.0.0
```

A direct Netmiko test subsequently succeeded against R1.

---

## 5. Layered Application Architecture

The network functionality was separated into multiple application layers.

### Router Layer

File:

```text
app/routers/network.py
```

Responsibilities:

* Define HTTP endpoints.
* Receive request parameters.
* Call the network service.
* Translate application/network exceptions into HTTP responses.
* Avoid direct Netmiko usage.

Endpoint:

```text
GET /network/devices/{host}/health
```

---

### Service Layer

File:

```text
app/services/network_service.py
```

Responsibilities:

* Implement network-operation business logic.
* Request operational information from the adapter.
* Translate low-level network failures into application-level exceptions.
* Return structured information to the API layer.

The initial health operation uses:

```text
show version
```

---

### Network Adapter Layer

File:

```text
app/network/netmiko_adapter.py
```

Responsibilities:

* Establish the Netmiko connection.
* Execute the network command.
* Disconnect from the device.
* Convert Netmiko connection failures into project-specific exceptions.

This keeps the Netmiko implementation isolated from FastAPI.

---

### Exception Layer

File:

```text
app/network/exceptions.py
```

Defined exceptions:

```text
NetworkOperationError
NetworkConnectionError
NetworkCommandError
```

The hierarchy allows low-level failures to be translated into meaningful application-level errors.

---

### Schema Layer

File:

```text
app/schemas/network.py
```

Response model:

```text
DeviceHealthResponse
```

Returned fields:

```text
host
reachable
raw_output
```

---

### Configuration Layer

File:

```text
app/config.py
```

Network credentials are loaded from environment variables:

```text
NETWORK_USERNAME
NETWORK_PASSWORD
```

The password is not hard-coded into the application source.

The application intentionally raises an error if `NETWORK_PASSWORD` is not configured.

---

## 6. Live Network Operation

The adapter connects to the Cisco device and executes:

```text
show version
```

A successful API request:

```text
GET /network/devices/192.168.40.10/health
```

returned:

```json
{
  "host": "192.168.40.10",
  "reachable": true,
  "raw_output": "Cisco IOS Software..."
}
```

The returned data contained real information from R1, including:

```text
Cisco IOS Software
C3745-ADVENTERPRISEK9-M
Version 12.4(25d)
R1 uptime
Cisco 3745 processor information
FastEthernet interfaces
Serial interfaces
```

This confirmed that the API was communicating with the real GNS3 Cisco router rather than returning mocked data.

---

## 7. Error Handling

Network failures are deliberately prevented from leaking raw Netmiko exceptions directly to the API client.

The flow is:

```text
Netmiko Failure
      ↓
NetworkConnectionError
      ↓
NetworkOperationError
      ↓
FastAPI HTTPException
      ↓
HTTP 502 Bad Gateway
```

An unreachable device was tested using:

```text
192.168.40.99
```

The API correctly returned:

```text
HTTP/1.1 502 Bad Gateway
```

with:

```json
{
  "detail": {
    "message": "Network device is unreachable",
    "host": "192.168.40.99",
    "operation": "connect"
  }
}
```

This establishes a clean boundary between network-layer failures and HTTP-layer responses.

---

## 8. Validation Performed

### Python Syntax Validation

The following modules were syntax-checked:

```text
app/main.py
app/config.py
app/network/exceptions.py
app/network/netmiko_adapter.py
app/services/network_service.py
app/schemas/network.py
app/routers/network.py
```

### Application Health

```text
GET /health
```

returned:

```json
{
  "status": "healthy"
}
```

### Successful Network Operation

```text
GET /network/devices/192.168.40.10/health
```

Result:

```text
200 OK
```

and real Cisco IOS output was returned.

### Network Failure

```text
GET /network/devices/192.168.40.99/health
```

Result:

```text
502 Bad Gateway
```

with structured error information.

---

## 9. Key Engineering Concepts Learned

### Separation of Concerns

FastAPI should not directly contain Netmiko connection logic.

Instead:

```text
Router → Service → Adapter → Network Device
```

### Adapter Pattern

The Netmiko adapter isolates the network library from the rest of the application.

This makes it possible to replace or extend the network implementation later without rewriting the API routes.

### Exception Translation

Different application layers should expose errors appropriate to their abstraction level.

```text
Netmiko exception
        ↓
Project network exception
        ↓
HTTP error
```

### Environment-Based Configuration

Credentials should be supplied through configuration/environment variables rather than being embedded in source code.

### Real Network Integration

The application has moved from a simulated/in-memory API toward an actual network automation platform capable of communicating with Cisco infrastructure.

---

## 10. Current Project Structure

Relevant Lab 07 components:

```text
app/
├── config.py
├── main.py
├── network/
│   ├── exceptions.py
│   └── netmiko_adapter.py
├── routers/
│   └── network.py
├── schemas/
│   └── network.py
└── services/
    └── network_service.py
```

---

## 11. Architecture Status

Lab 07 establishes the first working version of the live network-operation architecture.

Current capability:

```text
FastAPI
   ↓
Network Router
   ↓
Network Service
   ↓
Netmiko Adapter
   ↓
Cisco IOS
```

The architecture is intentionally designed so that future labs can add:

* Multi-device operations
* Structured command execution
* Interface information
* Configuration retrieval
* Configuration changes
* Job execution
* Audit history
* PostgreSQL persistence
* Authentication and authorization
* Configuration backup
* Configuration diff
* Rollback
* ACL management
* Docker deployment
* Logging and metrics

---

## 12. Lab 07 Completion Criteria

* [x] Connect FastAPI to real GNS3 infrastructure
* [x] Integrate Netmiko
* [x] Resolve Netmiko/Paramiko compatibility issue
* [x] Create network adapter layer
* [x] Create network service layer
* [x] Create network router
* [x] Create network response schema
* [x] Create custom network exceptions
* [x] Move credentials to environment configuration
* [x] Execute real `show version`
* [x] Validate successful device operation
* [x] Validate unreachable-device handling
* [x] Return HTTP 502 for network connection failure
* [x] Verify end-to-end API operation

---

## 13. Next Lab

### LAB 08 - NETWORK SERVICE & ADAPTER ARCHITECTURE

The next stage will strengthen the architecture created here.

Planned improvements include:

* Cleaner FastAPI dependency injection
* Reusable network-service dependencies
* Better device abstraction
* Structured command execution
* More robust exception handling
* Separation of device-specific logic
* Preparation for multi-device operations

The objective is to evolve the application from a single live health endpoint into a reusable network automation service layer.
