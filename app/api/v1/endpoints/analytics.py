"""
Analytics API endpoints.

Why: Recebe dados de fingerprinting do cliente e registra
     eventos de analytics para tracking de visitantes.

How: Endpoints para coletar fingerprint, registrar eventos
     e gerenciar sessões de visitantes.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.db import get_session
from app.models.analytics import (
    AnalyticsEvent,
    EventType,
    Visitor,
    generate_fingerprint_hash,
    generate_session_token,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["analytics"])


# =============================================================================
# Request/Response Models
# =============================================================================


class FingerprintData(BaseModel):
    """Client-side fingerprint data."""

    # Screen info
    screen_width: Optional[int] = None
    screen_height: Optional[int] = None
    viewport_width: Optional[int] = None
    viewport_height: Optional[int] = None
    color_depth: Optional[int] = None
    pixel_ratio: Optional[float] = None

    # Timezone/Language
    timezone: Optional[str] = None
    timezone_offset: Optional[int] = None
    language: Optional[str] = None

    # Features
    has_touch: Optional[bool] = None
    has_cookies: Optional[bool] = None
    has_local_storage: Optional[bool] = None
    has_session_storage: Optional[bool] = None
    has_webgl: Optional[bool] = None
    webgl_vendor: Optional[str] = None
    webgl_renderer: Optional[str] = None

    # Hashes
    canvas_hash: Optional[str] = None
    audio_hash: Optional[str] = None
    fonts_hash: Optional[str] = None
    plugins_hash: Optional[str] = None

    # Connection
    connection_type: Optional[str] = None


class IdentifyRequest(BaseModel):
    """Request to identify/create a visitor."""

    fingerprint: FingerprintData
    display_name: Optional[str] = Field(default=None, max_length=50)


class IdentifyResponse(BaseModel):
    """Response with visitor info."""

    visitor_id: str
    session_id: str
    is_new: bool


class TrackEventRequest(BaseModel):
    """Request to track an event."""

    event_type: EventType
    page_url: str
    page_title: Optional[str] = None
    referrer_url: Optional[str] = None
    event_data: Optional[dict[str, Any]] = None
    scroll_depth: Optional[int] = None
    time_on_page: Optional[int] = None


# =============================================================================
# Endpoints
# =============================================================================


@router.post("/identify", response_model=IdentifyResponse)
async def identify_visitor(
    request: Request,
    data: IdentifyRequest,
    session: AsyncSession = Depends(get_session),
) -> IdentifyResponse:
    """
    Identifica ou cria um visitor baseado no fingerprint.

    Why: Permite tracking de visitantes anônimos de forma
         consistente entre sessões.

    Returns:
        visitor_id e session_id para uso subsequente
    """
    # Get request metadata
    analytics_data = getattr(request.state, "analytics", {})
    ip_address = analytics_data.get("client_ip", "unknown")
    user_agent = analytics_data.get("user_agent", "")

    # Combine client fingerprint with user agent for hash
    fingerprint_dict = data.fingerprint.model_dump()
    fingerprint_dict["user_agent"] = user_agent
    fingerprint_hash = generate_fingerprint_hash(fingerprint_dict)

    # Try to find existing visitor
    stmt = select(Visitor).where(Visitor.fingerprint_hash == fingerprint_hash)
    result = await session.execute(stmt)
    visitor = result.scalar_one_or_none()

    is_new = False

    if visitor:
        # Update last seen and visit count
        visitor.last_seen_at = datetime.now(timezone.utc)
        visitor.visit_count += 1
        visitor.ip_address = ip_address  # Update IP (may change)

        if data.display_name:
            visitor.display_name = data.display_name
    else:
        # Create new visitor
        is_new = True
        visitor = Visitor(
            fingerprint_hash=fingerprint_hash,
            ip_address=ip_address,
            user_agent=user_agent,
            display_name=data.display_name,
            # Browser info from middleware
            browser_name=analytics_data.get("browser_name"),
            browser_version=analytics_data.get("browser_version"),
            os_name=analytics_data.get("os_name"),
            os_version=analytics_data.get("os_version"),
            device_type=analytics_data.get("device_type"),
            is_bot=analytics_data.get("is_bot", False),
            # Client fingerprint data
            screen_width=data.fingerprint.screen_width,
            screen_height=data.fingerprint.screen_height,
            viewport_width=data.fingerprint.viewport_width,
            viewport_height=data.fingerprint.viewport_height,
            color_depth=data.fingerprint.color_depth,
            pixel_ratio=data.fingerprint.pixel_ratio,
            language=data.fingerprint.language,
            timezone=data.fingerprint.timezone,
            timezone_offset=data.fingerprint.timezone_offset,
            connection_type=data.fingerprint.connection_type,
            has_touch=data.fingerprint.has_touch,
            has_cookies=data.fingerprint.has_cookies,
            has_local_storage=data.fingerprint.has_local_storage,
            has_session_storage=data.fingerprint.has_session_storage,
            has_webgl=data.fingerprint.has_webgl,
            webgl_vendor=data.fingerprint.webgl_vendor,
            webgl_renderer=data.fingerprint.webgl_renderer,
            canvas_hash=data.fingerprint.canvas_hash,
            audio_hash=data.fingerprint.audio_hash,
            fonts_hash=data.fingerprint.fonts_hash,
            plugins_hash=data.fingerprint.plugins_hash,
        )
        session.add(visitor)

    await session.commit()
    await session.refresh(visitor)

    # Get or create session
    session_token = analytics_data.get("session_id", generate_session_token())

    return IdentifyResponse(
        visitor_id=str(visitor.id),
        session_id=session_token,
        is_new=is_new,
    )


@router.post("/track", status_code=status.HTTP_202_ACCEPTED)
async def track_event(
    request: Request,
    data: TrackEventRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Registra um evento de analytics.

    Why: Tracking de pageviews, clicks, scrolls e outros
         eventos para análise de comportamento.
    """
    analytics_data = getattr(request.state, "analytics", {})
    session_id = analytics_data.get("session_id")

    # Get visitor from cookie or create minimal tracking
    visitor_id = request.cookies.get("_visitor_id")

    if not visitor_id:
        # Create anonymous event with server fingerprint
        fingerprint_hash = analytics_data.get("server_fingerprint", "unknown")

        # Try to find visitor by server fingerprint
        stmt = select(Visitor).where(Visitor.fingerprint_hash == fingerprint_hash)
        result = await session.execute(stmt)
        visitor = result.scalar_one_or_none()

        if visitor:
            visitor_id = str(visitor.id)

    if not visitor_id:
        # Can't track without visitor - return silently
        return {"status": "skipped", "reason": "no_visitor"}

    # Parse UTM parameters from URL
    from urllib.parse import parse_qs, urlparse

    parsed_url = urlparse(data.page_url)
    query_params = parse_qs(parsed_url.query)

    # Create event
    event = AnalyticsEvent(
        visitor_id=UUID(visitor_id),
        event_type=data.event_type,
        page_url=data.page_url,
        page_title=data.page_title,
        referrer_url=data.referrer_url,
        session_id=session_id,
        event_data=data.event_data or {},
        scroll_depth=data.scroll_depth,
        time_on_page=data.time_on_page,
        # UTM params
        utm_source=query_params.get("utm_source", [None])[0],
        utm_medium=query_params.get("utm_medium", [None])[0],
        utm_campaign=query_params.get("utm_campaign", [None])[0],
        utm_term=query_params.get("utm_term", [None])[0],
        utm_content=query_params.get("utm_content", [None])[0],
    )

    session.add(event)
    await session.commit()

    return {"status": "tracked", "event_id": str(event.id)}


@router.post("/pageview", status_code=status.HTTP_202_ACCEPTED)
async def track_pageview(
    request: Request,
    page_url: str,
    page_title: Optional[str] = None,
    referrer_url: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Endpoint simplificado para tracking de pageview.

    Why: Facilita tracking básico sem payload complexo.
    """
    data = TrackEventRequest(
        event_type=EventType.PAGE_VIEW,
        page_url=page_url,
        page_title=page_title,
        referrer_url=referrer_url,
    )
    return await track_event(request, data, session)
