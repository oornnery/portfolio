import logging
from pathlib import Path
from typing import Any, cast

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.presentation.dependencies import limiter, render_template
from app.core.logger import configure_logging
from app.presentation.routers import about, analytics, contact, home, projects
from app.core.security import RequestTracingMiddleware, SecurityHeadersMiddleware
from app.application.services.seo import seo_for_page
from app.observability.telemetry import configure_telemetry

logger = logging.getLogger(__name__)


def rate_limit_handler(request: Request, exc: Exception) -> Response:
    if isinstance(exc, RateLimitExceeded):
        return _rate_limit_exceeded_handler(request, exc)
    return HTMLResponse("Rate limit exceeded.", status_code=429)


def create_app() -> FastAPI:
    configure_logging(settings.log_level)
    logger.info("Creating FastAPI application.")

    app = FastAPI(
        title=settings.app_name,
        description=settings.app_description,
        docs_url="/docs" if settings.debug else None,
        redoc_url=None,
        openapi_url="/openapi.json" if settings.debug else None,
    )
    configure_telemetry(app)

    static_dir = Path(__file__).resolve().parent / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
        logger.info("Mounted static files directory at /static.")
    else:
        logger.warning("Static directory not found; /static mount skipped.")

    app.add_middleware(cast(Any, RequestTracingMiddleware))
    app.add_middleware(cast(Any, SecurityHeadersMiddleware))

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

    app.include_router(home.router)
    app.include_router(about.router)
    app.include_router(projects.router)
    app.include_router(contact.router)
    app.include_router(analytics.router)
    logger.info("Routers registered: home | about | projects | contact | analytics.")

    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc: Exception) -> HTMLResponse:
        logger.info(f"Route not found for path={request.url.path}")
        seo = seo_for_page("404 - Not Found", "Page not found")
        html = render_template("pages/not_found.jinja", seo=seo, current_path="")
        return HTMLResponse(content=html, status_code=404)

    logger.info("FastAPI application created successfully.")
    return app


app = create_app()
