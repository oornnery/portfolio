"""
API v1 router aggregator.

Why: Versiona a API para permitir evolução sem quebrar
     clientes existentes. Prefixo /api/v1 indica versão.

How: Agrega todos os routers da v1 em um único ponto,
     facilitando inclusão no app principal.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, blog, comments, projects

api_router = APIRouter()

# Registra todos os endpoints da v1
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(blog.router, prefix="/blog", tags=["Blog"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(comments.router, prefix="/comments", tags=["Comments"])
