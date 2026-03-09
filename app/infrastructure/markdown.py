import logging
import re
import threading
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx
import markdown
import nh3
from cachetools import TTLCache, cached
from cachetools.keys import hashkey
from pydantic import ValidationError
import yaml

from app.core.config import settings
from app.models.models import BlogComment, BlogPost, Project
from app.models.schemas import (
    AboutContent,
    AboutFrontmatter,
    BlogPostFrontmatter,
    CertificateItem,
    EducationItem,
    ProjectFrontmatter,
    SkillGroupItem,
    WorkExperienceItem,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONTENT_DIR = PROJECT_ROOT / "content"
PROJECTS_DIR = CONTENT_DIR / "projects"
BLOG_DIR = CONTENT_DIR / "blog"
logger = logging.getLogger(__name__)
_GIST_ID_PATTERN = re.compile(r"^[0-9a-fA-F]{8,40}$")


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


def _extract_description(markdown_body: str) -> str:
    lines = [line.strip() for line in markdown_body.splitlines() if line.strip()]
    for line in lines:
        if line.startswith(("#", "-", "*", ">")):
            continue
        compact = re.sub(r"\s+", " ", line).strip()
        if compact:
            return compact[:157].rstrip() + "..." if len(compact) > 160 else compact
    return "Post content."


_ABOUT_SECTION_PATTERN = re.compile(r"^\s*##\s+(.+?)\s*$")
_ABOUT_ENTRY_PATTERN = re.compile(r"^\s*###\s+(.+?)\s*$")
_ABOUT_META_PATTERN = re.compile(r"^\s*\*\*(.+?):\*\*\s*(.+?)\s*$")
_ABOUT_LIST_PATTERN = re.compile(r"^\s*[-*+]\s+(.+?)\s*$")


def _normalize_about_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")


def _split_markdown_sections(
    content: str, heading_pattern: re.Pattern[str]
) -> tuple[str, list[tuple[str, str]]]:
    preamble_lines: list[str] = []
    sections: list[tuple[str, str]] = []
    current_title = ""
    current_lines: list[str] = []

    for line in content.splitlines():
        match = heading_pattern.match(line)
        if match:
            if current_title:
                sections.append((current_title, "\n".join(current_lines).strip()))
            else:
                preamble_lines = (
                    current_lines.copy() if current_lines else preamble_lines
                )
            current_title = match.group(1).strip()
            current_lines = []
            continue

        if current_title:
            current_lines.append(line)
        else:
            preamble_lines.append(line)

    if current_title:
        sections.append((current_title, "\n".join(current_lines).strip()))

    return "\n".join(preamble_lines).strip(), sections


def _extract_about_metadata(content: str) -> tuple[dict[str, str], str]:
    lines = content.splitlines()
    metadata: dict[str, str] = {}
    index = 0

    while index < len(lines) and not lines[index].strip():
        index += 1

    while index < len(lines):
        stripped = lines[index].strip()
        if not stripped:
            index += 1
            continue

        match = _ABOUT_META_PATTERN.match(stripped)
        if not match:
            break

        metadata[_normalize_about_key(match.group(1))] = match.group(2).strip()
        index += 1

    while index < len(lines) and not lines[index].strip():
        index += 1

    return metadata, "\n".join(lines[index:]).strip()


def _split_period_value(value: str) -> tuple[str, str]:
    raw = value.strip()
    if not raw:
        return "", ""

    for delimiter in (" - ", " – ", " — "):
        if delimiter in raw:
            start, end = raw.split(delimiter, 1)
            return start.strip(), end.strip()

    return raw, ""


def _resolve_period_metadata(metadata: dict[str, str]) -> tuple[str, str]:
    start = metadata.get("start_date") or metadata.get("start") or ""
    end = metadata.get("end_date") or metadata.get("end") or ""
    if start or end:
        return start.strip(), end.strip()

    return _split_period_value(metadata.get("period") or metadata.get("dates") or "")


def _extract_skill_values(content: str) -> list[str]:
    skills: list[str] = []

    for line in content.splitlines():
        match = _ABOUT_LIST_PATTERN.match(line)
        if not match:
            continue
        value = match.group(1).strip()
        value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
        value = re.sub(r"[*_`]+", "", value)
        value = re.sub(r"\s+", " ", value).strip()
        if value:
            skills.append(value)

    if skills:
        return skills

    compact = " ".join(line.strip() for line in content.splitlines() if line.strip())
    if not compact:
        return []

    fallback_skills: list[str] = []
    for item in compact.split(","):
        candidate = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", item)
        candidate = re.sub(r"[*_`]+", "", candidate)
        candidate = re.sub(r"\s+", " ", candidate).strip()
        if candidate:
            fallback_skills.append(candidate)
    return fallback_skills


def _render_sanitized_markdown(content: str) -> str:
    if not content.strip():
        return ""
    return _sanitize_html(_render_md(content))


def _parse_about_work_experience(content: str) -> list[WorkExperienceItem]:
    _, entries = _split_markdown_sections(content, _ABOUT_ENTRY_PATTERN)
    items: list[WorkExperienceItem] = []

    for title, entry_content in entries:
        metadata, body = _extract_about_metadata(entry_content)
        start_date, end_date = _resolve_period_metadata(metadata)
        items.append(
            WorkExperienceItem(
                title=title.strip(),
                company=metadata.get("company", ""),
                location=metadata.get("location", ""),
                start_date=start_date,
                end_date=end_date,
                content_html=_render_sanitized_markdown(body),
            )
        )

    return items


def _parse_about_education(content: str) -> list[EducationItem]:
    _, entries = _split_markdown_sections(content, _ABOUT_ENTRY_PATTERN)
    items: list[EducationItem] = []

    for title, entry_content in entries:
        metadata, body = _extract_about_metadata(entry_content)
        start_date, end_date = _resolve_period_metadata(metadata)
        items.append(
            EducationItem(
                school=title.strip(),
                degree=metadata.get("degree", ""),
                start_date=start_date,
                end_date=end_date,
                details_html=_render_sanitized_markdown(body),
            )
        )

    return items


def _parse_about_certificates(content: str) -> list[CertificateItem]:
    _, entries = _split_markdown_sections(content, _ABOUT_ENTRY_PATTERN)
    items: list[CertificateItem] = []

    for title, entry_content in entries:
        metadata, body = _extract_about_metadata(entry_content)
        items.append(
            CertificateItem(
                name=title.strip(),
                issuer=metadata.get("issuer", ""),
                date=metadata.get("date", ""),
                credential_id=metadata.get("credential_id", ""),
                details_html=_render_sanitized_markdown(body),
            )
        )

    return items


def _parse_about_skill_groups(content: str) -> list[SkillGroupItem]:
    section_intro, entries = _split_markdown_sections(content, _ABOUT_ENTRY_PATTERN)
    groups: list[SkillGroupItem] = []

    if entries:
        for title, entry_content in entries:
            skills = _extract_skill_values(entry_content)
            if skills:
                groups.append(SkillGroupItem(title=title.strip(), skills=skills))
        return groups

    intro_skills = _extract_skill_values(section_intro)
    if intro_skills:
        groups.append(SkillGroupItem(title="Core", skills=intro_skills))
    return groups


def _parse_about_body(body: str) -> dict[str, Any]:
    hero_markdown, sections = _split_markdown_sections(body, _ABOUT_SECTION_PATTERN)

    section_map = {
        _normalize_about_key(title): content
        for title, content in sections
        if title.strip()
    }

    return {
        "hero_markdown": hero_markdown,
        "hero_html": _render_sanitized_markdown(hero_markdown),
        "about_markdown": section_map.get("about", ""),
        "about_html": _render_sanitized_markdown(section_map.get("about", "")),
        "work_experience": _parse_about_work_experience(
            section_map.get("work_experience", "")
        ),
        "education": _parse_about_education(section_map.get("education", "")),
        "certificates": _parse_about_certificates(section_map.get("certificates", "")),
        "skill_groups": _parse_about_skill_groups(section_map.get("skills", "")),
    }


def _extract_gist_id(gist_url: str) -> str:
    raw = gist_url.strip()
    if not raw:
        return ""

    if _GIST_ID_PATTERN.fullmatch(raw):
        return raw.lower()

    try:
        parsed = urlparse(raw)
    except ValueError:
        return ""

    host = parsed.netloc.lower()
    if host not in {"gist.github.com", "www.gist.github.com"}:
        return ""

    path_parts = [part for part in parsed.path.split("/") if part]
    if not path_parts:
        return ""

    candidate = path_parts[-1]
    if candidate.lower() == "raw" and len(path_parts) > 1:
        candidate = path_parts[-2]

    if _GIST_ID_PATTERN.fullmatch(candidate):
        return candidate.lower()
    return ""


def _github_api_headers() -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "site-app",
    }
    token = settings.github_token.strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _fetch_gist_payload(gist_id: str) -> dict[str, Any] | None:
    if not gist_id:
        return None

    url = f"https://api.github.com/gists/{gist_id}"
    try:
        with httpx.Client(
            follow_redirects=True,
            timeout=float(settings.github_api_timeout_seconds),
        ) as client:
            response = client.get(url, headers=_github_api_headers())
        if response.status_code == 404:
            logger.warning(f"Gist not found for gist_id={gist_id}.")
            return None
        response.raise_for_status()
        payload = response.json()
        if isinstance(payload, dict):
            return payload
    except (httpx.HTTPError, ValueError):
        logger.exception(f"Failed to fetch gist payload for gist_id={gist_id}.")
    return None


