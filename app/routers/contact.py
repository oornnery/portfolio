import logging
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse

from app.config import settings
from app.dependencies import (
    get_analytics_service,
    get_contact_page_service,
    get_contact_notification_service,
    get_contact_submission_service,
    limiter,
    render_template,
)
from app.schemas import AnalyticsEventName, AnalyticsTrackEvent
from app.services.contact import (
    ContactNotificationContext,
    ContactNotificationService,
)
from app.services.analytics import AnalyticsService
from app.security import is_allowed_form_content_type
from app.services.use_cases import ContactPageService, ContactSubmissionService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/contact", response_class=HTMLResponse)
async def contact_get(
    request: Request,
    page_service: ContactPageService = Depends(get_contact_page_service),
) -> HTMLResponse:
    logger.info("Contact page rendered.")
    user_agent = request.headers.get("user-agent", "")
    page = page_service.build_page(user_agent=user_agent)
    html = render_template(page.template, **page.context)
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
    analytics_service: AnalyticsService = Depends(get_analytics_service),
) -> HTMLResponse:
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "")
    request_id = getattr(request.state, "request_id", "unknown")
    content_type = request.headers.get("content-type", "")
    logger.info("Contact form submission received.")
    analytics_service.ingest_events(
        [
            AnalyticsTrackEvent(
                event_name=AnalyticsEventName.CONTACT_ATTEMPT,
                page_path="/contact",
                metadata={"subject": subject[:120]},
            )
        ],
        request_id=request_id,
        client_ip=client_ip,
        user_agent=user_agent,
    )

    if not is_allowed_form_content_type(content_type):
        logger.warning(
            f"Invalid content-type for contact submission: {content_type} request_id={request_id}."
        )
        page = page_service.build_page(
            user_agent=user_agent,
            errors={"form": "Unsupported content type."},
            form_data={
                "name": name,
                "email": email,
                "subject": subject,
                "message": message,
            },
        )
        html = render_template(page.template, **page.context)
        analytics_service.ingest_events(
            [
                AnalyticsTrackEvent(
                    event_name=AnalyticsEventName.CONTACT_FAILURE,
                    page_path="/contact",
                    metadata={"reason": "unsupported_content_type"},
                )
            ],
            request_id=request_id,
            client_ip=client_ip,
            user_agent=user_agent,
        )
        return HTMLResponse(content=html, status_code=415)

    submission = submission_service.process(
        name=name,
        email=email,
        subject=subject,
        message=message,
        csrf_token=csrf_token,
        client_ip=client_ip,
        user_agent=user_agent,
    )
    if not submission.is_valid:
        failure_reason = "csrf" if "csrf" in submission.errors else "validation_error"
        page = page_service.build_page(
            user_agent=user_agent,
            errors=submission.errors,
            form_data=submission.form_data,
        )
        html = render_template(page.template, **page.context)
        analytics_service.ingest_events(
            [
                AnalyticsTrackEvent(
                    event_name=AnalyticsEventName.CONTACT_FAILURE,
                    page_path="/contact",
                    metadata={"reason": failure_reason},
                )
            ],
            request_id=request_id,
            client_ip=client_ip,
            user_agent=user_agent,
        )
        return HTMLResponse(content=html, status_code=submission.status_code)
    if submission.contact is None:
        page = page_service.build_page(
            user_agent=user_agent,
            errors={"form": "Unexpected contact submission state."},
            form_data=submission.form_data,
        )
        html = render_template(page.template, **page.context)
        analytics_service.ingest_events(
            [
                AnalyticsTrackEvent(
                    event_name=AnalyticsEventName.CONTACT_FAILURE,
                    page_path="/contact",
                    metadata={"reason": "unexpected_submission_state"},
                )
            ],
            request_id=request_id,
            client_ip=client_ip,
            user_agent=user_agent,
        )
        return HTMLResponse(content=html, status_code=500)

    notification_context = ContactNotificationContext(
        request_id=request_id,
        client_ip=client_ip,
    )
    dispatch_result = await notification_service.notify_submission(
        contact=submission.contact,
        context=notification_context,
    )
    if dispatch_result.has_channels and dispatch_result.all_failed and not dispatch_result.all_skipped:
        logger.error(
            f"All contact notification channels failed for request_id={request_id}."
        )
        page = page_service.build_page(
            user_agent=user_agent,
            errors={
                "form": (
                    "Your message could not be delivered right now. "
                    "Please try again in a few minutes."
                )
            },
            form_data=submission.form_data,
        )
        html = render_template(page.template, **page.context)
        analytics_service.ingest_events(
            [
                AnalyticsTrackEvent(
                    event_name=AnalyticsEventName.CONTACT_FAILURE,
                    page_path="/contact",
                    metadata={"reason": "notification_all_failed"},
                )
            ],
            request_id=request_id,
            client_ip=client_ip,
            user_agent=user_agent,
        )
        return HTMLResponse(content=html, status_code=503)

    logger.info(f"Contact form submitted successfully by {client_ip}.")
    page = page_service.build_page(
        user_agent=user_agent,
        success="Message sent successfully. Thank you for reaching out.",
    )
    html = render_template(page.template, **page.context)
    analytics_service.ingest_events(
        [
            AnalyticsTrackEvent(
                event_name=AnalyticsEventName.CONTACT_SUCCESS,
                page_path="/contact",
            )
        ],
        request_id=request_id,
        client_ip=client_ip,
        user_agent=user_agent,
    )
    return HTMLResponse(content=html)
