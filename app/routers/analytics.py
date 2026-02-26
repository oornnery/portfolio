import logging

from fastapi import APIRouter, Depends, Request

from app.dependencies import get_analytics_service
from app.schemas import AnalyticsTrackRequest, AnalyticsTrackResponse
from app.services.analytics import AnalyticsService

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])
logger = logging.getLogger(__name__)


@router.post("/track", response_model=AnalyticsTrackResponse)
async def track_analytics(
    payload: AnalyticsTrackRequest,
    request: Request,
    analytics_service: AnalyticsService = Depends(get_analytics_service),
) -> AnalyticsTrackResponse:
    request_id = getattr(request.state, "request_id", "unknown")
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "")

    result = analytics_service.ingest_events(
        payload.events,
        request_id=request_id,
        client_ip=client_ip,
        user_agent=user_agent,
    )

    message = "Events accepted."
    if result.rejected > 0:
        message = "Some events were rejected."
        logger.warning(
            f"Analytics ingestion completed with rejections request_id={request_id} rejected={result.rejected}."
        )

    return AnalyticsTrackResponse(
        accepted=result.accepted,
        rejected=result.rejected,
        message=message,
        errors=list(result.errors),
    )