def _fetch_gist_raw_content(raw_url: str) -> str:
    if not raw_url:
        return ""
    try:
        with httpx.Client(
            follow_redirects=True,
            timeout=float(settings.github_api_timeout_seconds),
        ) as client:
            response = client.get(raw_url, headers={"User-Agent": "site-app"})
        response.raise_for_status()
        return response.text.strip()
    except httpx.HTTPError:
        logger.exception(f"Failed to fetch gist raw content from raw_url={raw_url}.")
        return ""


def _pick_gist_file(
    files: dict[str, Any], file_hint: str = ""
) -> dict[str, Any] | None:
    if not files:
        return None

    hint = file_hint.strip()
    if hint:
        if hint in files and isinstance(files[hint], dict):
            return files[hint]
        lower_hint = hint.lower()
        for filename, file_data in files.items():
            if filename.lower() == lower_hint and isinstance(file_data, dict):
                return file_data

    for filename, file_data in files.items():
        if filename.lower().endswith(".md") and isinstance(file_data, dict):
            return file_data

    for file_data in files.values():
        if isinstance(file_data, dict):
            return file_data
    return None


def _extract_gist_markdown(gist_payload: dict[str, Any], file_hint: str = "") -> str:
    files = gist_payload.get("files")
    if not isinstance(files, dict):
        return ""

    selected = _pick_gist_file(files, file_hint)
    if selected is None:
        return ""

    content = selected.get("content")
    truncated = bool(selected.get("truncated"))
    if isinstance(content, str) and content.strip() and not truncated:
        return content.strip()

    raw_url = str(selected.get("raw_url") or "").strip()
    if raw_url:
        return _fetch_gist_raw_content(raw_url)

    if isinstance(content, str):
        return content.strip()
    return ""


