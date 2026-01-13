"""FastAPI application."""
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import os
import logging
import traceback

app = FastAPI(
    title="CDC Pipeline API",
    description="Change Data Capture Pipeline Management API",
    version="1.0.0"
)

# CORS middleware - must be added before other middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Middleware to add CORS headers to all responses
@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    """Add CORS headers to all responses."""
    try:
        response = await call_next(request)
        # Ensure CORS headers are present
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response
    except Exception as e:
        # Catch any exception and return with CORS headers
        import logging
        error_msg = str(e)
        # Sanitize error message
        model_keywords = [
            "UserSessionModel", "refresh_token_hash", "user_sessions", "session",
            "expires_at", "ip_address", "user_agent", "created_at", "user_id",
            "datetime.datetime", "datetime", "SQLAlchemy", "Base"
        ]
        if any(keyword in error_msg for keyword in model_keywords):
            error_msg = "Internal server error. Please try again."
        logging.error(f"Middleware caught exception: {type(e).__name__}: {error_msg}")
        return JSONResponse(
            status_code=500,
            content={"detail": error_msg},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*",
            }
        )

# Exception handler for HTTPException to add CORS headers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTPException with CORS headers."""
    from fastapi import HTTPException
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

# Global exception handler for unhandled exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler to sanitize error messages and prevent model serialization."""
    from fastapi import HTTPException
    
    # HTTPException should be handled by the handler above
    if isinstance(exc, HTTPException):
        raise exc
    
    # Handle other exceptions
    logging.error(f"Unhandled exception: {type(exc).__name__}: {str(exc)}")
    
    # Sanitize error message to prevent UserSessionModel serialization
    error_msg = str(exc)
    model_keywords = [
        "UserSessionModel", "refresh_token_hash", "user_sessions", "session",
        "expires_at", "ip_address", "user_agent", "created_at", "user_id",
        "datetime.datetime", "datetime", "SQLAlchemy", "Base"
    ]
    
    # Check if error contains model references
    if any(keyword in error_msg for keyword in model_keywords):
        error_msg = "Internal server error. Please try again."
        logging.error(f"Sanitized error message due to model object reference")
    
    # Log full traceback for debugging (but don't expose to client)
    try:
        tb_str = ''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        # Sanitize traceback too
        if any(keyword in tb_str for keyword in model_keywords):
            tb_str = "Traceback contains model objects - sanitized"
        logging.error(f"Traceback: {tb_str}")
    except Exception:
        logging.error("Could not format traceback")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": error_msg},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with CORS headers."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "CDC Pipeline API", "version": "1.0.0"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/api/health")
async def api_health():
    """API health check endpoint (for frontend compatibility)."""
    # Quick health check without database connection
    # This ensures the endpoint responds quickly even if DB is slow
    return {"status": "healthy", "service": "CDC Pipeline API"}


# Include routers
from ingestion.routers import auth, connections, pipelines, monitoring, discovery, users, audit, logs

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(audit.router, prefix="/api/v1/audit-logs", tags=["Audit"])
app.include_router(connections.router, prefix="/api/v1/connections", tags=["Connections"])
app.include_router(pipelines.router, prefix="/api/v1/pipelines", tags=["Pipelines"])
app.include_router(monitoring.router, prefix="/api/v1/monitoring", tags=["Monitoring"])
app.include_router(discovery.router, prefix="/api/v1/discovery", tags=["Discovery"])
app.include_router(logs.router, prefix="/api/v1/logs", tags=["Logs"])

# Alias for uvicorn compatibility
final_app = app

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("API_PORT", 8000))
    host = os.getenv("API_HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port)

