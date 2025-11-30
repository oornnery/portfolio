"""
API package - REST endpoints.

Why: Organiza os endpoints da API em um módulo separado
     das views, seguindo padrões REST.

How: Exporta o router versionado da v1 para inclusão no app principal.
"""

from app.api.v1 import api_router

__all__ = ["api_router"]
