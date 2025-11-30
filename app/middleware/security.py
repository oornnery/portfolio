"""
Security middleware for hardening HTTP responses and request tracing.

Why: Headers de segurança previnem ataques comuns como XSS,
     clickjacking, MIME sniffing e information disclosure.
     Request IDs facilitam auditoria, debugging e rastreamento de incidentes.

How: Adiciona headers de segurança recomendados pela OWASP
     e gera IDs únicos para cada request para correlação de logs.
"""

import uuid
from collections.abc import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Middleware de segurança completo: headers + request tracing.

    Why: Implementa defesas em profundidade contra ataques web comuns,
         seguindo recomendações OWASP e boas práticas de segurança.
         Request IDs permitem rastrear requisições para auditoria.

    Security Headers:
        - X-Content-Type-Options: Previne MIME sniffing
        - X-Frame-Options: Previne clickjacking
        - X-XSS-Protection: Ativa filtro XSS do browser
        - Referrer-Policy: Controla informações de referrer
        - Permissions-Policy: Restringe APIs do browser
        - Content-Security-Policy: Controla fontes de conteúdo

    Tracing Headers:
        - X-Request-ID: UUID único da request para correlação de logs
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # ==========================================
        # Request ID (Tracing & Auditoria)
        # ==========================================

        # Usa request ID existente (de proxy/load balancer) ou gera novo
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # Disponibiliza para uso em handlers e logging
        request.state.request_id = request_id

        # Processa request
        response = await call_next(request)

        # ==========================================
        # Request Tracing Header
        # ==========================================

        # Retorna ID para correlação cliente-servidor
        response.headers["X-Request-ID"] = request_id

        # ==========================================
        # Security Headers (OWASP Recommendations)
        # ==========================================

        # Previne MIME sniffing - força browser a respeitar Content-Type
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Previne clickjacking - página não pode ser embebida em iframe
        response.headers["X-Frame-Options"] = "DENY"

        # Ativa filtro XSS do browser (legacy, mas ainda útil)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Controla informações enviadas no header Referer
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Restringe APIs sensíveis do browser
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=(), payment=()"
        )

        # CSP básico - permite scripts inline para HTMX e Tailwind CDN
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.tailwindcss.com https://unpkg.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.tailwindcss.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )

        return response


# Alias para compatibilidade
SecurityHeadersMiddleware = SecurityMiddleware
RequestIdMiddleware = SecurityMiddleware
