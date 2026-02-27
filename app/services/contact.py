import logging
from typing import Callable

from pydantic import ValidationError

from app.core.logger import event_message
from app.core.security import (
    generate_csrf_token,
    is_allowed_form_content_type,
    validate_csrf_token,
)
from app.domain.schemas import AnalyticsEventName, AnalyticsTrackEvent, ContactForm
from app.infrastructure.notifications.email import (
    ContactNotificationContext,
    ContactNotificationService,
)
from app.observability.analytics import AnalyticsService
from app.observability.events import LogEvent
from app.observability.metrics import get_app_metrics
from app.services.seo import seo_for_page
from app.services.types import (
    ContactFormResult,
    ContactPageContext,
    ContactSubmissionResult,
    PageRenderData,
)

logger = logging.getLogger(__name__)


class ContactPageService:
    def __init__(
        self, csrf_token_factory: Callable[..., str] = generate_csrf_token
    ) -> None:
        self._csrf_token_factory = csrf_token_factory

    def build_page(
        self,
        *,
        user_agent: str = "",
        current_csrf: str | None = None,
        success: str = "",
        errors: dict[str, str] | None = None,
        form_data: dict[str, str] | None = None,
    ) -> PageRenderData:
        seo = seo_for_page(
            title="Contact",
            description="Get in touch with me.",
            path="/contact",
        )
        csrf_token = current_csrf or self._csrf_token_factory(user_agent=user_agent)
        return PageRenderData(
            template="pages/contact.jinja",
            context=ContactPageContext(
                seo=seo,
                csrf_token=csrf_token,
                success=success,
                errors=errors or {},
                form_data=form_data or {},
            ),
        )


class ContactSubmissionService:
    def __init__(
        self,
        csrf_validator: Callable[..., bool] = validate_csrf_token,
    ) -> None:
        self._csrf_validator = csrf_validator

    @staticmethod
    def _normalize_input(
        *,
        name: str,
        email: str,
        subject: str,
        message: str,
    ) -> dict[str, str]:
        return {
            "name": name.strip(),
            "email": email.strip(),
            "subject": subject.strip(),
            "message": message.strip(),
        }

    def process(
        self,
        *,
        name: str,
        email: str,
        subject: str,
        message: str,
        csrf_token: str,
        client_ip: str,
        user_agent: str,
    ) -> ContactSubmissionResult:
        form_data = self._normalize_input(
            name=name,
            email=email,
            subject=subject,
            message=message,
        )

        if not self._csrf_validator(csrf_token, user_agent=user_agent):
            logger.warning(
                f"Invalid or expired CSRF token for contact form submission from {client_ip}."
            )
            return ContactSubmissionResult(
                contact=None,
                form_data=form_data,
                errors={
                    "csrf": "Invalid or expired security token. Please reload the page."
                },
                status_code=403,
            )

        try:
            contact = ContactForm(
                name=form_data["name"],
                email=form_data["email"],
                subject=form_data["subject"],
                message=form_data["message"],
                csrf_token=csrf_token,
            )
            return ContactSubmissionResult(
                contact=contact,
                form_data=form_data,
                errors={},
                status_code=200,
            )
        except ValidationError as exc:
            errors: dict[str, str] = {}
            for err in exc.errors():
                loc = err.get("loc", ())
                field_name = str(loc[-1]) if loc else "form"
                errors[field_name] = err.get("msg", "Invalid value")
            logger.info(
                f"Contact form validation failed for {client_ip} with {len(errors)} error(s)."
            )
            return ContactSubmissionResult(
                contact=None,
                form_data=form_data,
                errors=errors,
                status_code=422,
            )


