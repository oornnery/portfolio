"""
Home and static page views.

Why: Separa as páginas estáticas (home, about, contact) em um módulo próprio,
     mantendo o código organizado e fácil de manter.

How: Usa JinjaX catalog para renderizar componentes de página.
"""

import markdown
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from app.catalog import catalog
from app.core.deps import get_current_user_optional
from app.db import get_session
from app.models.blog import Post
from app.models.profile import Profile
from app.models.project import Project
from app.models.user import User

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def home(
    request: Request,
    session: AsyncSession = Depends(get_session),
    user: User | None = Depends(get_current_user_optional),
):
    """Página inicial com projetos e posts em destaque."""
    # Busca profile
    profile_result = await session.execute(select(Profile).limit(1))
    profile = profile_result.scalar_one_or_none()

    # Busca os 3 projetos mais recentes
    projects_query = select(Project).order_by(col(Project.created_at).desc()).limit(3)
    projects_result = await session.execute(projects_query)
    projects_list = list(projects_result.scalars().all())

    # Busca os 3 posts publicados mais recentes
    posts_query = (
        select(Post)
        .where(Post.draft == False)  # noqa: E712
        .order_by(col(Post.published_at).desc())
        .limit(3)
    )
    posts_result = await session.execute(posts_query)
    posts_list = list(posts_result.scalars().all())

    return catalog.render(
        "pages/home.jinja",
        request=request,
        user=user,
        profile=profile,
        projects=projects_list,
        posts=posts_list,
    )


@router.get("/about", response_class=HTMLResponse)
async def about(
    request: Request,
    session: AsyncSession = Depends(get_session),
    user: User | None = Depends(get_current_user_optional),
):
    """Página sobre com perfil do usuário."""
    query = select(Profile).limit(1)
    result = await session.execute(query)
    profile = result.scalar_one_or_none()

    # Renderiza o markdown do about para HTML
    about_html = ""
    if profile and profile.about_markdown:
        about_html = markdown.markdown(
            profile.about_markdown,
            extensions=["fenced_code", "codehilite", "tables", "nl2br"],
        )

    return catalog.render(
        "pages/about.jinja",
        request=request,
        user=user,
        profile=profile,
        about_html=about_html,
    )


@router.get("/contact", response_class=HTMLResponse)
async def contact(
    request: Request,
    user: User | None = Depends(get_current_user_optional),
):
    """Página de contato."""
    return catalog.render(
        "pages/contact.jinja",
        request=request,
        user=user,
    )
