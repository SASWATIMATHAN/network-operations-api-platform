# Lab 06 — Pydantic Validation

## Objective

Implement and verify request and response data validation in the Network Operations API using **Pydantic models** and FastAPI.

This lab strengthens the API by enforcing structured input, type validation, field constraints, and meaningful validation errors.

---

## Technologies

* Python 3.12.3
* FastAPI
* Pydantic
* Uvicorn
* Ubuntu WSL
* VS Code
* Swagger UI

---

## Validation Features Implemented

### 1. Required Fields

The `DeviceCreate` model requires:

* `device_id`
* `hostname`
* `device_type`
* `management_ip`
* `status`

Missing required fields are rejected with HTTP `422 Unprocessable Entity`.

### 2. Optional Fields

Added an optional device description:

```python
description: str | None = Field(
    default=None,
    description="Optional device description"
)
```

The API therefore accepts device descriptions without requiring them for every device.

### 3. String Constraints

Field constraints were added using Pydantic `Field()`.

Examples:

```python
device_id: str = Field(min_length=2)
```

```python
hostname: str = Field(
    min_length=2,
    max_length=30
)
```

Invalid values are rejected automatically.

### 4. Device Type Validation

The `device_type` field uses `Literal`:

```python
device_type: Literal["router", "switch"]
```

Only supported device types are accepted.

For example:

```text
router
switch
```

An invalid value such as:

```text
firewall
```

produces a validation error.

### 5. IPv4 Address Validation

The management IP field uses Python's `IPv4Address` type:

```python
management_ip: IPv4Address
```

Invalid IPv4 addresses are rejected by Pydantic.

Example invalid value:

```text
not-an-ip
```

### 6. Nested Pydantic Model

A nested validation model was introduced:

```python
class ManagementInfo(BaseModel):
    ip_address: IPv4Address
    description: str | None = None
```

This demonstrates how Pydantic models can be composed into larger structured data models.

### 7. Request Validation

FastAPI automatically validates incoming JSON requests against the Pydantic request model.

Invalid requests return:

```text
HTTP 422 Unprocessable Entity
```

Validation was tested with:

* Short `device_id`
* Short `hostname`
* Invalid `device_type`
* Invalid IPv4 address
* Missing required fields
* Multiple invalid fields in the same request

### 8. Response Model

The API continues to use `DeviceResponse` for structured device responses:

```python
class DeviceResponse(BaseModel):
    device_id: str
    hostname: str
    device_type: str
    management_ip: str
    status: str
```

The response model defines the public structure returned by the API.

### 9. JSON Serialization Compatibility

During validation development, changing `management_ip` from a string to `IPv4Address` exposed a serialization compatibility issue.

The POST operation was updated to use:

```python
device.model_dump(mode="json")
```

This converts Pydantic-managed values into JSON-compatible representations before storing and returning the device data.

---

## Validation Test Results

| Test                    | Expected Result | Result |
| ----------------------- | --------------- | ------ |
| Valid device request    | `201 Created`   | Passed |
| Short `device_id`       | `422`           | Passed |
| Short `hostname`        | `422`           | Passed |
| Invalid device type     | `422`           | Passed |
| Invalid IPv4 address    | `422`           | Passed |
| Missing required field  | `422`           | Passed |
| Multiple invalid fields | `422`           | Passed |
| Optional description    | Accepted        | Passed |
| Long hostname           | `422`           | Passed |

---

## Example Valid Request

```json
{
  "device_id": "R102",
  "hostname": "EDGE-R102",
  "device_type": "router",
  "management_ip": "192.168.40.102",
  "status": "active",
  "description": "Validation test device"
}
```

Expected response:

```text
HTTP 201 Created
```

---

## Example Validation Error

Request:

```json
{
  "device_id": "R",
  "hostname": "X",
  "device_type": "firewall",
  "management_ip": "not-an-ip",
  "status": "active"
}
```

Expected:

```text
HTTP 422 Unprocessable Entity
```

Multiple field-level validation errors are returned by FastAPI/Pydantic.

---

## Key Learning Outcomes

This lab demonstrates how Pydantic provides a strong validation layer for a FastAPI-based network operations platform.

Key concepts:

* Declarative data validation
* Required and optional fields
* Type enforcement
* String constraints
* Enumerated values using `Literal`
* IPv4 address validation
* Nested Pydantic models
* HTTP `422` validation responses
* Request model vs response model
* JSON serialization of typed Pydantic data

---

## Project Status

**Lab 06 — Pydantic Validation: COMPLETE**

The API now has a stronger validation layer before moving toward persistent database storage and more advanced network-operations functionality.
