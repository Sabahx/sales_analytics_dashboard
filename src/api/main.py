"""
Main FastAPI application with authentication and analytics endpoints.
Professional REST API with JWT authentication, email verification, and protected routes.
"""
import logging

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from src.api.routers import auth, users, analytics, customers, products, geographic, revenue
from src.database.connection import get_connection

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Sales Analytics API",
    description="Professional REST API for sales analytics with secure authentication",
    version="1.0.0",
    docs_url="/api/docs",  # Swagger UI
    redoc_url="/api/redoc"  # ReDoc
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed error messages."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body}
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors gracefully."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred. Please try again later."}
    )


# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(analytics.router)
app.include_router(customers.router)
app.include_router(products.router)
app.include_router(geographic.router)
app.include_router(revenue.router)


# ==================== ROOT & SYSTEM ENDPOINTS ====================

@app.get("/", tags=["Root"])
async def root():
    """API root endpoint."""
    return {
        "message": "Sales Analytics API",
        "version": "1.0.0",
        "docs": "/api/docs"
    }


@app.get("/api/health", tags=["System"])
async def health_check():
    """
    API health check endpoint with database connectivity test.

    Returns:
        dict: Health status including API and database connectivity
    """
    health_status = {
        "status": "healthy",
        "service": "Sales Analytics API",
        "version": "1.0.0"
    }

    # Check database connectivity
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        conn.close()
        health_status["database"] = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["database"] = "disconnected"
        health_status["status"] = "degraded"

    return health_status
