import hashlib
import hmac
import logging
import secrets
import time
from uuid import uuid4

from fastapi import Request
from opentelemetry.trace import get_current_span
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.config import settings
from app.log_events import LogEvent
from app.logger import bind_request_context, event_message, reset_request_context
from app.metrics import get_app_metrics

logger = logging.getLogger(__name__)
app_metrics = get_app_metrics()


def _csrf_user_agent_hash(user_agent: str) -> str:
    normalized = user_agent.strip().lower()
    if not normalized:
        return "na"
    return hashlib.sha256(normalized.encode()).hexdigest()[:16]


def _anonymize_identifier(value: str, *, namespace: str) -> str:
    normalized = value.strip().lower()
    if not normalized:
        return "unknown"
    digest = hmac.new(
        settings.secret_key.encode(),
        f"{namespace}:{normalized}".encode(),
        hashlib.sha256,
    ).hexdigest()
    return digest[:16]


def generate_csrf_token(*, user_agent: str = "") -> str:
    """Generate a timestamped CSRF token signed with HMAC-SHA256."""
    timestamp = str(int(time.time()))
    random_part = secrets.token_hex(16)
    user_agent_hash = _csrf_user_agent_hash(user_agent)
    payload = f"{timestamp}:{random_part}:{user_agent_hash}"
    signature = hmac.new(
        settings.secret_key.encode(),
        payload.encode(),
        hashlib.sha256,
    ).hexdigest()
    return f"{payload}:{signature}"


def validate_csrf_token(token: str, *, user_agent: str = "") -> bool:
    """Validate CSRF token signature and expiry."""
    try:
        parts = token.rsplit(":", 3)
        if len(parts) != 4:
            logger.debug("CSRF token has an invalid format.")
            return False
        timestamp_str, random_part, user_agent_hash, signature = parts
        payload = f"{timestamp_str}:{random_part}:{user_agent_hash}"
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
        expected_user_agent_hash = _csrf_user_agent_hash(user_agent)
        if not hmac.compare_digest(user_agent_hash, expected_user_agent_hash):
            logger.debug("CSRF token user-agent binding validation failed.")
            return False
    except (TypeError, ValueError):
        logger.debug("CSRF token parsing failed.")
        return False
    return True


def is_allowed_form_content_type(content_type: str) -> bool:
    normalized = content_type.strip().lower()
    if not normalized:
        return False
    return normalized.startswith(
        ("application/x-www-form-urlencoded", "multipart/form-data")
    )


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
        raw_client_ip = request.client.host if request.client else "unknown"
        client_ip = _anonymize_identifier(raw_client_ip, namespace="ip")
        tokens = bind_request_context(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=client_ip,
        )
        request.state.request_id = request_id

        started_at = time.perf_counter()
        route_path = request.url.path
        app_metrics.request_started(method=request.method, path=route_path)
        logger.info(
            event_message(
                LogEvent.REQUEST_STARTED,
                route=route_path,
            )
        )
        status_code = 500
        exception_class = ""
        try:
            response = await call_next(request)
        except Exception as exc:
            exception_class = exc.__class__.__name__
            elapsed_ms = (time.perf_counter() - started_at) * 1000
            logger.exception(
                event_message(
                    LogEvent.REQUEST_FAILED,
                    route=route_path,
                    duration_ms=f"{elapsed_ms:.2f}",
                    error=exception_class,
                )
            )
            raise
        else:
            elapsed_ms = (time.perf_counter() - started_at) * 1000
            status_code = response.status_code
            route = request.scope.get("route")
            route_path = (
                getattr(route, "path", request.url.path) if route is not None else request.url.path
            )
            response.headers[settings.request_id_header] = request_id
            span_context = get_current_span().get_span_context()
            if span_context.is_valid:
                response.headers["X-Trace-ID"] = f"{span_context.trace_id:032x}"
            logger.info(
                event_message(
                    LogEvent.REQUEST_COMPLETED,
                    route=route_path,
                    status_code=response.status_code,
                    duration_ms=f"{elapsed_ms:.2f}",
                )
            )
            return response
        finally:
            elapsed_ms = (time.perf_counter() - started_at) * 1000
            app_metrics.request_finished(
                method=request.method,
                path=route_path,
                status_code=status_code,
                duration_ms=elapsed_ms,
                exception_class=exception_class,
            )
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
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=()"
        )

        if not settings.debug:
            response.headers["Strict-Transport-Security"] = (
                "max-age=63072000; includeSubDomains; preload"
            )
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "style-src 'self' 'unsafe-inline'; "
                "script-src 'self' https://cdn.tailwindcss.com; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self'; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
            )
        return response
