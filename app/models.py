from dataclasses import dataclass, field
from datetime import date as DateType


@dataclass(frozen=True)
class Project:
    slug: str
    title: str
    description: str
    content_html: str
    thumbnail: str = ""
    tags: list[str] = field(default_factory=list)
    tech_stack: list[str] = field(default_factory=list)
    github_url: str | None = None
    live_url: str | None = None
    date: DateType | None = None
    featured: bool = False
