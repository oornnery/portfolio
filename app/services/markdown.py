from datetime import date
from functools import lru_cache
import logging
from pathlib import Path
from typing import Any

import bleach
import markdown
import yaml

from app.models import Project
from app.schemas import AboutContent, AboutFrontmatter

CONTENT_DIR = Path("content")
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


_BLEACH_ALLOWED_TAGS = sorted(
    {
        *bleach.sanitizer.ALLOWED_TAGS,
        "br",
        "div",
        "em",
        "li",
        "ol",
        "p",
        "pre",
        "code",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "blockquote",
        "hr",
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
        "img",
    }
)
_BLEACH_ALLOWED_ATTRS = {
    **bleach.sanitizer.ALLOWED_ATTRIBUTES,
    "a": ["href", "title", "target", "rel"],
    "div": ["class"],
    "img": ["src", "alt", "title", "width", "height", "loading"],
    "ol": ["start"],
    "span": ["class"],
    "table": ["class"],
    "code": ["class"],
    "td": ["colspan", "rowspan", "align"],
    "th": ["colspan", "rowspan", "align", "scope"],
}
_BLEACH_ALLOWED_PROTOCOLS = ["http", "https", "mailto"]


def _sanitize_html(html: str) -> str:
    cleaned = bleach.clean(
        html,
        tags=_BLEACH_ALLOWED_TAGS,
        attributes=_BLEACH_ALLOWED_ATTRS,
        protocols=_BLEACH_ALLOWED_PROTOCOLS,
        strip=True,
    )
    return bleach.linkify(cleaned, skip_tags={"pre", "code"})


def _parse_date(raw: Any) -> date | None:
    if isinstance(raw, date):
        return raw
    if isinstance(raw, str):
        try:
            return date.fromisoformat(raw)
        except ValueError:
            return None
    return None


def _as_str_list(raw: Any) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, (list, tuple, set)):
        return [str(item) for item in raw if str(item).strip()]
    if isinstance(raw, str):
        return [raw] if raw.strip() else []
    return []


@lru_cache(maxsize=1)
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


@lru_cache(maxsize=1)
def load_all_projects() -> tuple[Project, ...]:
    if not PROJECTS_DIR.exists():
        logger.info(
            f"Projects directory {PROJECTS_DIR} not found. Returning empty project list."
        )
        return ()

    projects: list[Project] = []
    for md_file in sorted(PROJECTS_DIR.glob("*.md"), reverse=True):
        meta, body = _parse_frontmatter(md_file)
        title = meta.get("title", md_file.stem.replace("-", " ").title())
        projects.append(
            Project(
                slug=str(meta.get("slug", md_file.stem)),
                title=str(title),
                description=str(meta.get("description", "")),
                content_html=_sanitize_html(_render_md(body)),
                thumbnail=str(meta.get("thumbnail", "")),
                tags=_as_str_list(meta.get("tags")),
                tech_stack=_as_str_list(meta.get("tech_stack")),
                github_url=str(meta.get("github_url"))
                if meta.get("github_url")
                else None,
                live_url=str(meta.get("live_url")) if meta.get("live_url") else None,
                date=_parse_date(meta.get("date")),
                featured=bool(meta.get("featured", False)),
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
