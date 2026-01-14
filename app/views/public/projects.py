"""
Projects views.

Why: Separa as rotas de projetos (listagem, detalhe) em um módulo próprio,
     mantendo a lógica de projetos isolada.

How: Usa JinjaX catalog para renderizar componentes de projetos.
"""

import markdown
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.catalog import catalog
from app.core.deps import get_current_user_optional
from app.db import get_session
from app.models.project import Project
from app.models.user import User

router = APIRouter()


@router.get("", response_class=HTMLResponse)
async def projects_list(
    request: Request,
    category: str | None = None,
    session: AsyncSession = Depends(get_session),
    user: User | None = Depends(get_current_user_optional),
):
    """Lista de projetos com filtro opcional por categoria."""
    query = select(Project)
    if category:
        query = query.where(Project.category == category)

    result = await session.execute(query)
    projects_list = list(result.scalars().all())

    # HTMX partial response
    if request.headers.get("HX-Request"):
        return catalog.render(
            "projects/ProjectList.jinja",
            projects=projects_list,
        )

    return catalog.render(
        "pages/Projects.jinja",
        request=request,
        user=user,
        projects=projects_list,
    )


@router.get("/{slug}", response_class=HTMLResponse)
async def project_detail(
    slug: str,
    request: Request,
    session: AsyncSession = Depends(get_session),
    user: User | None = Depends(get_current_user_optional),
):
    """Detalhe de um projeto específico."""
    query = select(Project).where(Project.slug == slug)
    result = await session.execute(query)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    html_content = markdown.markdown(
        project.content or "", extensions=["fenced_code", "codehilite", "tables"]
    )

    return catalog.render(
        "pages/ProjectDetail.jinja",
        request=request,
        user=user,
        project=project,
        content=html_content,
    )
