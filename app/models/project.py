from datetime import datetime, timezone
from typing import Optional
import uuid
from sqlmodel import Field, SQLModel, Column, JSON
from pydantic import ConfigDict


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ProjectBase(SQLModel):
    """Base model for projects."""

    title: str = Field(min_length=1, max_length=200)
    slug: str = Field(unique=True, index=True, min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=500)
    content: str = Field(default="", description="Full markdown content")
    image: Optional[str] = Field(default=None)
    tech_stack: list[str] = Field(default=[], sa_column=Column(JSON))
    category: str = Field(default="other")
    github_url: Optional[str] = Field(default=None)
    demo_url: Optional[str] = Field(default=None)
    featured: bool = Field(default=False)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Portfolio Website",
                "slug": "portfolio-website",
                "description": "Full-stack portfolio with FastAPI and React",
                "tech_stack": ["FastAPI", "React", "TypeScript", "PostgreSQL"],
                "category": "web",
                "github_url": "https://github.com/user/portfolio",
                "demo_url": "https://portfolio.example.com",
                "featured": True,
            }
        }
    )


class Project(ProjectBase, table=True):
    """Database model for projects."""

    __tablename__ = "projects"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    github_stars: int = Field(default=0, ge=0)
    github_forks: int = Field(default=0, ge=0)


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    image: Optional[str] = None
    tech_stack: Optional[list[str]] = None
    category: Optional[str] = None
    github_url: Optional[str] = None
    demo_url: Optional[str] = None
    featured: Optional[bool] = None


class ProjectPublic(ProjectBase):
    id: uuid.UUID
    created_at: datetime
    github_stars: int
    github_forks: int
