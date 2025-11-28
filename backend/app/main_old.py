import logging
import platform
import time
from contextlib import asynccontextmanager
from datetime import datetime
from importlib.metadata import version

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.blog import router as blog_router
from app.api.projects import router as projects_router
from app.api.auth import router as auth_router
from app.api.comments import router as comments_router
from app.views import router as views_router
from app.config import settings
from app.db import init_db
from fastapi.staticfiles import StaticFiles

logger = logging.getLogger(__name__)


# ============================================
# Response Models for OpenAPI Documentation
# ============================================


class MessageResponse(BaseModel):
    """Simple message response."""

    message: str = Field(description="Response message")

    model_config = {"json_schema_extra": {"example": {"message": "OK"}}}


class HealthResponse(BaseModel):
    """Health check response with system information."""

    status: str = Field(description="Health status (healthy/unhealthy)")
    message: str = Field(description="Human-readable status message")
    service: str = Field(description="Service name")
    timestamp: str = Field(description="Current server timestamp (ISO format)")
    uptime: str = Field(description="Server uptime status")
    version: str = Field(description="Application version")
    platform: str = Field(description="Operating system platform")

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "healthy",
                "message": "Server is running",
                "service": "backend",
                "timestamp": "2025-11-26T00:30:00.000000",
                "uptime": "running",
                "version": "0.1.0",
                "platform": "Linux",
            }
        }
    }


class ErrorResponse(BaseModel):
    """Standard error response format."""

    status: str = Field(default="error", description="Error status indicator")
    type: str = Field(description="Error type identifier")
    message: str = Field(description="Human-readable error message")

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "error",
                "type": "not_found",
                "message": "Resource not found",
            }
        }
    }


class RateLimitResponse(BaseModel):
    """Rate limit exceeded response."""

    error: str = Field(description="Error message")
    retry_after: int = Field(description="Seconds until rate limit resets")

    model_config = {
        "json_schema_extra": {
            "example": {"error": "Rate limit exceeded", "retry_after": 60}
        }
    }


# ============================================
# Rate Limiter Setup
# ============================================

limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])


# ============================================
# Security Middleware
# ============================================


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=()"
        )

        # Remove server header if present
        if "server" in response.headers:
            del response.headers["server"]

        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests with timing information."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        process_time = (time.time() - start_time) * 1000
        logger.info(
            f"{request.method} {request.url.path} - {response.status_code} - {process_time:.2f}ms"
        )

        response.headers["X-Process-Time"] = f"{process_time:.2f}ms"

        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown events."""
    await init_db()
    logger.info("🚀 Application started successfully")
    yield
    logger.info("👋 Application shutting down")


# ============================================
# FastAPI Application Configuration
# ============================================

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
## Portfolio Backend API 🚀

A modern, fast, and secure REST API for a personal portfolio website.

### Features

* **Blog System** - Full CRUD for blog posts with markdown support
* **Reactions** - Like, love, fire, and more reactions on posts
* **Categories & Tags** - Organize content with categories and tags
* **Rate Limiting** - Protection against abuse (100 req/min default)
* **Security Headers** - OWASP recommended security headers

### Authentication

Currently, the API is open for public read access. 
Write operations (POST, PUT, DELETE) should be protected in production.

### Rate Limits

| Endpoint Type | Limit |
|--------------|-------|
| Read (GET) | 60/minute |
| Write (POST/PUT/DELETE) | 10/minute |
| Reactions | 30/minute |
| Health Check | 30/minute |

### Contact

- **GitHub**: [github.com/oornnery](https://github.com/oornnery)
- **Email**: contact@example.com
    """,
    version="0.1.0",
    terms_of_service="https://example.com/terms",
    contact={
        "name": "Portfolio API Support",
        "url": "https://github.com/oornnery/portfolio",
        "email": "contact@example.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan,
    docs_url=None if settings.ENV == "production" else "/docs",
    redoc_url=None if settings.ENV == "production" else "/redoc",
    openapi_url=None if settings.ENV == "production" else "/openapi.json",
    openapi_tags=[
        {
            "name": "System",
            "description": "System health and status endpoints",
        },
        {
            "name": "Blog",
            "description": "Blog post management - CRUD operations, reactions, categories, and tags",
        },
    ],
    responses={
        429: {
            "description": "Rate limit exceeded",
            "model": RateLimitResponse,
        },
        500: {
            "description": "Internal server error",
            "model": ErrorResponse,
        },
    },
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# ============================================
# Middleware Stack (order matters!)
# ============================================

# Security headers (outermost)
app.add_middleware(SecurityHeadersMiddleware)  # type: ignore[arg-type]

# Request logging
app.add_middleware(RequestLoggingMiddleware)  # type: ignore[arg-type]

# CORS
app.add_middleware(
    CORSMiddleware,  # type: ignore
    allow_origins=settings.ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Process-Time"],
)

# Trusted hosts
app.add_middleware(
    TrustedHostMiddleware,  # type: ignore
    allowed_hosts=settings.ALLOWED_HOSTS,
)


# ============================================
# Include Routers
# ============================================

app.include_router(blog_router, prefix="/api")
app.include_router(projects_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(comments_router, prefix="/api")
app.include_router(views_router)


# ============================================
# Exception Handlers
# ============================================


@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc: Exception):
    """Handle 404 Not Found errors."""
    return JSONResponse(
        status_code=404,
        content={
            "status": "error",
            "type": "not_found",
            "message": f"The route '{request.url.path}' was not found.",
        },
    )


@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc: Exception):
    """Handle 500 Internal Server errors."""
    logger.error(f"❌ CRITICAL ERROR: {exc!s}")

    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "type": "server_error",
            "message": "An unexpected error occurred. Please try again later.",
        },
    )


