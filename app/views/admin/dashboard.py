"""
Admin dashboard view.

Why: Página principal do painel administrativo.

How: Usa JinjaX catalog para renderizar o dashboard.
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from app.catalog import catalog
from app.models.user import User
from app.views.admin.deps import get_admin_user

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def admin_dashboard(request: Request, user: User = Depends(get_admin_user)):
    """Dashboard principal do admin."""
    return catalog.render(
        "admin/dashboard.jinja",
        request=request,
        user=user,
    )
