"""
Security middleware for hardening HTTP responses and request tracing.

Why: Headers de segurança previnem ataques comuns como XSS,
     clickjacking, MIME sniffing e information disclosure.
     Request IDs facilitam auditoria, debugging e rastreamento de incidentes.

How: Adiciona headers de segurança recomendados pela OWASP
     e gera IDs únicos para cada request para correlação de logs.
     Valida origem de requisições HTMX para prevenir CSRF.
"""

import uuid
from collections.abc import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.config import settings


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Middleware de segurança completo: headers + request tracing + HTMX validation.

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

    HTMX Security:
        - Valida HX-Request header com origem do request
        - Previne requisições HTMX cross-origin não autorizadas

    Tracing Headers:
        - X-Request-ID: UUID único da request para correlação de logs
    """

    # Paths que não precisam de validação HTMX (assets estáticos)
    SKIP_HTMX_VALIDATION = {"/static/", "/favicon.ico", "/health"}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # ==========================================
        # Request ID (Tracing & Auditoria)
        # ==========================================

        # Usa request ID existente (de proxy/load balancer) ou gera novo
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # Disponibiliza para uso em handlers e logging
        request.state.request_id = request_id

        # ==========================================
        # HTMX Request Validation
        # ==========================================

        # Valida requisições HTMX para prevenir CSRF
        if not self._should_skip_htmx_validation(request):
            if not self._validate_htmx_request(request):
                return Response(
                    content="Invalid HTMX request origin",
                    status_code=403,
                    headers={"X-Request-ID": request_id},
                )

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

        # Cache control para conteúdo sensível
        if request.url.path.startswith("/admin") or request.url.path.startswith(
            "/api/v1/auth"
        ):
            response.headers["Cache-Control"] = (
                "no-store, no-cache, must-revalidate, private"
            )

        # CSP - Content Security Policy
        # Modo mais restritivo em produção
        if settings.is_production:
            csp = self._get_production_csp()
        else:
            csp = self._get_development_csp()

        response.headers["Content-Security-Policy"] = csp

        return response

    def _should_skip_htmx_validation(self, request: Request) -> bool:
        """Verifica se request deve pular validação HTMX."""
        path = request.url.path
        return any(path.startswith(skip) for skip in self.SKIP_HTMX_VALIDATION)

    def _validate_htmx_request(self, request: Request) -> bool:
        """
        Valida requisições HTMX.

        HTMX envia headers específicos que podemos validar:
        - HX-Request: Indica que é uma requisição HTMX
        - HX-Current-URL: URL atual do cliente

        Retorna True se:
        - Não é uma requisição HTMX (sem HX-Request header)
        - É HTMX mas origem é válida (mesmo domínio)
        """
        hx_request = request.headers.get("HX-Request")

        # Não é HTMX, permite
        if not hx_request:
            return True

        # Valida origem
        origin = request.headers.get("Origin", "")
        referer = request.headers.get("Referer", "")

        # Host esperado
        host = request.headers.get("Host", "")

        # Verifica se origem/referer corresponde ao host
        if origin:
            # Remove protocolo para comparação
            origin_host = origin.split("://")[-1].split("/")[0]
            if origin_host == host or self._is_allowed_origin(origin):
                return True

        if referer:
            referer_host = referer.split("://")[-1].split("/")[0]
            if referer_host == host or self._is_allowed_origin(referer):
                return True

        # Em desenvolvimento, permite localhost
        if settings.is_development:
            if "localhost" in host or "127.0.0.1" in host:
                return True

        return False

    def _is_allowed_origin(self, url: str) -> bool:
        """Verifica se URL está na lista de origens permitidas."""
        for allowed in settings.ALLOW_ORIGINS:
            if url.startswith(allowed):
                return True
        return False

    def _get_production_csp(self) -> str:
        """CSP restritivo para produção."""
        return (
            "default-src 'self'; "
            "script-src 'self' https://cdn.tailwindcss.com https://unpkg.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.tailwindcss.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self';"
        )

    def _get_development_csp(self) -> str:
        """CSP mais permissivo para desenvolvimento."""
        return (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.tailwindcss.com https://unpkg.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.tailwindcss.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' ws://localhost:* http://localhost:*; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self';"
        )


# Alias para compatibilidade
SecurityHeadersMiddleware = SecurityMiddleware
RequestIdMiddleware = SecurityMiddleware
