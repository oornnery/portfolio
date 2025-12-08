"""
Analytics Tracking Middleware.

Why: Captura automaticamente pageviews e dados de visitantes
     para cada requisição, sem modificar os handlers.

How: Middleware que intercepta requisições, identifica/cria
     visitors via fingerprint, e registra eventos no banco.
"""

import asyncio
import hashlib
import logging
import time
import uuid
from datetime import datetime, timezone

from fastapi import Request, Response
from sqlmodel import select
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from user_agents import parse as parse_user_agent

logger = logging.getLogger(__name__)


def get_client_ip(request: Request) -> str:
    """
    Extrai IP real do cliente considerando proxies.

    Why: Em produção com reverse proxy (nginx, cloudflare),
         o IP real vem em headers específicos.
    """
    # Check common proxy headers
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # Get the first IP in the chain (original client)
        return forwarded.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    cf_ip = request.headers.get("CF-Connecting-IP")
    if cf_ip:
        return cf_ip

    # Fallback to direct connection
    if request.client:
        return request.client.host

    return "unknown"


def parse_user_agent_info(ua_string: str) -> dict:
    """
    Parse user agent string para extrair informações.

    Why: Identificar browser, OS e dispositivo para analytics
         e fingerprinting.
    """
    try:
        ua = parse_user_agent(ua_string)
        return {
            "browser_name": ua.browser.family,
            "browser_version": ua.browser.version_string,
            "os_name": ua.os.family,
            "os_version": ua.os.version_string,
            "device_type": "mobile"
            if ua.is_mobile
            else "tablet"
            if ua.is_tablet
            else "desktop",
            "is_bot": ua.is_bot,
        }
    except Exception:
        return {
            "browser_name": None,
            "browser_version": None,
            "os_name": None,
            "os_version": None,
            "device_type": None,
            "is_bot": False,
        }


def generate_server_fingerprint(request: Request) -> str:
    """
    Gera fingerprint server-side baseado em headers.

    Why: Fallback quando JS fingerprint não está disponível,
         para tracking mínimo de visitors.
    """
    components = [
        request.headers.get("User-Agent", ""),
        request.headers.get("Accept-Language", ""),
        request.headers.get("Accept-Encoding", ""),
        get_client_ip(request),
    ]
    fingerprint_string = "|".join(components)
    return hashlib.sha256(fingerprint_string.encode()).hexdigest()


async def save_analytics_to_db(
    request: Request,
    response_status: int,
    processing_time_ms: int,
) -> None:
    """
    Salva dados de analytics no banco de dados.

    Why: Persistir visitantes e pageviews para análise posterior.
    """
    from app.db import async_session_factory
    from app.models.analytics import AnalyticsEvent, EventType, Visitor

    analytics_data = getattr(request.state, "analytics", {})
    if not analytics_data:
        return

    try:
        async with async_session_factory() as session:
            fingerprint = analytics_data.get("server_fingerprint", "unknown")

            # Buscar ou criar visitor
            result = await session.execute(
                select(Visitor).where(Visitor.fingerprint_hash == fingerprint)
            )
            visitor = result.scalar_one_or_none()

            now = datetime.now(timezone.utc)

            if visitor:
                # Atualizar visitor existente
                visitor.last_seen_at = now
                visitor.visit_count += 1
                visitor.ip_address = analytics_data.get("client_ip")
            else:
                # Criar novo visitor
                visitor = Visitor(
                    fingerprint_hash=fingerprint,
                    ip_address=analytics_data.get("client_ip"),
                    user_agent=analytics_data.get("user_agent"),
                    browser_name=analytics_data.get("browser_name"),
                    browser_version=analytics_data.get("browser_version"),
                    os_name=analytics_data.get("os_name"),
                    os_version=analytics_data.get("os_version"),
                    device_type=analytics_data.get("device_type"),
                    is_bot=analytics_data.get("is_bot", False),
                    first_seen_at=now,
                    last_seen_at=now,
                    visit_count=1,
                )
                session.add(visitor)
                await session.flush()  # Para obter o ID

            # Criar evento de pageview
            event = AnalyticsEvent(
                visitor_id=visitor.id,
                event_type=EventType.PAGE_VIEW,
                page_url=str(request.url),
                page_title=None,  # Seria preenchido pelo JS
                referrer_url=analytics_data.get("referer"),
                session_id=analytics_data.get("session_id"),
                page_load_time=processing_time_ms,
            )
            session.add(event)

            await session.commit()

    except Exception as e:
        logger.error(f"Failed to save analytics: {e}")


class AnalyticsMiddleware(BaseHTTPMiddleware):
    """
    Middleware para tracking de analytics e fingerprinting.

    Features:
    - Tracking de page views
    - Identificação de visitors via fingerprint
    - Captura de dados de sessão
    - Rate limiting baseado em visitor
    """

    # Paths to skip tracking
    SKIP_PATHS = {
        "/static",
        "/favicon.ico",
        "/health",
        "/api/v1/analytics",  # Don't track analytics API itself
        "/_",  # Internal routes
    }

    # File extensions to skip
    SKIP_EXTENSIONS = {
        ".js",
        ".css",
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".svg",
        ".ico",
        ".woff",
        ".woff2",
    }

    def __init__(self, app, enabled: bool = True):
        super().__init__(app)
        self.enabled = enabled

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if not self.enabled:
            return await call_next(request)

        # Check if we should skip this path
        path = request.url.path
        if self._should_skip(path):
            return await call_next(request)

        # Add tracking info to request state
        start_time = time.time()
        request.state.analytics = {
            "client_ip": get_client_ip(request),
            "user_agent": request.headers.get("User-Agent", ""),
            "referer": request.headers.get("Referer"),
            "server_fingerprint": generate_server_fingerprint(request),
            "start_time": start_time,
        }

        # Parse user agent
        ua_info = parse_user_agent_info(request.state.analytics["user_agent"])
        request.state.analytics.update(ua_info)

        # Get or create session ID from cookie
        session_id = request.cookies.get("_analytics_session")
        if not session_id:
            session_id = str(uuid.uuid4())
        request.state.analytics["session_id"] = session_id

        # Process request
        response = await call_next(request)

        # Calculate processing time
        processing_time = time.time() - start_time
        request.state.analytics["processing_time_ms"] = int(processing_time * 1000)

        # Set session cookie if new
        if "_analytics_session" not in request.cookies:
            response.set_cookie(
                key="_analytics_session",
                value=session_id,
                max_age=60 * 60 * 24 * 365,  # 1 year
                httponly=True,
                samesite="lax",
                secure=request.url.scheme == "https",
            )

        # Salvar analytics no banco de dados (em background)
        if response.status_code < 400 and request.method == "GET":
            processing_time_ms = int(processing_time * 1000)
            # Executa em background para não bloquear a resposta
            asyncio.create_task(
                save_analytics_to_db(request, response.status_code, processing_time_ms)
            )

            logger.debug(
                f"Analytics: {request.method} {path} - "
                f"{response.status_code} - {processing_time * 1000:.0f}ms - "
                f"IP: {request.state.analytics['client_ip']} - "
                f"Session: {session_id[:8]}..."
            )

        return response

    def _should_skip(self, path: str) -> bool:
        """Check if path should be skipped from tracking."""
        # Check prefixes
        for skip_path in self.SKIP_PATHS:
            if path.startswith(skip_path):
                return True

        # Check extensions
        for ext in self.SKIP_EXTENSIONS:
            if path.endswith(ext):
                return True

        return False
