"""
Views package - Frontend routes.

Why: Organiza as views (rotas com templates) em um módulo separado
     das APIs, seguindo a separação frontend/backend.

How: Exporta routers públicos e admin para inclusão no app principal.
"""

from app.views.admin import router as admin_router
from app.views.public import router as public_router

__all__ = ["public_router", "admin_router"]
