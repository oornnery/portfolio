from functools import lru_cache
import logging
from pathlib import Path
from typing import Any

from jx import Catalog
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import settings
from app.services.markdown import load_about
from app.services.seo import seo_for_page
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


def _normalize_social_links(raw: Any) -> dict[str, str]:
    fallback_links = {key: str(value) for key, value in settings.social_links.items()}
    if not isinstance(raw, dict):
        return fallback_links

    normalized: dict[str, str] = {}
    for key, value in raw.items():
        normalized_key = str(key).strip().lower()
        normalized_value = str(value).strip()
        if normalized_key and normalized_value:
            normalized[normalized_key] = normalized_value

    return normalized or fallback_links


@lru_cache(maxsize=1)
def get_profile_globals() -> dict[str, Any]:
    meta, _ = load_about()
    profile_name = str(meta.get("name") or settings.site_name).strip()
    profile_role = str(meta.get("role") or "Backend Engineer").strip()
    profile_location = str(meta.get("location") or "Sao Paulo, Brazil").strip()
    profile_summary = str(
        meta.get("description")
        or "I build reliable backend systems with Python, FastAPI, and PostgreSQL."
    ).strip()
    profile_social_links = _normalize_social_links(meta.get("social_links"))

    logger.info(
        f"Profile globals loaded from content with name={profile_name} and social_links_count={len(profile_social_links)}."
    )
    return {
        "site_name": profile_name or settings.site_name,
        "profile_name": profile_name or settings.site_name,
        "profile_role": profile_role or "Backend Engineer",
        "profile_location": profile_location or "Sao Paulo, Brazil",
        "profile_summary": profile_summary
        or "I build reliable backend systems with Python, FastAPI, and PostgreSQL.",
        "social_links": profile_social_links,
    }


@lru_cache(maxsize=1)
def get_catalog() -> Catalog:
    logger.info("Initializing Jx catalog.")
    profile_globals = get_profile_globals()
    return Catalog(
        Path("components"),
        auto_reload=settings.debug,
        site_name=profile_globals["site_name"],
        base_url=str(settings.base_url),
        nav_links=[
            {"href": "/", "label": "Home"},
            {"href": "/about", "label": "About"},
            {"href": "/projects", "label": "Projects"},
            {"href": "/contact", "label": "Contact"},
        ],
        social_links=profile_globals["social_links"],
        profile_name=profile_globals["profile_name"],
        profile_role=profile_globals["profile_role"],
        profile_location=profile_globals["profile_location"],
        profile_summary=profile_globals["profile_summary"],
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


def render_template(template: str, **context: Any) -> str:
    """Render a Jx template and fallback only to maintenance page on failure."""
    catalog = get_catalog()
    try:
        return catalog.render(template, **context)
    except Exception as exc:
        logger.exception(
            f"Template rendering failed for {template} with {exc.__class__.__name__}: {exc}"
        )
        if template == "pages/maintenance.jinja":
            raise

        logger.warning(
            f"Rendering maintenance page after failure in template={template}."
        )
        return catalog.render(
            "pages/maintenance.jinja",
            seo=seo_for_page(
                title="Maintenance",
                description="Service temporarily unavailable.",
                path="/maintenance",
            ),
            current_path="",
            message=(
                "We are performing maintenance right now. "
                "Please try again in a few minutes."
            ),
        )
