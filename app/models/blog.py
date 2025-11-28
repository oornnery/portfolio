from datetime import datetime, timezone
from enum import Enum
from typing import Optional
import uuid

from pydantic import field_validator, ConfigDict
from sqlmodel import Field, Relationship, SQLModel, Column, JSON


# ============================================
# Helpers
# ============================================


def utc_now() -> datetime:
    """Return current UTC time as timezone-aware datetime."""
    return datetime.now(timezone.utc)


# ============================================
# Enums
# ============================================


class ReactionTypeEnum(str, Enum):
    """Available reaction types for blog posts"""

    LIKE = "like"
    LOVE = "love"
    FIRE = "fire"
    CLAP = "clap"
    THINKING = "thinking"
    ROCKET = "rocket"
    EYES = "eyes"


class PostCategoryEnum(str, Enum):
    """Available blog post categories"""

    TECH = "tech"
    DEV = "dev"
    TUTORIAL = "tutorial"
    CAREER = "career"
    PERSONAL = "personal"
    NEWS = "news"
    REVIEW = "review"
    OTHER = "other"


class LanguageEnum(str, Enum):
    """Supported languages"""

    EN = "en"
    PT = "pt"
    ES = "es"


# ============================================
# Base Models
# ============================================


class PostBase(SQLModel):
    """Base model for blog posts with common fields"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Building a Modern Portfolio with FastAPI and React",
                "slug": "building-modern-portfolio-fastapi-react",
                "description": "A comprehensive guide to building a full-stack portfolio application using FastAPI, React, and TypeScript.",
                "content": "# Introduction\n\nIn this tutorial, we'll build a modern portfolio...",
                "image": "https://example.com/images/portfolio-cover.jpg",
                "category": "tutorial",
                "tags": ["fastapi", "react", "typescript", "portfolio"],
                "draft": False,
                "lang": "en",
                "reading_time": 15,
            }
        }
    )

    title: str = Field(
        min_length=1,
        max_length=200,
        description="The title of the blog post. Should be descriptive and SEO-friendly.",
    )
    slug: str = Field(
        unique=True,
        index=True,
        min_length=1,
        max_length=200,
        description="URL-friendly identifier for the post. Must be lowercase with hyphens only.",
    )
    description: str = Field(
        min_length=1,
        max_length=500,
        description="A brief summary of the post for SEO and previews.",
    )
    content: str = Field(
        description="The full markdown content of the blog post.",
    )
    image: Optional[str] = Field(
        default=None,
        description="URL to the cover image for the post.",
    )
    category: str = Field(
        min_length=1,
        max_length=50,
        description="The category of the post (tech, tutorial, personal, etc.).",
    )
    tags: list[str] = Field(
        default=[],
        sa_column=Column(JSON),
        description="List of tags for categorization and search.",
    )
    draft: bool = Field(
        default=False,
        description="Whether the post is a draft (not publicly visible).",
    )
    lang: str = Field(
        default="en",
        max_length=5,
        description="Language code of the post (en, pt, es).",
    )
    reading_time: int = Field(
        default=0,
        ge=0,
        description="Estimated reading time in minutes. Auto-calculated if not provided.",
    )

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        """Ensure slug is URL-safe"""
        import re

        if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", v):
            raise ValueError("Slug must be lowercase alphanumeric with hyphens")
        return v


class Post(PostBase, table=True):
    """Database model for blog posts"""

    __tablename__ = "posts"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    published_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    views: int = Field(default=0, ge=0)

    # Relationships
    reactions: list["Reaction"] = Relationship(back_populates="post")


class PostCreate(PostBase):
    """Schema for creating a new blog post.

    All required fields must be provided. The reading_time will be
    auto-calculated based on content if not provided.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Getting Started with FastAPI",
                "slug": "getting-started-fastapi",
                "description": "A beginner-friendly guide to building APIs with FastAPI.",
                "content": "# Getting Started with FastAPI\n\nFastAPI is a modern, fast web framework...",
                "image": "https://example.com/fastapi-cover.jpg",
                "category": "tutorial",
                "tags": ["fastapi", "python", "api", "beginner"],
                "draft": False,
                "lang": "en",
            }
        }
    )


