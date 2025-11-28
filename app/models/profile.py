from datetime import datetime, timezone
from typing import Optional, List
import uuid
from sqlmodel import Field, SQLModel, Column, JSON
from pydantic import ConfigDict


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class WorkExperience(SQLModel):
    title: str
    company: str
    location: str
    start_date: str
    end_date: str
    description: str


class Education(SQLModel):
    degree: str
    school: str
    start_date: str
    end_date: str


class ProfileBase(SQLModel):
    """Base profile model."""
    
    name: str = Field(default="Fabio Souza")
    location: str = Field(default="São Paulo, Brazil")
    short_bio: str = Field(default="Full-stack Developer")
    email: str = Field(default="contact@example.com")
    phone: Optional[str] = Field(default=None)
    
    # Social Links
    website: Optional[str] = Field(default=None)
    github: Optional[str] = Field(default=None)
    linkedin: Optional[str] = Field(default=None)
    twitter: Optional[str] = Field(default=None)
    
    # Long content
    about_markdown: str = Field(default="")
    
    # Structured data
    work_experience: List[dict] = Field(default=[], sa_column=Column(JSON))
    education: List[dict] = Field(default=[], sa_column=Column(JSON))
    skills: List[str] = Field(default=[], sa_column=Column(JSON))

    model_config = ConfigDict(arbitrary_types_allowed=True)


class Profile(ProfileBase, table=True):
    """Database model for the user profile (singleton-ish)."""

    __tablename__ = "profile"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    updated_at: datetime = Field(default_factory=utc_now)