def _format_github_timestamp(raw: str) -> str:
    if not raw:
        return ""
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        return parsed.strftime("%b %d, %Y")
    except ValueError:
        return raw


def _fetch_gist_comments(gist_id: str) -> tuple[BlogComment, ...]:
    if not gist_id:
        return ()

    url = f"https://api.github.com/gists/{gist_id}/comments"
    try:
        with httpx.Client(
            follow_redirects=True,
            timeout=float(settings.github_api_timeout_seconds),
        ) as client:
            response = client.get(
                url,
                headers=_github_api_headers(),
                params={"per_page": str(settings.github_gist_comments_limit)},
            )
        if response.status_code == 404:
            logger.warning(f"Gist comments not found for gist_id={gist_id}.")
            return ()
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, list):
            return ()

        comments: list[BlogComment] = []
        for item in payload:
            if not isinstance(item, dict):
                continue
            user = item.get("user")
            user_data = user if isinstance(user, dict) else {}
            body = str(item.get("body") or "").strip()
            if not body:
                continue

            comments.append(
                BlogComment(
                    author=str(user_data.get("login") or "GitHub user"),
                    body=body,
                    created_at=_format_github_timestamp(
                        str(item.get("created_at") or "")
                    ),
                    profile_url=str(user_data.get("html_url") or "").strip(),
                    html_url=str(item.get("html_url") or "").strip(),
                    avatar_url=str(user_data.get("avatar_url") or "").strip(),
                )
            )

        return tuple(comments)
    except (httpx.HTTPError, ValueError):
        logger.exception(f"Failed to fetch gist comments for gist_id={gist_id}.")
        return ()


