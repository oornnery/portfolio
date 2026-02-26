import logging

from app.core.config import settings
from app.domain.models import Project
from app.domain.schemas import SEOMeta

logger = logging.getLogger(__name__)


def _join_url(base: str, path: str) -> str:
    return f"{base.rstrip('/')}/{path.lstrip('/')}"


def _absolute_asset_url(path_or_url: str | None) -> str:
    if not path_or_url:
        return _join_url(str(settings.base_url), settings.default_og_image)
    if path_or_url.startswith(("http://", "https://")):
        return path_or_url
    return _join_url(str(settings.base_url), path_or_url)


def _normalize_keywords(raw: object) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, (list, tuple, set)):
        return [str(item) for item in raw if str(item).strip()]
    if isinstance(raw, str):
        return [raw] if raw.strip() else []
    return []


def seo_for_page(
    title: str, description: str, path: str = "/", **kwargs: object
) -> SEOMeta:
    og_image_raw = kwargs.get("og_image", settings.default_og_image)
    og_image = None if og_image_raw is None else str(og_image_raw)
    og_type = str(kwargs.get("og_type", "website"))
    seo = SEOMeta(
        title=f"{title} | {settings.site_name}",
        description=description[:160],
        canonical_url=_join_url(str(settings.base_url), path),
        og_image=_absolute_asset_url(og_image),
        og_type=og_type,
        keywords=_normalize_keywords(kwargs.get("keywords")),
    )
    logger.debug(f"SEO metadata built for path={path} with title={seo.title}.")
    return seo


def seo_for_project(project: Project) -> SEOMeta:
    return seo_for_page(
        title=project.title,
        description=project.description,
        path=f"/projects/{project.slug}",
        og_image=project.thumbnail or settings.default_og_image,
        og_type="article",
        keywords=project.tags,
    )