class PostUpdate(SQLModel):
    """Schema for updating an existing blog post.

    All fields are optional - only provided fields will be updated.
    The updated_at timestamp is automatically set on update.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Updated: Getting Started with FastAPI",
                "description": "An updated beginner-friendly guide with new examples.",
                "tags": ["fastapi", "python", "api", "beginner", "updated"],
            }
        }
    )

    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=200,
        description="Updated title of the post.",
    )
    description: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=500,
        description="Updated description/summary.",
    )
    content: Optional[str] = Field(
        default=None,
        description="Updated markdown content.",
    )
    image: Optional[str] = Field(
        default=None,
        description="Updated cover image URL.",
    )
    category: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=50,
        description="Updated category.",
    )
    tags: Optional[list[str]] = Field(
        default=None,
        description="Updated tags list.",
    )
    draft: Optional[bool] = Field(
        default=None,
        description="Update draft status.",
    )
    lang: Optional[str] = Field(
        default=None,
        max_length=5,
        description="Updated language code.",
    )
    reading_time: Optional[int] = Field(
        default=None,
        ge=0,
        description="Updated reading time.",
    )


class PostPublic(PostBase):
    """Schema for public post response.

    Includes all base fields plus server-generated fields like ID,
    timestamps, and view count. Used in list endpoints.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Building a Modern Portfolio",
                "slug": "building-modern-portfolio",
                "description": "A guide to building portfolio applications.",
                "content": "# Introduction\n\nIn this tutorial...",
                "image": "https://example.com/cover.jpg",
                "category": "tutorial",
                "tags": ["fastapi", "react"],
                "draft": False,
                "lang": "en",
                "reading_time": 15,
                "published_at": "2025-11-26T00:00:00Z",
                "updated_at": "2025-11-26T12:00:00Z",
                "views": 1234,
            }
        }
    )

    id: uuid.UUID = Field(description="Unique identifier for the post.")
    published_at: datetime = Field(description="When the post was first published.")
    updated_at: datetime = Field(description="When the post was last updated.")
    views: int = Field(description="Total number of views.")


class PostDetail(PostPublic):
    """Schema for detailed post response with reactions.

    Extends PostPublic with reaction counts. Used when fetching
    a single post by slug.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Building a Modern Portfolio",
                "slug": "building-modern-portfolio",
                "description": "A guide to building portfolio applications.",
                "content": "# Introduction\n\nIn this tutorial...",
                "image": "https://example.com/cover.jpg",
                "category": "tutorial",
                "tags": ["fastapi", "react"],
                "draft": False,
                "lang": "en",
                "reading_time": 15,
                "published_at": "2025-11-26T00:00:00Z",
                "updated_at": "2025-11-26T12:00:00Z",
                "views": 1234,
                "reactions_count": {"like": 42, "love": 15, "fire": 8},
            }
        }
    )

    reactions_count: dict[str, int] = Field(
        default={},
        description="Count of reactions by type (e.g., {'like': 42, 'love': 15}).",
    )


# ============================================
# Reaction Models
# ============================================


class ReactionBase(SQLModel):
    """Base model for reactions"""

    model_config = ConfigDict(json_schema_extra={"example": {"type": "like"}})

    type: str = Field(
        min_length=1,
        max_length=20,
        description="Type of reaction (like, love, fire, clap, thinking, rocket, eyes).",
    )


class Reaction(ReactionBase, table=True):
    """Database model for reactions"""

    __tablename__ = "reactions"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    post_id: uuid.UUID = Field(foreign_key="posts.id", index=True)
    count: int = Field(default=0, ge=0)

    # Relationships
    post: Optional[Post] = Relationship(back_populates="reactions")


class ReactionCreate(ReactionBase):
    """Schema for adding a reaction to a post.

    Available reaction types: like, love, fire, clap, thinking, rocket, eyes.
    """

    model_config = ConfigDict(json_schema_extra={"example": {"type": "like"}})


class ReactionPublic(ReactionBase):
    """Schema for public reaction response with count."""

    model_config = ConfigDict(
        json_schema_extra={"example": {"type": "like", "count": 42}}
    )

    count: int = Field(description="Total count of this reaction type.")


# ============================================
# Category and Tag Models
# ============================================


class CategoryCount(SQLModel):
    """Category with associated post count."""

    model_config = ConfigDict(
        json_schema_extra={"example": {"name": "tutorial", "count": 15}}
    )

    name: str = Field(description="Category name.")
    count: int = Field(description="Number of posts in this category.")


class TagCount(SQLModel):
    """Tag with associated post count."""

    model_config = ConfigDict(
        json_schema_extra={"example": {"name": "python", "count": 25}}
    )

    name: str = Field(description="Tag name.")
    count: int = Field(description="Number of posts with this tag.")


# ============================================
# Response Models
# ============================================


class PaginatedPostsResponse(SQLModel):
    """Paginated list of posts with metadata."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [],
                "total": 50,
                "page": 1,
                "per_page": 20,
                "pages": 3,
            }
        }
    )

    items: list[PostPublic] = Field(description="List of posts.")
    total: int = Field(description="Total number of posts matching the query.")
    page: int = Field(description="Current page number.")
    per_page: int = Field(description="Number of items per page.")
    pages: int = Field(description="Total number of pages.")


class ErrorResponse(SQLModel):
    """Standard error response format."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "error",
                "type": "not_found",
                "message": "Post not found",
                "detail": None,
            }
        }
    )

    status: str = Field(default="error", description="Error status.")
    type: str = Field(description="Error type identifier.")
    message: str = Field(description="Human-readable error message.")
    detail: Optional[str] = Field(default=None, description="Additional error details.")


class SuccessResponse(SQLModel):
    """Standard success response format."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "success",
                "message": "Operation completed successfully",
            }
        }
    )

    status: str = Field(default="success", description="Success status.")
    message: str = Field(description="Success message.")
