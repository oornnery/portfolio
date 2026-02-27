from fastapi import APIRouter

from . import about, analytics, contact, health, home, projects

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(home.router, tags=["home"])
api_router.include_router(about.router, tags=["about"])
api_router.include_router(projects.router, tags=["projects"])
api_router.include_router(contact.router, tags=["contact"])
api_router.include_router(analytics.router, tags=["analytics"])
