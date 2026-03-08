from dataclasses import dataclass
from datetime import date as DateType


@dataclass(frozen=True)
class Project:
    slug: str
    title: str
    description: str
    content_html: str
    thumbnail: str = ""
    tags: tuple[str, ...] = ()
    tech_stack: tuple[str, ...] = ()
    github_url: str | None = None
    live_url: str | None = None
    date: DateType | None = None
    featured: bool = False


@dataclass(frozen=True)
class BlogPost:
    slug: str
    title: str
    description: str
    content_html: str
    tags: tuple[str, ...] = ()
    author: str = ""
    discussion_url: str = ""
    gist_url: str = ""
    gist_id: str = ""
    comments: tuple["BlogComment", ...] = ()
    date: DateType | None = None
    featured: bool = False


@dataclass(frozen=True)
class BlogTag:
    name: str
    count: int


@dataclass(frozen=True)
class BlogComment:
    author: str
    body: str
    created_at: str = ""
    profile_url: str = ""
    html_url: str = ""
    avatar_url: str = ""
