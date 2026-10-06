# LAB 08 — NETWORK OPERATIONS SERVICE LAYER

## 1. Objective

The objective of this lab is to introduce a dedicated **Service Layer** into the Network Operations API.

The Service Layer separates:

- **HTTP/API handling**
- **Network operation logic**
- **Netmiko device communication**
- **Network result representation**

This creates a cleaner and more scalable architecture for the Network Operations API.

---

## 2. Lab Architecture

The request flow implemented in this lab is:

    Client
       │
       ▼
    FastAPI Router
       │
       ▼
    Dependency Provider
       │
       ▼
    NetworkService
       │
       ▼
    NetmikoAdapter
       │
       ▼
    NetworkConnection
       │
       ▼
    Netmiko
       │
       ▼
    GNS3 Cisco Router

The Service Layer acts as the application-level abstraction between the FastAPI router and the network automation layer.

---

## 3. Existing Environment

This lab continues using the existing network automation environment.

### GNS3 Topology

    R1 ───── R2 ───── R3

    R1 = 192.168.40.10
    R2 = 192.168.40.11
    R3 = 192.168.40.12

The existing GNS3 topology was **not modified**.

### Network Device

    Vendor        : Cisco
    Platform      : Cisco IOS
    Device Model  : Cisco 3745
    IOS Version   : 12.4(25d)

### Network Automation

    Netmiko
    Paramiko

The already working Netmiko environment was reused.

---

## 4. Lab Objectives

This lab implements the following:

- Introduce a dedicated **NetworkService**
- Separate business/application logic from the FastAPI router
- Introduce a **dependency provider**
- Introduce a reusable **NetworkConnection**
- Keep Netmiko communication behind an adapter
- Introduce a structured **NetworkResult**
- Centralize network operation handling
- Improve exception propagation
- Preserve the existing live GNS3/Netmiko functionality
- Verify successful and failed network operations through the API

---

## 5. Application Structure

The application was reorganized into the following logical layers:

    app/
    │
    ├── config.py
    │
    ├── dependencies.py
    │
    ├── network/
    │   ├── connection.py
    │   ├── exceptions.py
    │   └── netmiko_adapter.py
    │
    ├── routers/
    │   └── network.py
    │
    ├── schemas/
    │   └── network_result.py
    │
    └── services/
        └── network_service.py

---

## 6. Components Implemented

### 6.1 `app/config.py`

The configuration module centralizes network-related settings.

It contains configuration for:

    NETWORK_USERNAME
    NETWORK_PASSWORD
    NETWORK_CONNECT_TIMEOUT
    NETWORK_COMMAND_TIMEOUT

This avoids scattering configuration values throughout the application.

---

### 6.2 `app/dependencies.py`

The dependency provider creates and exposes the required application components.

The FastAPI router can obtain a configured `NetworkService` without directly constructing the underlying network components.

This improves:

- Dependency injection
- Testability
- Separation of concerns
- Maintainability

---

### 6.3 `app/network/connection.py`

`NetworkConnection` provides the connection-level abstraction for communicating with network devices.

It is responsible for managing the network connection lifecycle while keeping connection details outside the API router.

---

### 6.4 `app/network/netmiko_adapter.py`

`NetmikoAdapter` provides the integration between the application and Netmiko.

Its purpose is to isolate the Netmiko implementation from the rest of the application.

The higher-level service therefore does not need to directly manage Netmiko connection details.

---

### 6.5 `app/routers/network.py`

The FastAPI router is responsible for the HTTP/API layer.

The router receives the request and delegates the actual network operation to `NetworkService`.

The router therefore avoids directly implementing network automation logic.

---

### 6.6 `app/schemas/network_result.py`

`NetworkResult` provides a structured representation of the result returned from a network operation.

This creates a defined application-level result instead of allowing raw network communication details to propagate through every layer.

---

### 6.7 `app/services/network_service.py`

`NetworkService` is the main application/service layer introduced in this lab.

It coordinates the network operation between the FastAPI API layer and the underlying network adapter.

The service layer is responsible for:

    Receiving the network operation request
                ↓
    Using the network connection
                ↓
    Executing the required network operation
                ↓
    Handling network-level errors
                ↓
    Returning a structured result

This makes the service layer the main location for future network-operation business logic.

---

## 7. Exception Handling

Network-specific failures are separated from HTTP-level handling.

The application uses network operation exceptions so that failures can propagate through the architecture cleanly.