# ============================================
# System Endpoints
# ============================================


@app.get(
    "/api",
    response_model=MessageResponse,
    summary="API Root",
    description="""
Check if the API is accessible.

Returns a simple OK message to confirm the server is running.

**Rate Limit:** 60 requests per minute
    """,
    tags=["System"],
    responses={
        200: {
            "description": "Server is accessible",
            "model": MessageResponse,
            "content": {"application/json": {"example": {"message": "OK"}}},
        },
    },
)
@limiter.limit("60/minute")
async def api_root(request: Request) -> MessageResponse:
    """API Root endpoint - confirm API is accessible."""
    return MessageResponse(message="OK")


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="""
Get detailed health status and system information.

Returns:
- Server health status
- Application version
- Platform information
- Current timestamp

Useful for:
- Monitoring and alerting systems
- Load balancer health checks
- Deployment verification

**Rate Limit:** 30 requests per minute
    """,
    tags=["System"],
    responses={
        200: {
            "description": "Health status information",
            "model": HealthResponse,
        },
        503: {
            "description": "Service unavailable",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "type": "service_unavailable",
                        "message": "Service is temporarily unavailable",
                    }
                }
            },
        },
    },
)
@limiter.limit("30/minute")
async def health(request: Request) -> HealthResponse:
    """Health check endpoint with system information."""
    try:
        app_version = version("backend")
    except Exception:
        app_version = "0.1.0"

    return HealthResponse(
        status="healthy",
        message="Server is running",
        service="backend",
        timestamp=datetime.now().isoformat(),
        uptime="running",
        version=app_version,
        platform=platform.system(),
    )


@app.get(
    "/ping",
    response_model=MessageResponse,
    summary="Ping",
    description="""
Simple ping endpoint for quick connectivity checks.

Returns "pong" to confirm the server is responsive.
Minimal processing - ideal for frequent health checks.

**Rate Limit:** 60 requests per minute
    """,
    tags=["System"],
    responses={
        200: {
            "description": "Pong response",
            "content": {"application/json": {"example": {"message": "pong"}}},
        },
    },
)
@limiter.limit("60/minute")
async def ping(request: Request) -> MessageResponse:
    """Simple ping endpoint."""
    return MessageResponse(message="pong")


@app.get(
    "/version",
    summary="API Version",
    description="""
Get the current API version and build information.

Returns version details useful for:
- Client compatibility checks
- Debugging deployment issues
- API versioning

**Rate Limit:** 60 requests per minute
    """,
    tags=["System"],
    responses={
        200: {
            "description": "Version information",
            "content": {
                "application/json": {
                    "example": {
                        "version": "0.1.0",
                        "api_version": "v1",
                        "python_version": "3.14.0",
                        "environment": "development",
                    }
                }
            },
        },
    },
)
@limiter.limit("60/minute")
async def get_version(request: Request):
    """Get API version information."""
    import sys

    try:
        app_version = version("backend")
    except Exception:
        app_version = "0.1.0"

    return {
        "version": app_version,
        "api_version": "v1",
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "environment": settings.ENV,
    }
