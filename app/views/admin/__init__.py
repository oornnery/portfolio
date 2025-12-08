"""
Admin views module.

Why: Agrupa todas as rotas admin do site,
     facilitando manutenção e organização.

How: Re-exporta routers de submodulos específicos.
"""

from fastapi import APIRouter

from app.views.admin.analytics import router as analytics_router
from app.views.admin.blog import router as blog_router
from app.views.admin.dashboard import router as dashboard_router
from app.views.admin.profile import router as profile_router
from app.views.admin.projects import router as projects_router

router = APIRouter(prefix="/admin", include_in_schema=False)

# Include all admin routers
router.include_router(dashboard_router)
router.include_router(profile_router)
router.include_router(projects_router)
router.include_router(blog_router)
router.include_router(analytics_router)