Example failure flow:

    Netmiko / Network Failure
              ↓
    Network Exception
              ↓
    NetworkService
              ↓
    FastAPI Router
              ↓
    HTTP 502 Bad Gateway

This prevents network implementation details from being mixed directly into the API layer.

---

## 8. API Endpoint Tested

The existing network health endpoint was used to verify the new architecture.

### Endpoint

    GET /network/devices/{host}/health

### Successful Request

    GET /network/devices/192.168.40.10/health

The request successfully reached the live GNS3 R1 router through the application architecture.

The response contained the router's live `show version` output.

---

## 9. Successful Live Network Test

The successful request demonstrated the complete path:

    Swagger / HTTP Client
            ↓
    FastAPI Router
            ↓
    Dependency Provider
            ↓
    NetworkService
            ↓
    NetmikoAdapter
            ↓
    NetworkConnection
            ↓
    Netmiko
            ↓
    GNS3 R1

The live router response confirmed that the service-layer architecture works with the existing network automation environment.

---

## 10. Invalid Device Test

An invalid device address was also tested.

### Test

    GET /network/devices/192.168.40.99/health

The device does not exist in the current GNS3 topology.

The API correctly returned:

    HTTP 502 Bad Gateway

with a network-operation failure message.

This verified that network failures are correctly propagated through the service architecture and converted into an appropriate API response.

---

## 11. Swagger Verification

The endpoint was tested through the FastAPI Swagger interface.

    http://127.0.0.1:8000/docs

Swagger successfully displayed the network endpoint and allowed the live network operation to be executed.

Both successful and failed network operations were verified.

---

## 12. Validation

The application source was checked using:

    python -m compileall -q app

The command completed successfully without compilation errors.

This confirms that the application Python files are syntactically valid.

---

## 13. Lab Documentation

The Lab 08 documentation directory contains copies of the relevant implementation files for reference.

    LAB 08 - NETWORK OPERATIONS SERVICE LAYER/
    │
    ├── config.py
    ├── connection.py
    ├── dependencies.py
    ├── netmiko_adapter.py
    ├── network_result.py
    ├── network_service.py
    ├── README.md
    │
    └── screenshots/
        ├── 1.png
        ├── 2.png
        ├── 3.png
        ├── ...
        └── 24.png

There are **24 screenshots** documenting the implementation and verification process.

The documentation copies are separate from the actual application source.

The working source remains inside:

    app/

---

## 14. Final Architecture

After Lab 08, the Network Operations API follows a layered architecture:

                         ┌──────────────────────┐
                         │       Client         │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   FastAPI Router     │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Dependency Provider  │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   NetworkService     │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   NetmikoAdapter     │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ NetworkConnection    │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │       Netmiko        │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    GNS3 Cisco R1     │
                         │    192.168.40.10     │
                         └──────────────────────┘

---

## 15. Key Concepts Learned

### Service Layer

Separates application/business logic from the HTTP layer.

### Dependency Injection

Allows application components to be provided to FastAPI routes without tightly coupling object creation to the router.

### Adapter Pattern

Isolates the Netmiko implementation behind an application-specific interface.

### Network Abstraction

Keeps network connection and device communication details outside the API layer.

### Exception Propagation

Allows network failures to move cleanly through the application and become appropriate HTTP responses.

### Layered Architecture

Creates a scalable foundation for adding more network operations without making the FastAPI router increasingly complex.

---

## 16. Lab Outcome

Lab 08 successfully introduced the **Network Operations Service Layer** into the FastAPI application.

The application now separates:

    API Layer
        ↓
    Dependency Layer
        ↓
    Service Layer
        ↓
    Network Adapter
        ↓
    Connection Layer
        ↓
    Netmiko
        ↓
    Network Device

The architecture was verified against the existing live GNS3 Cisco topology.

### Verification Summary

    ✓ Service Layer implemented
    ✓ Dependency Provider implemented
    ✓ NetworkConnection implemented
    ✓ NetmikoAdapter integrated
    ✓ NetworkResult implemented
    ✓ Live R1 operation successful
    ✓ Invalid-device operation returned HTTP 502
    ✓ Swagger verification successful
    ✓ Python compilation successful
    ✓ Existing GNS3 topology preserved
    ✓ Existing Netmiko environment reused
    ✓ 24 documentation screenshots captured

---

# LAB 08 — NETWORK OPERATIONS SERVICE LAYER: COMPLETE
