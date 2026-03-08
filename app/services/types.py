from dataclasses import dataclass
from typing import TypeAlias

from pydantic import BaseModel, ConfigDict, Field

from app.models.models import BlogPost, BlogTag, Project
from app.models.schemas import (
    AboutFrontmatter,
    CertificateItem,
    ContactForm,
    EducationItem,
    SEOMeta,
    SkillGroupItem,
    WorkExperienceItem,
)


class HomePageContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    seo: SEOMeta
    featured: tuple[Project, ...]
    latest_posts: tuple[BlogPost, ...]
    csrf_token: str
    current_path: str = "/"


class AboutPageContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    seo: SEOMeta
    meta: AboutFrontmatter
    hero_html: str
    about_html: str
    work_experience: tuple[WorkExperienceItem, ...] = ()
    education: tuple[EducationItem, ...] = ()
    certificates: tuple[CertificateItem, ...] = ()
    skill_groups: tuple[SkillGroupItem, ...] = ()
    current_path: str = "/about"


class ProjectsListPageContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    seo: SEOMeta
    projects: tuple[Project, ...]
    current_path: str = "/projects"


class ProjectDetailPageContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    seo: SEOMeta
    project: Project
    current_path: str = "/projects"


class ContactPageContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    seo: SEOMeta
    csrf_token: str
    success: str = ""
    errors: dict[str, str] = Field(default_factory=dict)
    form_data: dict[str, str] = Field(default_factory=dict)
    current_path: str = "/contact"


class BlogHomePageContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    seo: SEOMeta
    featured_posts: tuple[BlogPost, ...]
    recent_posts: tuple[BlogPost, ...]
    tags: tuple[BlogTag, ...]
    current_path: str = "/blog"


class BlogPostsPageContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    seo: SEOMeta
    posts: tuple[BlogPost, ...]
    current_path: str = "/blog"


class BlogPostDetailPageContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    seo: SEOMeta
    post: BlogPost
    previous_post: BlogPost | None = None
    next_post: BlogPost | None = None
    read_time_minutes: int = 1
    current_path: str = "/blog"


class BlogTagsPageContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    seo: SEOMeta
    tags: tuple[BlogTag, ...]
    posts: tuple[BlogPost, ...]
    selected_tag: str = ""
    current_path: str = "/blog"


PageContext: TypeAlias = (
    HomePageContext
    | AboutPageContext
    | ProjectsListPageContext
    | ProjectDetailPageContext
    | ContactPageContext
    | BlogHomePageContext
    | BlogPostsPageContext
    | BlogPostDetailPageContext
    | BlogTagsPageContext
)


@dataclass(frozen=True)
class PageRenderData:
    template: str
    context: PageContext


@dataclass(frozen=True)
class ContactSubmissionResult:
    contact: ContactForm | None
    form_data: dict[str, str]
    errors: dict[str, str]
    status_code: int

    @property
    def is_valid(self) -> bool:
        return self.contact is not None and not self.errors


@dataclass(frozen=True)
class ContactFormResult:
    """Result of the full contact form orchestration."""

    page: PageRenderData
    status_code: int
    outcome: str
