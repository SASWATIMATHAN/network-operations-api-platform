# Lab 03 — REST API — GET

## Project

**Network Operations API Platform**

## Phase

**Phase 1 — Web API & Network Operations**

---

## Objective

Implement and validate RESTful `GET` operations for retrieving network resources through FastAPI.

This lab extends the device inventory developed in Lab 02 by introducing a nested network resource for retrieving the interfaces associated with a specific network device.

---

## Technologies Used

* Python 3.12.3
* FastAPI
* Uvicorn
* Pydantic
* Swagger UI
* OpenAPI

---

## REST Resources Implemented

### 1. List Devices

```http
GET /devices
```

Retrieves the complete network device inventory.

Supports query parameters:

```http
GET /devices?device_type=router
GET /devices?status=active
GET /devices?device_type=router&status=active
```

---

### 2. Retrieve a Device

```http
GET /devices/{device_id}
```

Example:

```http
GET /devices/R2
```

Device lookup is case-insensitive.

---

### 3. Retrieve Device Interfaces

```http
GET /devices/{device_id}/interfaces
```

Example:

```http
GET /devices/R1/interfaces
```

Returns the interfaces associated with the requested network device.

The interface response contains:

* Interface name
* IPv4 address
* Subnet mask
* Operational status
* Interface description

---

## Response Models

### DeviceResponse

Defines the JSON response structure for network devices.

Fields:

* `device_id`
* `hostname`
* `device_type`
* `management_ip`
* `status`

### InterfaceResponse

Defines the JSON response structure for network interfaces.

Fields:

* `interface_name`
* `ip_address`
* `subnet_mask`
* `status`
* `description`

---

## HTTP Status Codes

### Successful Request

```text
200 OK
```

Returned when the requested network resource is successfully retrieved.

### Resource Not Found

```text
404 Not Found
```

Returned when the requested device does not exist.

Example:

```http
GET /devices/R99/interfaces
```

Response:

```json
{
    "detail": "Device 'R99' not found"
}
```

---

## API Testing

The API was tested using:

### Swagger UI

```text
http://127.0.0.1:8000/docs
```

Swagger UI was used to execute and validate the implemented GET endpoints.

### Browser/API Testing

The following resources were tested:

```text
GET /devices
GET /devices/R2
GET /devices/R1/interfaces
```

Query parameter filtering was also tested:

```text
GET /devices?device_type=router
GET /devices?status=active
GET /devices?device_type=router&status=active
```

Case-insensitive filtering was verified using:

```text
GET /devices?device_type=ROUTER
```

### OpenAPI

The generated API specification was verified at:

```text
http://127.0.0.1:8000/openapi.json
```

The following paths were confirmed:

```text
/devices
/devices/{device_id}
/devices/{device_id}/interfaces
```

---

## Implementation Architecture

```text
Client
   │
   │ HTTP GET
   ▼
FastAPI
   │
   ├── /devices
   │
   ├── /devices/{device_id}
   │
   └── /devices/{device_id}/interfaces
   │
   ▼
Pydantic Response Models
   │
   ▼
JSON Response
```

---

## Current Data Source

The current implementation uses an in-memory Python data structure for development and API testing.

```text
FastAPI
   │
   ▼
In-memory network inventory
   │
   ▼
JSON response
```

The API is not yet retrieving live information from the Cisco/GNS3 topology.

Live network-device integration will be introduced in later stages of the project.

---

## Validation

The following functionality was successfully verified:

* [x] GET collection endpoint
* [x] GET individual resource
* [x] GET nested resource
* [x] Path parameters
* [x] Query parameters
* [x] Combined query filtering
* [x] Case-insensitive filtering
* [x] Pydantic response models
* [x] HTTP 200 response
* [x] HTTP 404 handling
* [x] Swagger UI testing
* [x] Browser/API testing
* [x] OpenAPI specification

---

## Project Structure

```text
LAB 03 - REST API - GET/
├── screenshots/
├── outputs/
└── README.md
```

---

## Outcome

Lab 03 established the RESTful `GET` layer for the Network Operations API.

The API can now retrieve:

```text
Network Devices
      │
      └── Device Interfaces
```

This provides the foundation for subsequent REST operations and the later integration of persistent network data and live network-device operations.
