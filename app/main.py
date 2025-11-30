"""
Main FastAPI application entry point.

Why: Centraliza a configuração da aplicação, middlewares,
     routers e lifecycle hooks em um único ponto.

How: Usa lifespan para inicialização do banco,
     middlewares para segurança e logging,
     routers versionados para API e views.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlmodel import SQLModel

from app.api.v1 import api_router
from app.db import engine, seed_db
from app.middleware import RequestLoggingMiddleware, SecurityMiddleware
from app.views import admin_router, public_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle manager.

    Startup: Cria tabelas no banco e executa seed.
    Shutdown: Cleanup de recursos (se necessário).
    """
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    # Seed database with admin user
    await seed_db()

    yield


# ==========================================
# App Configuration
# ==========================================

app = FastAPI(
    title="Portfolio API",
    description="API for a minimalist portfolio with blog and projects",
    version="1.0.0",
    lifespan=lifespan,
)

# ==========================================
# Middlewares (ordem importa - último adicionado é executado primeiro)
# ==========================================

app.add_middleware(RequestLoggingMiddleware)  # type: ignore[arg-type]
app.add_middleware(SecurityMiddleware)  # type: ignore[arg-type]

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