def _gist_comments_url(gist_url: str) -> str:
    url = gist_url.strip()
    if not url:
        return ""
    if "#comments" in url:
        return url
    return f"{url}#comments"


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
    body_markdown = body or "Content coming soon."
    parsed_about = _parse_about_body(body_markdown)
    sanitized = _render_sanitized_markdown(body_markdown)
    logger.info(f"About content loaded from {about_path}.")
    return AboutContent(
        frontmatter=frontmatter,
        body_markdown=body_markdown,
        body_html=sanitized,
        hero_markdown=parsed_about["hero_markdown"],
        hero_html=parsed_about["hero_html"],
        about_markdown=parsed_about["about_markdown"],
        about_html=parsed_about["about_html"],
        work_experience=parsed_about["work_experience"],
        education=parsed_about["education"],
        certificates=parsed_about["certificates"],
        skill_groups=parsed_about["skill_groups"],
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
                tags=tuple(frontmatter.tags),
                tech_stack=tuple(frontmatter.tech_stack),
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


@cached(cache=_content_cache, key=lambda: hashkey("all_blog_posts"), lock=_cache_lock)
def load_all_blog_posts() -> tuple[BlogPost, ...]:
    if not BLOG_DIR.exists():
        logger.info(f"Blog directory {BLOG_DIR} not found. Returning empty post list.")
        return ()

    posts: list[BlogPost] = []
    for md_file in sorted(BLOG_DIR.glob("*.md"), reverse=True):
        meta, body = _parse_frontmatter(md_file)
        try:
            frontmatter = BlogPostFrontmatter.model_validate(meta)
        except ValidationError:
            logger.exception(f"Invalid blog post frontmatter in file: {md_file}")
            continue

        if frontmatter.draft and not settings.debug:
            logger.info(f"Skipping draft blog post in file: {md_file}")
            continue

        resolved_title = frontmatter.title or md_file.stem.replace("-", " ").title()
        resolved_slug = frontmatter.slug or md_file.stem
        gist_url = frontmatter.gist_url.strip()
        gist_id = _extract_gist_id(gist_url)
        if gist_url and not gist_id:
            logger.warning(
                f"Invalid gist_url for blog post slug={resolved_slug}: gist_url={gist_url}"
            )

        body_markdown = body.strip()
        if not body_markdown and gist_id:
            gist_payload = _fetch_gist_payload(gist_id)
            if gist_payload is not None:
                body_markdown = _extract_gist_markdown(
                    gist_payload, frontmatter.gist_file
                )
        if not body_markdown:
            body_markdown = "Content coming soon."

        resolved_description = (
            frontmatter.description.strip()
            if frontmatter.description.strip()
            else _extract_description(body_markdown)
        )
        comments = _fetch_gist_comments(gist_id) if gist_id else ()
        resolved_discussion_url = frontmatter.discussion_url.strip()
        if gist_url:
            resolved_discussion_url = _gist_comments_url(gist_url)

        posts.append(
            BlogPost(
                slug=resolved_slug,
                title=resolved_title,
                description=resolved_description,
                content_html=_sanitize_html(_render_md(body_markdown)),
                tags=tuple(frontmatter.tags),
                author=frontmatter.author.strip(),
                discussion_url=resolved_discussion_url,
                gist_url=gist_url,
                gist_id=gist_id,
                comments=comments,
                date=frontmatter.published_date,
                featured=frontmatter.featured,
            )
        )

    sorted_posts = sorted(
        posts,
        key=lambda post: (post.date is not None, post.date, post.slug),
        reverse=True,
    )
    logger.info(f"Loaded {len(sorted_posts)} blog post(s) from {BLOG_DIR}.")
    return tuple(sorted_posts)


def get_blog_post_by_slug(slug: str) -> BlogPost | None:
    post = next((post for post in load_all_blog_posts() if post.slug == slug), None)
    if post is None:
        logger.info(f"Blog post not found for slug={slug}.")
    return post
