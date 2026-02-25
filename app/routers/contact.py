import logging
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse

from app.config import settings
from app.dependencies import (
    get_contact_page_service,
    get_contact_notification_service,
    get_contact_submission_service,
    limiter,
    render_or_fallback,
)
from app.services.contact import (
    ContactNotificationContext,
    ContactNotificationService,
)
from app.services.use_cases import ContactPageService, ContactSubmissionService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/contact", response_class=HTMLResponse)
async def contact_get(
    page_service: ContactPageService = Depends(get_contact_page_service),
) -> HTMLResponse:
    logger.info("Contact page rendered.")
    page = page_service.build_page()
    html = render_or_fallback(page.template, page.fallback_html, **page.context)
    return HTMLResponse(content=html)


@router.post("/contact", response_class=HTMLResponse)
@limiter.limit(settings.rate_limit)
async def contact_post(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    subject: str = Form(...),
    message: str = Form(...),
    csrf_token: str = Form(...),
    page_service: ContactPageService = Depends(get_contact_page_service),
    submission_service: ContactSubmissionService = Depends(
        get_contact_submission_service
    ),
    notification_service: ContactNotificationService = Depends(
        get_contact_notification_service
    ),
) -> HTMLResponse:
    client_ip = request.client.host if request.client else "unknown"
    request_id = getattr(request.state, "request_id", "unknown")
    logger.info("Contact form submission received.")

    submission = submission_service.process(
        name=name,
        email=email,
        subject=subject,
        message=message,
        csrf_token=csrf_token,
        client_ip=client_ip,
    )
    if not submission.is_valid:
        page = page_service.build_page(
            errors=submission.errors,
            form_data=submission.form_data,
        )
        html = render_or_fallback(page.template, page.fallback_html, **page.context)
        return HTMLResponse(content=html, status_code=submission.status_code)
    if submission.contact is None:
        page = page_service.build_page(
            errors={"form": "Unexpected contact submission state."},
            form_data=submission.form_data,
        )
        html = render_or_fallback(page.template, page.fallback_html, **page.context)
        return HTMLResponse(content=html, status_code=500)

    notification_context = ContactNotificationContext(
        request_id=request_id,
        client_ip=client_ip,
    )
    await notification_service.notify_submission(
        contact=submission.contact,
        context=notification_context,
    )

    logger.info(f"Contact form submitted successfully by {client_ip}.")
    page = page_service.build_page(
        success="Message sent successfully. Thank you for reaching out.",
    )
    html = render_or_fallback(page.template, page.fallback_html, **page.context)
    return HTMLResponse(content=html)
