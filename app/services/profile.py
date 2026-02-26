from dataclasses import dataclass
import logging
from typing import Any

from app.config import settings
from app.services.markdown import load_about

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ProfileGlobals:
    site_name: str
    profile_name: str
    profile_role: str
    profile_location: str
    profile_summary: str
    social_links: dict[str, str]


class ProfileService:
    @staticmethod
    def _normalize_social_links(raw: Any) -> dict[str, str]:
        fallback_links = {
            key: str(value) for key, value in settings.social_links.items()
        }
        if not isinstance(raw, dict):
            return fallback_links

        normalized: dict[str, str] = {}
        for key, value in raw.items():
            normalized_key = str(key).strip().lower()
            normalized_value = str(value).strip()
            if normalized_key and normalized_value:
                normalized[normalized_key] = normalized_value

        return normalized or fallback_links

    def get_profile_globals(self) -> ProfileGlobals:
        about_content = load_about()
        frontmatter = about_content.frontmatter

        profile_name = str(frontmatter.name or settings.site_name).strip()
        profile_role = str(frontmatter.role or "Backend Engineer").strip()
        profile_location = str(frontmatter.location or "Sao Paulo, Brazil").strip()
        profile_summary = str(
            frontmatter.description
            or "I build reliable backend systems with Python, FastAPI, and PostgreSQL."
        ).strip()
        profile_social_links = self._normalize_social_links(frontmatter.social_links)

        logger.info(
            f"Profile globals loaded with name={profile_name} and social_links_count={len(profile_social_links)}."
        )

        return ProfileGlobals(
            site_name=profile_name or settings.site_name,
            profile_name=profile_name or settings.site_name,
            profile_role=profile_role or "Backend Engineer",
            profile_location=profile_location or "Sao Paulo, Brazil",
            profile_summary=profile_summary
            or "I build reliable backend systems with Python, FastAPI, and PostgreSQL.",
            social_links=profile_social_links,
        )
