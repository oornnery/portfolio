"""
Analytics Tracking Middleware.

Why: Captura automaticamente pageviews e dados de visitantes
     para cada requisição, sem modificar os handlers.

How: Middleware que intercepta requisições, identifica/cria
     visitors via fingerprint, e registra eventos.
"""

import hashlib
import logging
import time
import uuid

from fastapi import Request, Response
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

        # Log pageview asynchronously (we'll do this in background)
        # For now, just log to console in debug
        if response.status_code < 400:
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
