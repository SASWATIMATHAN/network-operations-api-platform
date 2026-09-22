# Lab 05 — REST API: PUT & DELETE

## Project 3 — Network Operations API Platform

**Phase 1:** WEB API & NETWORK OPERATIONS

---

## 1. Objective

The objective of this lab was to extend the Network Operations API by implementing the remaining REST CRUD operations:

* `PUT` — update an existing network device
* `DELETE` — remove an existing network device

The lab also verified appropriate HTTP status codes for successful operations and missing resources.

---

## 2. Technologies Used

* Python 3.12.3
* FastAPI
* Pydantic
* Uvicorn
* Swagger/OpenAPI
* Ubuntu WSL
* VS Code
* Git/GitHub

**GNS3:** Not required for this lab.

---

## 3. API Operations

The API now supports the complete CRUD workflow:

| Operation | HTTP Method | Endpoint               | Purpose                   |
| --------- | ----------- | ---------------------- | ------------------------- |
| Create    | POST        | `/devices`             | Create a new device       |
| Read      | GET         | `/devices`             | List devices              |
| Read      | GET         | `/devices/{device_id}` | Retrieve one device       |
| Update    | PUT         | `/devices/{device_id}` | Update an existing device |
| Delete    | DELETE      | `/devices/{device_id}` | Delete an existing device |

---

## 4. DeviceUpdate Model

A dedicated Pydantic request model was added for PUT operations.

The model accepts:

* `hostname`
* `device_type`
* `management_ip`
* `status`

The `device_id` remains part of the URL path.

Example:

```text
PUT /devices/R1
```

---

## 5. PUT Operation

### Endpoint

```text
PUT /devices/{device_id}
```

### Purpose

Updates an existing network-device resource.

### Example Request

```json
{
  "hostname": "CORE-R1-UPDATED",
  "device_type": "router",
  "management_ip": "192.168.40.10",
  "status": "maintenance"
}
```

### Successful Response

```text
200 OK
```

The updated device is returned in the response.

### Missing Device

If the requested device does not exist:

```text
404 Not Found
```

Example:

```json
{
  "detail": "Device 'R99' not found"
}
```

---

## 6. DELETE Operation

### Endpoint

```text
DELETE /devices/{device_id}
```

### Purpose

Removes an existing network-device resource.

### Successful Response

```text
204 No Content
```

No response body is returned.

### Missing Device

If the requested device does not exist:

```text
404 Not Found
```

---

## 7. Testing Performed

### Test 1 — Update Existing Device

```text
PUT /devices/R1
```

Result:

```text
200 OK
```

R1 was successfully updated.

---

### Test 2 — Verify Updated Device

```text
GET /devices/R1
```

Result:

```text
200 OK
```

The updated R1 data was returned, confirming that the modification persisted in the application's device list.

---

### Test 3 — Update Nonexistent Device

```text
PUT /devices/R99
```

Result:

```text
404 Not Found
```

---

### Test 4 — Delete Existing Device

```text
DELETE /devices/R4
```

Result:

```text
204 No Content
```

The R4 resource created during Lab 04 was successfully deleted.

---

### Test 5 — Verify Deleted Device

```text
GET /devices/R4
```

Result:

```text
404 Not Found
```

This confirmed that R4 was removed.

---

### Test 6 — Delete Already Deleted Device

```text
DELETE /devices/R4
```

Result:

```text
404 Not Found
```

This confirmed correct handling of a resource that no longer exists.

---

## 8. CRUD Workflow

The Network Operations API now supports:

```text
              ┌─────────────┐
              │    POST     │
              │   CREATE    │
              └──────┬──────┘
                     ↓
              ┌─────────────┐
              │     GET     │
              │     READ    │
              └──────┬──────┘
                     ↓
              ┌─────────────┐
              │     PUT     │
              │   UPDATE    │
              └──────┬──────┘
                     ↓
              ┌─────────────┐
              │   DELETE    │
              │    DELETE   │
              └─────────────┘
```

---

## 9. Result

Lab 05 successfully completed the basic REST CRUD functionality of the Network Operations API.

The API can now create, retrieve, update, and delete network-device resources.

The next stages can move beyond basic CRUD toward persistent storage, authentication, and eventually integration with actual network automation operations.

---

## 10. GNS3 Requirement

GNS3 was **not required** for Lab 05.

The devices were represented as API resources in the FastAPI application's current in-memory data structure.

Actual interaction with GNS3 routers will be introduced in later network-automation stages.

---

## 11. Lab Status

**Status:** Completed

**Git commit:** `Complete Lab 05 REST API PUT DELETE`
