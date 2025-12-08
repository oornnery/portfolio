"""
Admin dashboard view.

Why: Página principal do painel administrativo.

How: Usa JinjaX catalog para renderizar o dashboard com
     estatísticas resumidas de analytics.
"""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.catalog import catalog
from app.db import get_session
from app.models.analytics import AnalyticsEvent, EventType, Visitor
from app.models.blog import Post
from app.models.project import Project
from app.models.user import User
from app.views.admin.deps import get_admin_user

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_admin_user),
):
    """Dashboard principal do admin com estatísticas."""
    now = datetime.now(timezone.utc)
    last_7_days = now - timedelta(days=7)

    # Contagem de posts
    posts_result = await session.execute(select(func.count(Post.id)))
    total_posts = posts_result.scalar() or 0

    # Contagem de projetos
    projects_result = await session.execute(select(func.count(Project.id)))
    total_projects = projects_result.scalar() or 0

    # Visitantes únicos últimos 7 dias
    visitors_result = await session.execute(
        select(func.count(Visitor.id)).where(Visitor.first_seen_at >= last_7_days)
    )
    recent_visitors = visitors_result.scalar() or 0

    # Page views últimos 7 dias
    pageviews_result = await session.execute(
        select(func.count(AnalyticsEvent.id)).where(
            AnalyticsEvent.event_type == EventType.PAGE_VIEW,
            AnalyticsEvent.created_at >= last_7_days,
        )
    )
    recent_pageviews = pageviews_result.scalar() or 0

    stats = {
        "total_posts": total_posts,
        "total_projects": total_projects,
        "recent_visitors": recent_visitors,
        "recent_pageviews": recent_pageviews,
    }

    return catalog.render(
        "admin/dashboard.jinja",
        request=request,
        user=user,
        stats=stats,
    )
