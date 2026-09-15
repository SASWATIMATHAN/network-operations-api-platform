# LAB 01 — Python & FastAPI Environment Setup

## Objective

Set up the Python development environment for **Project 3 — Network Operations API Platform** and verify the FastAPI application using Uvicorn, HTTP requests, and automatically generated OpenAPI documentation.

## Technology Stack

* Python 3.12.3
* FastAPI 0.141.1
* Uvicorn 0.53.0
* Pydantic 2.13.5
* WSL2 / Ubuntu
* Visual Studio Code
* Git / GitHub

## Project Structure

```text
PHASE 1 - WEB API & NETWORK OPERATIONS/
├── app/
│   └── main.py
│
├── LAB 01 - PYTHON & FASTAPI ENVIRONMENT SETUP/
│   └── README.md
│
├── requirements.txt
└── venv/
```

The virtual environment is shared across Phase 1 to avoid creating separate environments for every laboratory.

## Environment Setup

Create and activate the Phase 1 virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install the required packages:

```bash
pip install fastapi uvicorn
```

Verify the Python version:

```bash
python --version
```

Output:

```text
Python 3.12.3
```

Save the installed dependencies:

```bash
pip freeze > requirements.txt
```

## FastAPI Application

The application is located at:

```text
app/main.py
```

The initial application provides two endpoints:

### Root Endpoint

```text
GET /
```

Response:

```json
{
    "message": "Network Operations API is running"
}
```

### Health Check Endpoint

```text
GET /health
```

Response:

```json
{
    "status": "healthy"
}
```

## Running the Application

Start the FastAPI application using Uvicorn:

```bash
uvicorn app.main:app --reload
```

The application runs locally at:

```text
http://127.0.0.1:8000
```

## API Verification

### Root Endpoint

Access:

```text
http://127.0.0.1:8000
```

Result:

```json
{
    "message": "Network Operations API is running"
}
```

### Health Endpoint

Access:

```text
http://127.0.0.1:8000/health
```

Result:

```json
{
    "status": "healthy"
}
```

### Swagger UI

FastAPI automatically provides interactive API documentation at:

```text
http://127.0.0.1:8000/docs
```

The Swagger interface successfully displayed the available API endpoints.

### OpenAPI Specification

FastAPI also generates the OpenAPI specification at:

```text
http://127.0.0.1:8000/openapi.json
```

## Server Verification

The Uvicorn server successfully processed the following requests:

```text
GET /                 → 200 OK
GET /health           → 200 OK
GET /docs             → 200 OK
GET /openapi.json     → 200 OK
```

A browser request for `/favicon.ico` returned `404 Not Found`. This is expected because no favicon has been configured for the application.

## Key Concepts Learned

* Python virtual environments
* FastAPI application creation
* Uvicorn ASGI server
* REST-style HTTP GET endpoints
* JSON responses
* API health checks
* Automatic OpenAPI generation
* Swagger UI
* Basic API verification
* Python dependency management using `requirements.txt`

## Lab Outcome

The Python and FastAPI development environment was successfully configured and verified.

The initial Network Operations API is running successfully and provides working HTTP endpoints with automatically generated Swagger/OpenAPI documentation.

**Lab Status: COMPLETE**
