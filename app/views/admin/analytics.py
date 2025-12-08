"""
Admin analytics views.

Why: Visualização de métricas de visitantes, pageviews,
     eventos e comportamento no painel administrativo.

How: Queries agregadas nas tabelas de analytics com
     renderização via JinjaX.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from app.catalog import catalog
from app.db import get_session
from app.models.analytics import AnalyticsEvent, EventType, Session, Visitor
from app.models.user import User
from app.views.admin.deps import get_admin_user

router = APIRouter(prefix="/analytics")


async def get_overview_stats(session: AsyncSession, days: int = 30) -> dict[str, Any]:
    """
    Obtém estatísticas gerais de analytics.

    Why: Fornecer visão geral de métricas principais
         como visitantes, pageviews e sessões.
    """
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=days)

    # Total visitors
    total_visitors_result = await session.execute(select(func.count(Visitor.id)))
    total_visitors = total_visitors_result.scalar() or 0

    # New visitors in period
    new_visitors_result = await session.execute(
        select(func.count(Visitor.id)).where(Visitor.first_seen_at >= start_date)
    )
    new_visitors = new_visitors_result.scalar() or 0

    # Total pageviews in period
    pageviews_result = await session.execute(
        select(func.count(AnalyticsEvent.id)).where(
            AnalyticsEvent.event_type == EventType.PAGE_VIEW,
            AnalyticsEvent.created_at >= start_date,
        )
    )
    total_pageviews = pageviews_result.scalar() or 0

    # Total events in period
    total_events_result = await session.execute(
        select(func.count(AnalyticsEvent.id)).where(
            AnalyticsEvent.created_at >= start_date
        )
    )
    total_events = total_events_result.scalar() or 0

    # Active sessions (last 30 min)
    active_threshold = now - timedelta(minutes=30)
    active_sessions_result = await session.execute(
        select(func.count(Session.id)).where(
            Session.last_activity_at >= active_threshold, Session.is_active
        )
    )
    active_sessions = active_sessions_result.scalar() or 0

    # Unique visitors in period
    unique_visitors_result = await session.execute(
        select(func.count(func.distinct(AnalyticsEvent.visitor_id))).where(
            AnalyticsEvent.created_at >= start_date
        )
    )
    unique_visitors = unique_visitors_result.scalar() or 0

    return {
        "total_visitors": total_visitors,
        "new_visitors": new_visitors,
        "unique_visitors": unique_visitors,
        "total_pageviews": total_pageviews,
        "total_events": total_events,
        "active_sessions": active_sessions,
        "period_days": days,
    }


async def get_top_pages(
    session: AsyncSession, days: int = 30, limit: int = 10
) -> list[dict]:
    """
    Obtém as páginas mais visitadas.

    Why: Identificar conteúdo mais popular para
         otimização e produção de conteúdo.
    """
    start_date = datetime.now(timezone.utc) - timedelta(days=days)

    result = await session.execute(
        select(
            AnalyticsEvent.page_url,
            AnalyticsEvent.page_title,
            func.count(AnalyticsEvent.id).label("views"),
        )
        .where(
            AnalyticsEvent.event_type == EventType.PAGE_VIEW,
            AnalyticsEvent.created_at >= start_date,
        )
        .group_by(AnalyticsEvent.page_url, AnalyticsEvent.page_title)
        .order_by(func.count(AnalyticsEvent.id).desc())
        .limit(limit)
    )

    return [
        {
            "url": row.page_url,
            "title": row.page_title or row.page_url,
            "views": row.views,
        }
        for row in result.all()
    ]


async def get_top_referrers(
    session: AsyncSession, days: int = 30, limit: int = 10
) -> list[dict]:
    """
    Obtém os principais referenciadores.

    Why: Entender de onde vem o tráfego para
         otimizar estratégias de marketing.
    """
    start_date = datetime.now(timezone.utc) - timedelta(days=days)

    result = await session.execute(
        select(
            AnalyticsEvent.referrer_url, func.count(AnalyticsEvent.id).label("count")
        )
        .where(
            AnalyticsEvent.event_type == EventType.PAGE_VIEW,
            AnalyticsEvent.created_at >= start_date,
            AnalyticsEvent.referrer_url.isnot(None),
            AnalyticsEvent.referrer_url != "",
        )
        .group_by(AnalyticsEvent.referrer_url)
        .order_by(func.count(AnalyticsEvent.id).desc())
        .limit(limit)
    )

    return [{"url": row.referrer_url, "count": row.count} for row in result.all()]


async def get_device_stats(session: AsyncSession, days: int = 30) -> dict[str, int]:
    """
    Obtém estatísticas de dispositivos.

    Why: Entender quais dispositivos os visitantes
         usam para otimizar a experiência.
    """
    start_date = datetime.now(timezone.utc) - timedelta(days=days)

    result = await session.execute(
        select(Visitor.device_type, func.count(Visitor.id).label("count"))
        .where(Visitor.first_seen_at >= start_date)
        .group_by(Visitor.device_type)
    )

    stats = {"desktop": 0, "mobile": 0, "tablet": 0, "unknown": 0}
    for row in result.all():
        device = row.device_type or "unknown"
        stats[device] = row.count

    return stats


async def get_browser_stats(session: AsyncSession, days: int = 30) -> list[dict]:
    """
    Obtém estatísticas de navegadores.

    Why: Entender quais navegadores os visitantes
         usam para garantir compatibilidade.
    """
    start_date = datetime.now(timezone.utc) - timedelta(days=days)

    result = await session.execute(
        select(Visitor.browser_name, func.count(Visitor.id).label("count"))
        .where(Visitor.first_seen_at >= start_date)
        .group_by(Visitor.browser_name)
        .order_by(func.count(Visitor.id).desc())
        .limit(10)
    )

    return [
        {"browser": row.browser_name or "Unknown", "count": row.count}
        for row in result.all()
    ]


async def get_country_stats(session: AsyncSession, days: int = 30) -> list[dict]:
    """
    Obtém estatísticas por país.

    Why: Entender distribuição geográfica dos visitantes.
    """
    start_date = datetime.now(timezone.utc) - timedelta(days=days)

    result = await session.execute(
        select(Visitor.country, func.count(Visitor.id).label("count"))
        .where(Visitor.first_seen_at >= start_date, Visitor.country.isnot(None))
        .group_by(Visitor.country)
        .order_by(func.count(Visitor.id).desc())
        .limit(10)
    )

    return [{"country": row.country, "count": row.count} for row in result.all()]


async def get_recent_events(session: AsyncSession, limit: int = 20) -> list[dict]:
    """
    Obtém eventos recentes.

    Why: Monitorar atividade em tempo real.
    """
    result = await session.execute(
        select(AnalyticsEvent)
        .order_by(col(AnalyticsEvent.created_at).desc())
        .limit(limit)
    )

    events = result.scalars().all()
    return [
        {
            "id": str(e.id),
            "type": e.event_type.value,
            "page_url": e.page_url,
            "page_title": e.page_title,
            "created_at": e.created_at,
        }
        for e in events
    ]


async def get_recent_visitors(session: AsyncSession, limit: int = 10) -> list[dict]:
    """
    Obtém visitantes recentes.

    Why: Ver quem está visitando o site recentemente.
    """
    result = await session.execute(
        select(Visitor).order_by(col(Visitor.last_seen_at).desc()).limit(limit)
    )

    visitors = result.scalars().all()
    return [
        {
            "id": str(v.id),
            "display_name": v.display_name,
            "browser": v.browser_name,
            "os": v.os_name,
            "device": v.device_type,
            "country": v.country,
            "city": v.city,
            "visit_count": v.visit_count,
            "first_seen": v.first_seen_at,
            "last_seen": v.last_seen_at,
            "is_bot": v.is_bot,
        }
        for v in visitors
    ]


async def get_pageviews_by_day(session: AsyncSession, days: int = 30) -> list[dict]:
    """
    Obtém pageviews agrupados por dia.

    Why: Visualizar tendências de tráfego ao longo do tempo.
    """
    # Build a date range from start_date -> today (inclusive) and
    # aggregate counts per day. We also fill missing days with 0
    # so the chart renders a continuous time series.
    end_dt = datetime.now(timezone.utc)
    start_dt = end_dt - timedelta(days=days - 1)

    result = await session.execute(
        select(
            func.date(AnalyticsEvent.created_at).label("date"),
            func.count(AnalyticsEvent.id).label("views"),
        )
        .where(
            AnalyticsEvent.event_type == EventType.PAGE_VIEW,
            AnalyticsEvent.created_at >= start_dt,
            AnalyticsEvent.created_at <= end_dt,
        )
        .group_by(func.date(AnalyticsEvent.created_at))
        .order_by(func.date(AnalyticsEvent.created_at))
    )

    # Map SQL rows into a dict keyed by ISO date string
    rows = {str(row.date): row.views for row in result.all()}

    series: list[dict] = []
    for i in range(days):
        day = (start_dt + timedelta(days=i)).date()
        day_str = str(day)
        series.append({"date": day_str, "views": int(rows.get(day_str, 0))})

    return series


async def get_top_ips(
    session: AsyncSession, days: int = 30, limit: int = 10
) -> list[dict]:
    """
    Obtém os IPs mais frequentes.

    Why: Identificar visitantes mais ativos e detectar
         possíveis abusos ou bots.
    """
    start_date = datetime.now(timezone.utc) - timedelta(days=days)

    result = await session.execute(
        select(
            Visitor.ip_address,
            func.count(Visitor.id).label("count"),
            func.max(Visitor.last_seen_at).label("last_seen"),
            func.sum(Visitor.visit_count).label("total_visits"),
        )
        .where(
            Visitor.first_seen_at >= start_date,
            Visitor.ip_address.isnot(None),
            Visitor.ip_address != "unknown",
        )
        .group_by(Visitor.ip_address)
        .order_by(func.sum(Visitor.visit_count).desc())
        .limit(limit)
    )

    return [
        {
            "ip": row.ip_address,
            "visitors": row.count,
            "total_visits": row.total_visits or 0,
            "last_seen": row.last_seen,
        }
        for row in result.all()
    ]


@router.get("", response_class=HTMLResponse)
async def analytics_dashboard(
    request: Request,
    days: int = 30,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_admin_user),
):
    """Dashboard completo de analytics."""

    # Fetch all data in parallel would be better, but for simplicity:
    overview = await get_overview_stats(session, days)
    top_pages = await get_top_pages(session, days)
    top_referrers = await get_top_referrers(session, days)
    top_ips = await get_top_ips(session, days)
    device_stats = await get_device_stats(session, days)
    browser_stats = await get_browser_stats(session, days)
    country_stats = await get_country_stats(session, days)
    recent_events = await get_recent_events(session)
    recent_visitors = await get_recent_visitors(session)
    pageviews_by_day = await get_pageviews_by_day(session, days)

    return catalog.render(
        "admin/analytics.jinja",
        request=request,
        user=user,
        overview=overview,
        top_pages=top_pages,
        top_referrers=top_referrers,
        top_ips=top_ips,
        device_stats=device_stats,
        browser_stats=browser_stats,
        country_stats=country_stats,
        recent_events=recent_events,
        recent_visitors=recent_visitors,
        pageviews_by_day=pageviews_by_day,
        selected_days=days,
    )
