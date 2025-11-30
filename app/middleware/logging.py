"""
Request logging middleware for observability.

Why: Logs estruturados de cada request permitem monitoramento,
     debugging e análise de performance em produção.

How: Captura informações da request/response e loga em formato
     estruturado com métricas de tempo e status.
"""

import logging
import time
from collections.abc import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.config import settings

# Configura logger específico para requests
logger = logging.getLogger("app.requests")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Loga informações de cada request HTTP.

    Why: Fornece visibilidade sobre o tráfego da aplicação,
         permite identificar erros, lentidão e padrões de uso.

    Informações logadas:
        - Método HTTP e path
        - Status code da resposta
        - Tempo de processamento em ms
        - Request ID para correlação
        - IP do cliente (para rate limiting e análise)
    """

    # Paths que não devem ser logados (health checks, static files)
    SKIP_PATHS = {"/health", "/static", "/favicon.ico"}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip logging para paths frequentes/não importantes
        if any(request.url.path.startswith(p) for p in self.SKIP_PATHS):
            return await call_next(request)

        start_time = time.perf_counter()
        request_id = getattr(request.state, "request_id", "unknown")

        # Processa a request
        response = await call_next(request)

        # Calcula tempo de processamento
        process_time_ms = (time.perf_counter() - start_time) * 1000

        # Log estruturado
        log_data = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "duration_ms": round(process_time_ms, 2),
            "client_ip": self._get_client_ip(request),
        }

        # Define nível de log baseado no status code
        if response.status_code >= 500:
            logger.error("Request failed", extra=log_data)
        elif response.status_code >= 400:
            logger.warning("Request error", extra=log_data)
        elif settings.ENV == "development":
            # Em dev, loga todas as requests
            logger.info("Request completed", extra=log_data)

        # Adiciona header com tempo de processamento (útil para debugging)
        response.headers["X-Process-Time"] = f"{process_time_ms:.2f}ms"

        return response

    def _get_client_ip(self, request: Request) -> str:
        """
        Extrai IP real do cliente, considerando proxies.

        Why: Em produção atrás de load balancer/proxy, o IP direto
             é do proxy. X-Forwarded-For contém o IP real.
        """
        # Tenta X-Forwarded-For primeiro (quando atrás de proxy)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            # Pode conter múltiplos IPs, o primeiro é o cliente original
            return forwarded.split(",")[0].strip()

        # Fallback para IP direto
        if request.client:
            return request.client.host

        return "unknown"
