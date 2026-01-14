"""
Auth views.

Why: Separa as rotas de autenticação (login) em um módulo próprio.

How: Usa JinjaX catalog para renderizar página de login.
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.catalog import catalog
from app.core.deps import get_current_user_optional
from app.models.user import User

router = APIRouter()


@router.get("/login", response_class=HTMLResponse)
async def login_page(
    request: Request,
    user: User | None = Depends(get_current_user_optional),
):
    """Página de login - redireciona se já autenticado."""
    if user:
        return RedirectResponse(url="/")

    return catalog.render(
        "pages/Login.jinja",
        request=request,
        user=user,
    )
