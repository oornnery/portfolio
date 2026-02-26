from contextvars import ContextVar, Token
import logging
from types import ModuleType

from opentelemetry.trace import get_current_span
from rich.logging import RichHandler

_request_id_ctx: ContextVar[str] = ContextVar("request_id", default="-")
_method_ctx: ContextVar[str] = ContextVar("method", default="-")
_path_ctx: ContextVar[str] = ContextVar("path", default="-")
_client_ip_ctx: ContextVar[str] = ContextVar("client_ip", default="-")

_configured = False


class RequestContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.trace_request_id = _request_id_ctx.get()
        record.trace_method = _method_ctx.get()
        record.trace_path = _path_ctx.get()
        record.trace_client_ip = _client_ip_ctx.get()
        span = get_current_span()
        context = span.get_span_context() if span is not None else None
        if context and context.is_valid:
            record.trace_id = f"{context.trace_id:032x}"
            record.span_id = f"{context.span_id:016x}"
        else:
            record.trace_id = "-"
            record.span_id = "-"
        return True


def _build_rich_handler(level: str) -> RichHandler:
    traceback_suppress: list[str | ModuleType] = []
    try:
        import click

        traceback_suppress.append(click)
    except Exception:
        traceback_suppress = []

    handler = RichHandler(
        level=level,
        rich_tracebacks=True,
        tracebacks_suppress=traceback_suppress,
        log_time_format="[%X]",
        show_path=False,
        markup=False,
        omit_repeated_times=False,
    )
    return handler


def configure_logging(level: str) -> None:
    global _configured
    if _configured:
        return

    normalized_level = level.upper().strip() or "INFO"
    handler = _build_rich_handler(normalized_level)
    handler.addFilter(RequestContextFilter())
    logging.basicConfig(
        level=normalized_level,
        format=(
            "%(name)s | %(message)s | "
            "req_id=%(trace_request_id)s method=%(trace_method)s "
            "path=%(trace_path)s ip=%(trace_client_ip)s "
            "trace_id=%(trace_id)s span_id=%(span_id)s"
        ),
        datefmt="[%X]",
        handlers=[handler],
        force=True,
    )

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("watchfiles").setLevel(logging.WARNING)
    _configured = True


def bind_request_context(
    request_id: str,
    method: str,
    path: str,
    client_ip: str,
) -> tuple[Token[str], Token[str], Token[str], Token[str]]:
    return (
        _request_id_ctx.set(request_id),
        _method_ctx.set(method),
        _path_ctx.set(path),
        _client_ip_ctx.set(client_ip),
    )


def reset_request_context(
    tokens: tuple[Token[str], Token[str], Token[str], Token[str]],
) -> None:
    request_token, method_token, path_token, client_ip_token = tokens
    _request_id_ctx.reset(request_token)
    _method_ctx.reset(method_token)
    _path_ctx.reset(path_token)
    _client_ip_ctx.reset(client_ip_token)


def get_request_id() -> str:
    return _request_id_ctx.get()
