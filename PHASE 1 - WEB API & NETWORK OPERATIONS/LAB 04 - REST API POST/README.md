# Lab 04 — REST API: POST

## Objective

Implement HTTP POST operations in FastAPI to create new network-device resources.

## Concepts Covered

* HTTP POST method
* Request bodies
* JSON payloads
* Pydantic request models
* Input validation
* Response models
* HTTP 201 Created
* HTTP 409 Conflict
* HTTP 422 Unprocessable Entity
* Swagger/OpenAPI testing
* In-memory resource creation

## API Endpoint

### POST `/devices`

Creates a new network device.

### Request Model

The request body is validated using the `DeviceCreate` Pydantic model.

Fields:

* `device_id`
* `hostname`
* `device_type`
* `management_ip`
* `status`

`device_id` and `hostname` have a minimum length of 2 characters.

## Successful Request

Example JSON:

```json
{
  "device_id": "R4",
  "hostname": "CORE-R4",
  "device_type": "router",
  "management_ip": "192.168.40.13",
  "status": "active"
}
```

### Successful Response

HTTP status:

```text
201 Created
```

Response:

```json
{
  "device_id": "R4",
  "hostname": "CORE-R4",
  "device_type": "router",
  "management_ip": "192.168.40.13",
  "status": "active"
}
```

## Duplicate Device Handling

If a device with the same `device_id` already exists, the API returns:

```text
409 Conflict
```

Example:

```json
{
  "detail": "Device 'R4' already exists"
}
```

## Input Validation

FastAPI/Pydantic automatically validates the request body.

Missing required fields result in:

```text
422 Unprocessable Entity
```

Example missing fields:

* `device_type`
* `management_ip`
* `status`

Field-length validation is also applied to:

* `device_id`
* `hostname`

## Testing

Testing was performed using the FastAPI Swagger UI:

```text
http://127.0.0.1:8000/docs
```

### Test Results

| Test                    | Expected Result      | Status |
| ----------------------- | -------------------- | ------ |
| Create R4               | 201 Created          | PASS   |
| GET devices after POST  | R4 appears           | PASS   |
| Missing required fields | 422 Validation Error | PASS   |
| Invalid field length    | 422 Validation Error | PASS   |
| Duplicate R4            | 409 Conflict         | PASS   |

## Current Storage

Devices are currently stored in the Python `devices` list in memory.

Therefore, newly created devices are lost when the application restarts.

Persistent database storage will be introduced in a later phase using PostgreSQL.

## Result

The FastAPI application can now create and validate network-device resources through a RESTful POST endpoint while retaining the existing GET functionality from Lab 03.
