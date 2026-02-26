from functools import lru_cache
import logging
from pathlib import Path
from typing import Any

from jx import Catalog
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import settings
from app.services.analytics import AnalyticsService, build_analytics_service
from app.services.contact import (
    ContactNotificationService,
    EmailNotificationChannel,
    EmailNotificationConfig,
    WebhookNotificationChannel,
)
from app.services.profile import ProfileService
from app.services.use_cases import (
    AboutPageService,
    ContactPageService,
    ContactSubmissionService,
    HomePageService,
    ProjectsPageService,
)

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_profile_service() -> ProfileService:
    return ProfileService()


@lru_cache(maxsize=1)
def get_catalog() -> Catalog:
    logger.info("Initializing Jx catalog.")
    profile_globals = get_profile_service().get_profile_globals()
    catalog = Catalog(
        auto_reload=settings.debug,
        site_name=profile_globals.site_name,
        base_url=str(settings.base_url),
        nav_links=[
            {"href": "/", "label": "Home"},
            {"href": "/about", "label": "About"},
            {"href": "/projects", "label": "Projects"},
            {"href": "/contact", "label": "Contact"},
        ],
        social_links=profile_globals.social_links,
        profile_name=profile_globals.profile_name,
        profile_role=profile_globals.profile_role,
        profile_location=profile_globals.profile_location,
        profile_summary=profile_globals.profile_summary,
        analytics_enabled=settings.analytics_enabled,
    )
    prefixed_folders = (
        (Path("components/ui"), "ui"),
        (Path("components/layouts"), "layouts"),
        (Path("components/seo"), "seo"),
        (Path("components/nav"), "nav"),
        (Path("components/footer"), "footer"),
        (Path("components/cards"), "cards"),
        (Path("components/contact"), "contact"),
        (Path("components/markdown"), "markdown"),
        (Path("components/tags"), "tags"),
        (Path("components/pages"), "pages"),
    )
    for folder_path, prefix in prefixed_folders:
        if folder_path.exists():
            catalog.add_folder(folder_path, prefix=prefix)
            logger.info(f"Registered Jx folder={folder_path} with prefix=@{prefix}.")
        else:
            logger.debug(
                f"Skipping optional Jx folder={folder_path} because it does not exist."
            )
    return catalog


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


@lru_cache(maxsize=1)
def get_analytics_service() -> AnalyticsService:
    return build_analytics_service()


def render_template(template: str, **context: Any) -> str:
    """Render a Jx template without silent fallback behavior."""
    catalog = get_catalog()
    resolved_template = template
    if template.startswith("pages/"):
        resolved_template = f"@pages/{template.split('/', 1)[1]}"
    rendered = catalog.render(resolved_template, **context)
    logger.debug(
        f"Template rendered successfully: template={template} resolved={resolved_template}"
    )
    return rendered
