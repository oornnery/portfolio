import logging

from app.core.config import settings
from app.models.models import Project
from app.models.schemas import SEOMeta

logger = logging.getLogger(__name__)


def _join_url(base: str, path: str) -> str:
    return f"{base.rstrip('/')}/{path.lstrip('/')}"


def _absolute_asset_url(path_or_url: str | None) -> str:
    if not path_or_url:
        return _join_url(str(settings.base_url), settings.default_og_image)
    if path_or_url.startswith(("http://", "https://")):
        return path_or_url
    return _join_url(str(settings.base_url), path_or_url)


def _resolve_site_name(raw_site_name: str = "") -> str:
    if raw_site_name:
        return raw_site_name

    try:
        from app.infrastructure.markdown import load_about

        content_site_name = str(load_about().frontmatter.name).strip()
        if content_site_name:
            return content_site_name
    except Exception:
        logger.debug("Unable to resolve site name from markdown content.")

    return settings.site_name


def seo_for_page(
    title: str,
    description: str,
    path: str = "/",
    *,
    og_image: str = "",
    og_type: str = "website",
    site_name: str = "",
    keywords: list[str] | tuple[str, ...] = (),
) -> SEOMeta:
    resolved_og_image = og_image or settings.default_og_image
    resolved_site_name = _resolve_site_name(site_name)
    seo = SEOMeta(
        title=f"{title} | {resolved_site_name}",
        description=description[:160],
        canonical_url=_join_url(str(settings.base_url), path),
        og_image=_absolute_asset_url(resolved_og_image),
        og_type=og_type,
        keywords=list(keywords),
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
