import hashlib
import hmac
import logging
import secrets
import time
from uuid import uuid4

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.config import settings
from app.logger import bind_request_context, reset_request_context

logger = logging.getLogger(__name__)


def generate_csrf_token() -> str:
    """Generate a timestamped CSRF token signed with HMAC-SHA256."""
    timestamp = str(int(time.time()))
    random_part = secrets.token_hex(16)
    payload = f"{timestamp}:{random_part}"
    signature = hmac.new(
        settings.secret_key.encode(),
        payload.encode(),
        hashlib.sha256,
    ).hexdigest()
    return f"{payload}:{signature}"


def validate_csrf_token(token: str) -> bool:
    """Validate CSRF token signature and expiry."""
    try:
        parts = token.rsplit(":", 2)
        if len(parts) != 3:
            logger.debug("CSRF token has an invalid format.")
            return False
        timestamp_str, random_part, signature = parts
        payload = f"{timestamp_str}:{random_part}"
        expected = hmac.new(
            settings.secret_key.encode(),
            payload.encode(),
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(signature, expected):
            logger.debug("CSRF token signature validation failed.")
            return False

        timestamp = int(timestamp_str)
        age = time.time() - timestamp
        if age < 0:
            logger.debug("CSRF token timestamp is in the future.")
            return False
        if age > settings.csrf_token_expiry:
            logger.debug(f"CSRF token expired (age={age:.2f}s).")
            return False
    except (TypeError, ValueError):
        logger.debug("CSRF token parsing failed.")
        return False
    return True


class RequestTracingMiddleware(BaseHTTPMiddleware):
    """Attach trace context to each request and emit request lifecycle logs."""

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        request_id = (
            request.headers.get(settings.request_id_header, "").strip() or uuid4().hex
        )
        client_ip = request.client.host if request.client else "unknown"
        tokens = bind_request_context(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=client_ip,
        )
        request.state.request_id = request_id

        started_at = time.perf_counter()
        logger.info("Request started.")
        try:
            response = await call_next(request)
        except Exception:
            elapsed_ms = (time.perf_counter() - started_at) * 1000
            logger.exception(f"Request failed after {elapsed_ms:.2f}ms.")
            raise
        else:
            elapsed_ms = (time.perf_counter() - started_at) * 1000
            response.headers[settings.request_id_header] = request_id
            logger.info(
                f"Request completed with status_code={response.status_code} "
                f"duration_ms={elapsed_ms:.2f}."
            )
            return response
        finally:
            reset_request_context(tokens)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add baseline security headers to every response."""

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=()"
        )

        if not settings.debug:
            response.headers["Strict-Transport-Security"] = (
                "max-age=63072000; includeSubDomains; preload"
            )
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "script-src 'self' https://cdn.tailwindcss.com; "
                "img-src 'self' data: https:; "
                "font-src 'self' data: https://fonts.gstatic.com https:; "
            )
        return response
