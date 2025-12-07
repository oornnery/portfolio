"""
Public views module.

Why: Agrupa todas as rotas públicas do site,
     facilitando manutenção e organização.

How: Re-exporta routers de submodulos específicos.
"""

from fastapi import APIRouter

from app.views.public.home import router as home_router
from app.views.public.blog import router as blog_router
from app.views.public.projects import router as projects_router
from app.views.public.auth import router as auth_router

router = APIRouter(include_in_schema=False)

# Include all public routers
router.include_router(home_router)
router.include_router(blog_router, prefix="/blog")
router.include_router(projects_router, prefix="/projects")
router.include_router(auth_router)
