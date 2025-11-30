"""
Middleware layer for cross-cutting concerns.

Why: Centraliza lógica que se aplica a todas as requests,
     como logging, segurança, rate limiting e monitoramento.

How: Cada middleware é registrado no app FastAPI e executa
     antes/depois de cada request de forma transparente.
"""

from app.middleware.logging import RequestLoggingMiddleware
from app.middleware.security import SecurityMiddleware

__all__ = [
    "RequestLoggingMiddleware",
    "SecurityMiddleware",
]
