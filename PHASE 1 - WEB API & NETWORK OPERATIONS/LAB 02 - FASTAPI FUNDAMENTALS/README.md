# Lab 02 — FastAPI Fundamentals

> **Project:** Network Operations API Platform
> **Phase:** 1 — Web API & Network Operations
> **Lab:** 02 — FastAPI Fundamentals

---

## 🎯 Objective

This lab establishes the **FastAPI API layer** required for the Network Operations API Platform.

The implementation uses an **in-memory network-device inventory** to demonstrate how FastAPI handles:

* **Path parameters**
* **Query parameters**
* **Resource filtering**
* **Pydantic response models**
* **HTTP exception handling**
* **Endpoint metadata and tags**
* **OpenAPI schema generation**
* **Swagger UI documentation**

> **Scope:** This is a FastAPI fundamentals and API-contract demonstration. Database persistence, authentication, and real network-device automation are intentionally introduced in later labs.

---

## 🧠 Engineering Context

A network operations platform requires a well-defined **API contract** before integrating persistent storage and network-device automation.

The API layer must be able to:

1. Identify a specific network device.
2. Return structured device information.
3. Retrieve a collection of devices.
4. Filter devices using operational attributes.
5. Return appropriate HTTP responses for invalid resource requests.
6. Define structured response schemas.
7. Expose a machine-readable **OpenAPI specification**.
8. Provide interactive API documentation for engineers and API consumers.

This lab establishes those fundamentals using a simplified network-device inventory.

---

## 🛠️ Technologies Used

| Technology          | Purpose                            |
| ------------------- | ---------------------------------- |
| **Python 3.12.3**   | Application development            |
| **FastAPI 0.141.1** | REST API framework                 |
| **Uvicorn**         | ASGI application server            |
| **Pydantic**        | Data and response modelling        |
| **OpenAPI**         | Machine-readable API specification |
| **Swagger UI**      | Interactive API documentation      |
| **WSL2 Ubuntu**     | Development environment            |
| **VS Code**         | Source-code development            |

---

## 🌐 Network Device Data Model

The lab uses an in-memory inventory containing four representative network devices.

| Device ID | Hostname     | Device Type | Management IP   | Status     |
| --------- | ------------ | ----------- | --------------- | ---------- |
| `R1`      | `CORE-R1`    | `router`    | `192.168.40.10` | `active`   |
| `R2`      | `CORE-R2`    | `router`    | `192.168.40.11` | `active`   |
| `R3`      | `CORE-R3`    | `router`    | `192.168.40.12` | `inactive` |
| `SW1`     | `ACCESS-SW1` | `switch`    | `192.168.40.20` | `active`   |

The inventory is intentionally stored **in memory** for this lab.

> **PostgreSQL persistence is introduced later in Phase 1.**

---

# 🔌 API Endpoints

## System Endpoints

### `GET /`

Returns the availability message of the API.

```text
GET /
```

---

### `GET /health`

Provides a basic API health response.

```text
GET /health
```

---

# 📡 Device Endpoints

## `GET /devices/{device_id}`

Retrieves information for a specific network device.

### Example Request

```text
GET /devices/R1
```

### Example Response

```json
{
  "device_id": "R1",
  "hostname": "CORE-R1",
  "device_type": "router",
  "management_ip": "192.168.40.10",
  "status": "active"
}
```

The `device_id` is supplied as a **path parameter**.

The implementation also supports **case-insensitive device lookup**.

For example:

```text
/devices/R1
/devices/r1
```

both resolve to the same device.

---

## `GET /devices`

Retrieves the complete network-device inventory.

```text
GET /devices
```

The endpoint also supports optional **query parameters** for inventory filtering.

---

# 🔎 Query Parameter Filtering

## Filter by Device Type

```text
GET /devices?device_type=router
```

Returns only devices whose `device_type` matches `router`.

---

## Filter by Operational Status

```text
GET /devices?status=active
```

Returns only devices whose operational status is `active`.

---

## Combined Filtering

Multiple query parameters can be supplied in the same request.

```text
GET /devices?device_type=router&status=active
```

This applies both filtering conditions and returns only devices satisfying both criteria.

For the current inventory, the result contains:

```text
R1
R2
```

---

# 📦 Pydantic Response Model

The API defines a structured `DeviceResponse` model:

```python
class DeviceResponse(BaseModel):
    device_id: str
    hostname: str
    device_type: str
    management_ip: str
    status: str
```

The model is used through FastAPI's `response_model` mechanism.

```python
response_model=DeviceResponse
```

For the collection endpoint:

```python
response_model=list[DeviceResponse]
```

### Why this matters

The response model establishes a defined **API response contract**.