class ContactOrchestrator:
    """Orchestrates the full contact form submission lifecycle."""

    def __init__(
        self,
        page_service: ContactPageService,
        submission_service: ContactSubmissionService,
        notification_service: ContactNotificationService,
        analytics_service: AnalyticsService,
    ) -> None:
        self._page_service = page_service
        self._submission_service = submission_service
        self._notification_service = notification_service
        self._analytics_service = analytics_service

    def _track(
        self,
        event_name: AnalyticsEventName,
        *,
        request_id: str,
        client_ip: str,
        user_agent: str,
        metadata: dict[str, str] | None = None,
    ) -> None:
        self._analytics_service.ingest_events(
            [
                AnalyticsTrackEvent(
                    event_name=event_name,
                    page_path="/contact",
                    metadata=metadata or {},
                )
            ],
            request_id=request_id,
            client_ip=client_ip,
            user_agent=user_agent,
        )

    def _error_page(
        self,
        *,
        user_agent: str,
        errors: dict[str, str],
        form_data: dict[str, str],
    ) -> PageRenderData:
        return self._page_service.build_page(
            user_agent=user_agent,
            errors=errors,
            form_data=form_data,
        )

    async def handle_submission(
        self,
        *,
        name: str,
        email: str,
        subject: str,
        message: str,
        csrf_token: str,
        content_type: str,
        client_ip: str,
        user_agent: str,
        request_id: str,
    ) -> ContactFormResult:
        app_metrics = get_app_metrics()
        ctx = dict(request_id=request_id, client_ip=client_ip, user_agent=user_agent)
        form_data = {
            "name": name,
            "email": email,
            "subject": subject,
            "message": message,
        }

        self._track(
            AnalyticsEventName.CONTACT_ATTEMPT,
            **ctx,
            metadata={"source": "contact_form"},
        )

        if not is_allowed_form_content_type(content_type):
            app_metrics.record_contact_submission(outcome="unsupported_content_type")
            logger.warning(
                event_message(
                    LogEvent.CONTACT_SUBMISSION_REJECTED,
                    reason="unsupported_content_type",
                    content_type=content_type,
                    request_id=request_id,
                )
            )
            self._track(
                AnalyticsEventName.CONTACT_FAILURE,
                **ctx,
                metadata={"reason": "unsupported_content_type"},
            )
            page = self._error_page(
                user_agent=user_agent,
                errors={"form": "Unsupported content type."},
                form_data=form_data,
            )
            return ContactFormResult(
                page=page, status_code=415, outcome="unsupported_content_type"
            )

        submission = self._submission_service.process(
            name=name,
            email=email,
            subject=subject,
            message=message,
            csrf_token=csrf_token,
            client_ip=client_ip,
            user_agent=user_agent,
        )

        if not submission.is_valid:
            reason = "csrf" if "csrf" in submission.errors else "validation_error"
            app_metrics.record_contact_submission(outcome=reason)
            logger.info(
                event_message(
                    LogEvent.CONTACT_SUBMISSION_REJECTED,
                    reason=reason,
                    request_id=request_id,
                )
            )
            self._track(
                AnalyticsEventName.CONTACT_FAILURE,
                **ctx,
                metadata={"reason": reason},
            )
            page = self._error_page(
                user_agent=user_agent,
                errors=submission.errors,
                form_data=submission.form_data,
            )
            return ContactFormResult(
                page=page, status_code=submission.status_code, outcome=reason
            )

        if submission.contact is None:
            app_metrics.record_contact_submission(outcome="unexpected_submission_state")
            logger.error(
                event_message(
                    LogEvent.CONTACT_SUBMISSION_REJECTED,
                    reason="unexpected_submission_state",
                    request_id=request_id,
                )
            )
            self._track(
                AnalyticsEventName.CONTACT_FAILURE,
                **ctx,
                metadata={"reason": "unexpected_submission_state"},
            )
            page = self._error_page(
                user_agent=user_agent,
                errors={"form": "Unexpected contact submission state."},
                form_data=submission.form_data,
            )
            return ContactFormResult(
                page=page, status_code=500, outcome="unexpected_submission_state"
            )

        notification_context = ContactNotificationContext(
            request_id=request_id,
            client_ip=client_ip,
        )
        dispatch_result = await self._notification_service.notify_submission(
            contact=submission.contact,
            context=notification_context,
        )

        if (
            dispatch_result.has_channels
            and dispatch_result.all_failed
            and not dispatch_result.all_skipped
        ):
            app_metrics.record_contact_submission(outcome="notification_failed")
            logger.error(
                event_message(
                    LogEvent.CONTACT_SUBMISSION_REJECTED,
                    reason="notification_all_failed",
                    request_id=request_id,
                )
            )
            self._track(
                AnalyticsEventName.CONTACT_FAILURE,
                **ctx,
                metadata={"reason": "notification_all_failed"},
            )
            page = self._error_page(
                user_agent=user_agent,
                errors={
                    "form": (
                        "Your message could not be delivered right now. "
                        "Please try again in a few minutes."
                    )
                },
                form_data=submission.form_data,
            )
            return ContactFormResult(
                page=page, status_code=503, outcome="notification_failed"
            )

        if not dispatch_result.has_channels or dispatch_result.all_skipped:
            outcome = "accepted_no_channel"
        elif dispatch_result.any_success and any(
            not r.success for r in dispatch_result.results
        ):
            outcome = "success_partial"
        else:
            outcome = "success"

        app_metrics.record_contact_submission(outcome=outcome)
        logger.info(
            event_message(
                LogEvent.CONTACT_SUBMISSION_SUCCEEDED,
                request_id=request_id,
            )
        )
        self._track(
            AnalyticsEventName.CONTACT_SUCCESS,
            request_id=request_id,
            client_ip=client_ip,
            user_agent=user_agent,
        )
        page = self._page_service.build_page(
            user_agent=user_agent,
            success="Message sent successfully. Thank you for reaching out.",
        )
        return ContactFormResult(page=page, status_code=200, outcome=outcome)
