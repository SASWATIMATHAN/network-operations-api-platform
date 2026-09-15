from fastapi import FastAPI

app = FastAPI(
    title="Network Operations API",
    description="REST API for network operations and device management",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "Network Operations API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }
