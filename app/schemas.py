from __future__ import annotations

from datetime import date, datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl


class SEOMeta(BaseModel):
    title: str
    description: str = Field(max_length=160)
    og_image: str = ""
    og_type: str = "website"
    canonical_url: str = ""
    keywords: list[str] = Field(default_factory=list)


class ContactForm(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    subject: str = Field(min_length=3, max_length=200)
    message: str = Field(min_length=10, max_length=5000)
    csrf_token: str

    model_config = ConfigDict(extra="forbid")


class ContactResponse(BaseModel):
    success: bool
    message: str
    errors: dict[str, str] = Field(default_factory=dict)


class WorkExperienceItem(BaseModel):
    title: str = ""
    company: str = ""
    location: str = ""
    start_date: str = ""
    end_date: str = ""
    description: str = ""


class EducationItem(BaseModel):
    school: str = ""
    degree: str = ""
    start_date: str = ""
    end_date: str = ""


class CertificateItem(BaseModel):
    name: str = ""
    issuer: str = ""
    date: str = ""
    credential_id: str = ""


class AboutFrontmatter(BaseModel):
    title: str = "About"
    description: str = ""
    name: str = ""
    role: str = ""
    location: str = ""
    full_description: str = ""
    social_links: dict[str, HttpUrl] = Field(default_factory=dict)
    work_experience: list[WorkExperienceItem] = Field(default_factory=list)
    education: list[EducationItem] = Field(default_factory=list)
    certificates: list[CertificateItem] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)

    model_config = ConfigDict(extra="ignore")


class AboutContent(BaseModel):
    frontmatter: AboutFrontmatter
    body_markdown: str
    body_html: str


class ProjectFrontmatter(BaseModel):
    title: str = ""
    slug: str = ""
    description: str = ""
    thumbnail: str = ""
    tags: list[str] = Field(default_factory=list)
    tech_stack: list[str] = Field(default_factory=list)
    github_url: str = ""
    live_url: str = ""
    published_date: date | None = Field(default=None, alias="date")
    featured: bool = False

    model_config = ConfigDict(extra="ignore", populate_by_name=True)


class AnalyticsEventName(StrEnum):
    PAGE_VIEW = "page_view"
    CLICK = "click"
    OUTBOUND_CLICK = "outbound_click"
    SECTION_SCROLL = "section_scroll"
    CONTACT_ATTEMPT = "contact_attempt"
    CONTACT_SUCCESS = "contact_success"
    CONTACT_FAILURE = "contact_failure"


class AnalyticsTrackEvent(BaseModel):
    event_name: AnalyticsEventName
    page_path: str = Field(min_length=1, max_length=2048)
    element_id: str = Field(default="", max_length=256)
    element_text: str = Field(default="", max_length=512)
    target_url: str = Field(default="", max_length=2048)
    metadata: dict[str, Any] = Field(default_factory=dict)
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(extra="forbid")


class AnalyticsTrackRequest(BaseModel):
    events: list[AnalyticsTrackEvent] = Field(min_length=1, max_length=50)

    model_config = ConfigDict(extra="forbid")


class AnalyticsTrackResponse(BaseModel):
    accepted: int
    rejected: int
    message: str
    errors: list[str] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")
