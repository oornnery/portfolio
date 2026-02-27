import logging
import threading
from pathlib import Path
from typing import Any

import markdown
import nh3
from cachetools import TTLCache, cached
from cachetools.keys import hashkey
from pydantic import ValidationError
import yaml

from app.core.config import settings
from app.domain.models import Project
from app.domain.schemas import AboutContent, AboutFrontmatter, ProjectFrontmatter

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONTENT_DIR = PROJECT_ROOT / "content"
PROJECTS_DIR = CONTENT_DIR / "projects"
logger = logging.getLogger(__name__)


def _parse_frontmatter(filepath: Path) -> tuple[dict[str, Any], str]:
    if not filepath.exists():
        return {}, ""

    try:
        text = filepath.read_text(encoding="utf-8")
    except OSError:
        logger.exception(f"Failed to read markdown file: {filepath}")
        return {}, ""

    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            _, fm, body = parts
            try:
                meta = yaml.safe_load(fm) or {}
            except yaml.YAMLError:
                logger.exception(f"Invalid YAML frontmatter in file: {filepath}")
                meta = {}
            return meta, body.strip()
    return {}, text.strip()


def _render_md(content: str) -> str:
    if not content:
        return ""
    return markdown.markdown(
        content,
        extensions=["fenced_code", "codehilite", "tables", "toc", "attr_list"],
    )


_NH3_ALLOWED_TAGS = {
    "a",
    "abbr",
    "acronym",
    "b",
    "blockquote",
    "br",
    "code",
    "div",
    "em",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "hr",
    "i",
    "img",
    "li",
    "ol",
    "p",
    "pre",
    "span",
    "strong",
    "table",
    "tbody",
    "td",
    "tfoot",
    "th",
    "thead",
    "tr",
    "ul",
}

_NH3_ALLOWED_ATTRS: dict[str, set[str]] = {
    "a": {"href", "title", "target"},
    "div": {"class"},
    "img": {"src", "alt", "title", "width", "height", "loading"},
    "ol": {"start"},
    "span": {"class"},
    "table": {"class"},
    "code": {"class"},
    "td": {"colspan", "rowspan", "align"},
    "th": {"colspan", "rowspan", "align", "scope"},
}

_NH3_URL_SCHEMES = {"http", "https", "mailto"}


def _sanitize_html(html: str) -> str:
    return nh3.clean(
        html,
        tags=_NH3_ALLOWED_TAGS,
        attributes=_NH3_ALLOWED_ATTRS,
        url_schemes=_NH3_URL_SCHEMES,
        link_rel="noopener noreferrer",
        strip_comments=True,
    )


def _build_content_cache() -> TTLCache:
    ttl = settings.markdown_cache_ttl
    if ttl <= 0:
        ttl = 60 * 60 * 24 * 365
    return TTLCache(maxsize=16, ttl=ttl)


_content_cache: TTLCache = _build_content_cache()
_cache_lock = threading.Lock()


@cached(cache=_content_cache, key=lambda: hashkey("about"), lock=_cache_lock)
def load_about() -> AboutContent:
    about_path = CONTENT_DIR / "about.md"
    meta, body = _parse_frontmatter(about_path)
    frontmatter = AboutFrontmatter.model_validate(meta)

    full_description = frontmatter.full_description.strip()
    body_markdown = full_description or body or "Content coming soon."
    rendered = _render_md(body_markdown)
    sanitized = _sanitize_html(rendered)
    logger.info(f"About content loaded from {about_path}.")
    return AboutContent(
        frontmatter=frontmatter,
        body_markdown=body_markdown,
        body_html=sanitized,
    )


@cached(cache=_content_cache, key=lambda: hashkey("all_projects"), lock=_cache_lock)
def load_all_projects() -> tuple[Project, ...]:
    if not PROJECTS_DIR.exists():
        logger.info(
            f"Projects directory {PROJECTS_DIR} not found. Returning empty project list."
        )
        return ()

    projects: list[Project] = []
    for md_file in sorted(PROJECTS_DIR.glob("*.md"), reverse=True):
        meta, body = _parse_frontmatter(md_file)
        try:
            frontmatter = ProjectFrontmatter.model_validate(meta)
        except ValidationError:
            logger.exception(f"Invalid project frontmatter in file: {md_file}")
            continue

        resolved_title = frontmatter.title or md_file.stem.replace("-", " ").title()
        resolved_slug = frontmatter.slug or md_file.stem
        projects.append(
            Project(
                slug=resolved_slug,
                title=resolved_title,
                description=frontmatter.description,
                content_html=_sanitize_html(_render_md(body)),
                thumbnail=frontmatter.thumbnail,
                tags=frontmatter.tags,
                tech_stack=frontmatter.tech_stack,
                github_url=frontmatter.github_url or None,
                live_url=frontmatter.live_url or None,
                date=frontmatter.published_date,
                featured=frontmatter.featured,
            )
        )
    logger.info(f"Loaded {len(projects)} project(s) from {PROJECTS_DIR}.")
    return tuple(projects)


def get_project_by_slug(slug: str) -> Project | None:
    project = next(
        (project for project in load_all_projects() if project.slug == slug), None
    )
    if project is None:
        logger.info(f"Project not found for slug={slug}.")
    return project
