import logging
from typing import Callable

from pydantic import ValidationError

from app.domain.schemas import ContactForm
from app.core.security import generate_csrf_token, validate_csrf_token
from app.application.services.seo import seo_for_page
from app.application.use_cases.types import (
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
