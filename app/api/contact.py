import logging

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse

from app.core.config import settings
from app.core.dependencies import (
    get_contact_orchestrator,
    get_contact_page_service,
    limiter,
)
from app.core.logger import event_message
from app.core.security import _anonymize_identifier
from app.observability.events import LogEvent
from app.rendering.engine import render_page
from app.services import ContactPageService
from app.services.contact import ContactOrchestrator

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/contact", response_class=HTMLResponse)
async def contact_get(
    request: Request,
    page_service: ContactPageService = Depends(get_contact_page_service),
) -> HTMLResponse:
    logger.info(
        event_message(
            LogEvent.CONTACT_PAGE_RENDERED,
            path=request.url.path,
        )
    )
    user_agent = request.headers.get("user-agent", "")
    page = page_service.build_page(user_agent=user_agent)
    return render_page(page)


@router.post("/contact", response_class=HTMLResponse)
@limiter.limit(settings.rate_limit)
async def contact_post(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    subject: str = Form(...),
    message: str = Form(...),
    csrf_token: str = Form(...),
    orchestrator: ContactOrchestrator = Depends(get_contact_orchestrator),
) -> HTMLResponse:
    raw_ip = request.client.host if request.client else "unknown"
    client_ip = _anonymize_identifier(raw_ip, namespace="ip")
    user_agent = request.headers.get("user-agent", "")
    request_id = getattr(request.state, "request_id", "unknown")
    content_type = request.headers.get("content-type", "")

    logger.info(
        event_message(
            LogEvent.CONTACT_SUBMISSION_RECEIVED,
            path=request.url.path,
        )
    )

    result = await orchestrator.handle_submission(
        name=name,
        email=email,
        subject=subject,
        message=message,
        csrf_token=csrf_token,
        content_type=content_type,
        client_ip=client_ip,
        user_agent=user_agent,
        request_id=request_id,
    )
    return render_page(result.page, status_code=result.status_code)
