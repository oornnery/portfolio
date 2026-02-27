from dataclasses import dataclass
from typing import TypeAlias

from pydantic import BaseModel, ConfigDict, Field

from app.domain.models import Project
from app.domain.schemas import ContactForm
from app.domain.schemas import AboutFrontmatter, SEOMeta


class HomePageContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    seo: SEOMeta
    featured: tuple[Project, ...]
    csrf_token: str
    current_path: str = "/"


class AboutPageContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    seo: SEOMeta
    meta: AboutFrontmatter
    content_html: str
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


PageContext: TypeAlias = (
    HomePageContext
    | AboutPageContext
    | ProjectsListPageContext
    | ProjectDetailPageContext
    | ContactPageContext
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