It also allows FastAPI to automatically expose the schema through **OpenAPI** and **Swagger UI**.

---

# ⚠️ HTTP Error Handling

A request for a device that does not exist returns:

```text
HTTP 404 Not Found
```

### Example

```text
GET /devices/R99
```

### Response

```json
{
  "detail": "Device 'R99' not found"
}
```

The implementation explicitly raises an HTTP exception:

```python
raise HTTPException(
    status_code=404,
    detail=f"Device '{device_id}' not found"
)
```

This demonstrates resource-oriented HTTP error handling instead of returning an ambiguous empty response.

---

# 🏷️ API Organization and Metadata

FastAPI endpoint metadata is used to organize the generated documentation.

The API currently uses two tags:

* **System**
* **Devices**

Endpoints also contain descriptive summaries such as:

```text
API health check
Get network device information
List and filter network devices
```

This improves the readability of the generated API documentation.

---

# 📖 OpenAPI & Swagger UI

FastAPI automatically generates an **OpenAPI specification** from the application definitions.

### Swagger UI

```text
http://127.0.0.1:8000/docs
```

Swagger UI provides an interactive interface for exploring and executing the API endpoints.

### OpenAPI Specification

```text
http://127.0.0.1:8000/openapi.json
```

The generated specification contains information about:

* API endpoints
* Path parameters
* Query parameters
* Response models
* Endpoint metadata
* Tags
* Data schemas

This demonstrates that the API implementation and its documentation are derived from the same application definition.

---

# 🧪 Testing & Verification

The following API operations were tested during the lab:

| Test                              | Expected Behaviour        | Result   |
| --------------------------------- | ------------------------- | -------- |
| `GET /devices/R1`                 | Return R1 information     | ✅ Passed |
| `GET /devices/r1`                 | Case-insensitive lookup   | ✅ Passed |
| `GET /devices/R99`                | Return HTTP 404           | ✅ Passed |
| `GET /devices`                    | Return complete inventory | ✅ Passed |
| `GET /devices?device_type=router` | Return routers            | ✅ Passed |
| `GET /devices?status=active`      | Return active devices     | ✅ Passed |
| Combined device/status filtering  | Apply both conditions     | ✅ Passed |
| Swagger UI verification           | Display API contract      | ✅ Passed |
| OpenAPI schema verification       | Display generated schemas | ✅ Passed |

---

# 💡 Key FastAPI Concepts Demonstrated

### 1. Path Parameters

```python
@app.get("/devices/{device_id}")
```

Used to identify an individual network resource.

### 2. Query Parameters

```python
device_type: str | None
status: str | None
```

Used to modify or filter collection requests.

### 3. Response Models

```python
response_model=DeviceResponse
```

Used to define the expected response structure.

### 4. HTTP Exceptions

```python
HTTPException(status_code=404)
```

Used to return explicit HTTP error responses.

### 5. API Metadata

Tags and summaries organize the API and improve generated documentation.

### 6. OpenAPI Generation

FastAPI automatically generates a machine-readable API contract from the application definitions.

---

# 📁 Project Structure

```text
LAB 02 - FASTAPI FUNDAMENTALS/
│
├── screenshots/
│   ├── 1.png
│   ├── 2.png
│   ├── ...
│   └── 35.png
│
├── outputs/
│   └── .gitkeep
│
└── README.md
```

The `screenshots/` directory contains the **API testing and verification evidence** collected during the lab.

The `outputs/` directory is retained for generated artifacts that may be required by future labs. No separate output artifact is required for this demonstration lab.

---

# 🔗 Engineering Relevance

The concepts demonstrated here form the API foundation for the subsequent Network Operations Platform.

The progression is:

```text
FastAPI Fundamentals
        ↓
REST API Design
        ↓
PostgreSQL Persistence
        ↓
SQLAlchemy ORM
        ↓
Database Migrations
        ↓
Authentication & Authorization
        ↓
Network Device Communication
        ↓
Network Automation Workflows
        ↓
Integrated Network Operations Platform
```

The simplified in-memory inventory used here will eventually evolve into APIs backed by persistent network-device data and real network operations.

---

# ✅ Outcome

**Lab 02 successfully established the fundamental FastAPI API-contract concepts required for the Network Operations API Platform.**

The lab demonstrated:

* **Structured network-device resources**
* **Typed path parameters**
* **Query-based filtering**
* **Pydantic response modelling**
* **HTTP 404 handling**
* **API metadata and organization**
* **Automatic OpenAPI generation**
* **Interactive Swagger documentation**

These concepts provide the foundation for the more advanced REST, database, authentication, and network-automation capabilities developed in the subsequent labs.
