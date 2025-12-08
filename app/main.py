"""
Main FastAPI application entry point.

Why: Centraliza a configuração da aplicação, middlewares,
     routers e lifecycle hooks em um único ponto.

How: Usa lifespan para inicialização do banco,
     middlewares para segurança e logging,
     routers versionados para API e views.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from sqlmodel import SQLModel
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.api.v1 import api_router
from app.config import settings
from app.db import engine
from app.seed import seed_db
from app.middleware import RequestLoggingMiddleware, SecurityMiddleware
from app.middleware.analytics import AnalyticsMiddleware
from app.views import admin_router, public_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle manager.

    Startup: Cria tabelas no banco e executa seed.
    Shutdown: Cleanup de recursos (se necessário).
    """
    # Setup OpenTelemetry (opcional)
    try:
        from app.core.telemetry import instrument_app, setup_telemetry

        otlp_endpoint = getattr(settings, "OTLP_ENDPOINT", None)
        setup_telemetry(
            service_name="portfolio",
            otlp_endpoint=otlp_endpoint,
            enable_console_export=settings.is_development,
        )
        instrument_app(app, engine)
        logger.info("OpenTelemetry initialized")
    except ImportError:
        logger.debug("OpenTelemetry not available, skipping instrumentation")
    except Exception as e:
        logger.warning(f"OpenTelemetry setup failed: {e}")

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    # Seed database with admin user
    if settings.SEED_DB_ON_STARTUP:
        await seed_db()

    yield


# ==========================================
# Rate Limiter Configuration
# ==========================================

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"],
    storage_uri="memory://",
)


def rate_limit_exceeded_handler(request: Request, exc: Exception) -> Response:
    """Handler para rate limit excedido com tipagem correta."""
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Try again later."},
    )


# ==========================================
# App Configuration
# ==========================================

app = FastAPI(
    title="Portfolio API",
    description="API for a minimalist portfolio with blog and projects",
    version="1.0.0",
    lifespan=lifespan,
    # Desabilita docs em produção
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
    openapi_url="/openapi.json" if settings.is_development else None,
)

# Rate limiter state
app.state.limiter = limiter


# ==========================================
# Exception Handlers
# ==========================================

app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Handler global para exceções não tratadas.

    Why: Previne vazamento de informações de erro em produção.
    """
    if settings.is_development:
        # Em dev, mostra erro completo
        raise exc

    # Em produção, retorna erro genérico
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# ==========================================
# Middlewares (ordem importa - último adicionado é executado primeiro)
# ==========================================

# Rate limiting middleware
app.add_middleware(SlowAPIMiddleware)  # type: ignore[arg-type]

# Request logging (primeiro a executar, último a responder)
app.add_middleware(RequestLoggingMiddleware)  # type: ignore[arg-type]

# Analytics tracking (fingerprinting e pageviews)
app.add_middleware(AnalyticsMiddleware, enabled=True)  # type: ignore[arg-type]

# Security headers + HTMX validation
app.add_middleware(SecurityMiddleware)  # type: ignore[arg-type]

# Trusted hosts (previne host header injection)
if settings.is_production:
    app.add_middleware(
        TrustedHostMiddleware,  # type: ignore[arg-type]
        allowed_hosts=settings.ALLOWED_HOSTS,
    )
    # HTTPS redirect em produção
    if settings.FORCE_HTTPS:
        app.add_middleware(HTTPSRedirectMiddleware)  # type: ignore[arg-type]

# CORS middleware
app.add_middleware(
    CORSMiddleware,  # type: ignore[arg-type]
    allow_origins=settings.ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

# ==========================================
# Static Files
# ==========================================

app.mount("/static", StaticFiles(directory="app/static"), name="static")

# ==========================================
# Routers
# ==========================================

# Public views (templates)
app.include_router(public_router)

# Admin views (templates)
app.include_router(admin_router)

# API v1 (JSON endpoints)
app.include_router(api_router, prefix="/api/v1")


# ==========================================
# Health Check
# ==========================================


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "ok", "version": "1.0.0"}
