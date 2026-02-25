from functools import lru_cache
import logging
from pathlib import Path
from typing import Any

from jx import Catalog
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import settings
from app.services.contact import (
    ContactNotificationService,
    EmailNotificationChannel,
    EmailNotificationConfig,
    WebhookNotificationChannel,
)
from app.services.use_cases import (
    AboutPageService,
    ContactPageService,
    ContactSubmissionService,
    HomePageService,
    ProjectsPageService,
)

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_catalog() -> Catalog:
    logger.info("Initializing Jx catalog.")
    return Catalog(
        Path("components"),
        auto_reload=settings.debug,
        site_name=settings.site_name,
        base_url=str(settings.base_url),
        nav_links=[
            {"href": "/", "label": "Home"},
            {"href": "/about", "label": "About"},
            {"href": "/projects", "label": "Projects"},
            {"href": "/contact", "label": "Contact"},
        ],
        social_links=settings.social_links,
    )


limiter = Limiter(key_func=get_remote_address)


@lru_cache(maxsize=1)
def get_contact_notification_service() -> ContactNotificationService:
    logger.info("Initializing contact notification service.")
    email_config = EmailNotificationConfig(
        smtp_host=settings.smtp_host,
        smtp_port=settings.smtp_port,
        smtp_username=settings.smtp_username,
        smtp_password=settings.smtp_password,
        smtp_from=settings.smtp_from,
        smtp_use_tls=settings.smtp_use_tls,
        smtp_use_ssl=settings.smtp_use_ssl,
        smtp_timeout_seconds=settings.smtp_timeout_seconds,
        to_email=settings.contact_email_to,
        subject_prefix=settings.contact_email_subject,
        request_id_header=settings.request_id_header,
    )
    channels = (
        WebhookNotificationChannel(
            webhook_url=settings.contact_webhook_url,
            request_id_header=settings.request_id_header,
        ),
        EmailNotificationChannel(config=email_config),
    )
    return ContactNotificationService(channels=channels)


@lru_cache(maxsize=1)
def get_home_page_service() -> HomePageService:
    return HomePageService()


@lru_cache(maxsize=1)
def get_about_page_service() -> AboutPageService:
    return AboutPageService()


@lru_cache(maxsize=1)
def get_projects_page_service() -> ProjectsPageService:
    return ProjectsPageService()


@lru_cache(maxsize=1)
def get_contact_page_service() -> ContactPageService:
    return ContactPageService()


@lru_cache(maxsize=1)
def get_contact_submission_service() -> ContactSubmissionService:
    return ContactSubmissionService()


def render_or_fallback(template: str, fallback_html: str, **context: Any) -> str:
    """
    Render a Jx template when available.
    Return a simple fallback while templates are still being added.
    """
    catalog = get_catalog()
    try:
        return catalog.render(template, **context)
    except Exception as exc:
        logger.warning(
            f"Template {template} is not available yet "
            f"({exc.__class__.__name__}: {exc}). Returning fallback HTML."
        )
        return fallback_html
