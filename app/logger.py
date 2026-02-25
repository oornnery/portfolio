from contextvars import ContextVar, Token
import logging
import logging.config
from typing import Any

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
        return True


def configure_logging(level: str) -> None:
    global _configured
    if _configured:
        return

    normalized_level = level.upper().strip() or "INFO"
    config: dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "request_context": {
                "()": "app.logger.RequestContextFilter",
            }
        },
        "formatters": {
            "default": {
                "format": (
                    "{asctime} | {levelname:<8} | {name} | "
                    "req_id={trace_request_id} method={trace_method} "
                    "path={trace_path} ip={trace_client_ip} | {message}"
                ),
                "style": "{",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "filters": ["request_context"],
                "stream": "ext://sys.stdout",
            }
        },
        "root": {
            "handlers": ["console"],
            "level": normalized_level,
        },
        "loggers": {
            "httpx": {"level": "WARNING"},
            "httpcore": {"level": "WARNING"},
            "watchfiles": {"level": "WARNING"},
        },
    }
    logging.config.dictConfig(config)
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
