"""
Blog API endpoints for managing posts, reactions, categories, and tags.

This module provides a complete REST API for a blog system with:
- Full CRUD operations for posts
- Reaction system (like, love, fire, etc.)
- Category and tag aggregation
- Rate limiting for all endpoints
- Comprehensive error handling
"""

import re
from datetime import datetime, timezone
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.db import get_session
from app.models.blog import (
    CategoryCount,
    ErrorResponse,
    Post,
    PostCreate,
    PostDetail,
    PostPublic,
    PostUpdate,
    Reaction,
    ReactionCreate,
    ReactionPublic,
    ReactionTypeEnum,
    TagCount,
)

router = APIRouter(
    prefix="/blog",
    tags=["Blog"],
    responses={
        429: {
            "description": "Rate limit exceeded",
            "content": {
                "application/json": {
                    "example": {"error": "Rate limit exceeded", "retry_after": 60}
                }
            },
        },
        500: {
            "description": "Internal server error",
            "model": ErrorResponse,
        },
    },
)

# Rate limiter instance
limiter = Limiter(key_func=get_remote_address)


# ============================================
# Type Aliases for better documentation
# ============================================

SlugPath = Annotated[
    str,
    Path(
        description="URL-friendly post identifier (lowercase with hyphens)",
        min_length=1,
        max_length=200,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
        examples=["building-modern-portfolio", "getting-started-fastapi"],
    ),
]

CategoryQuery = Annotated[
    Optional[str],
    Query(
        description="Filter posts by category",
        examples=["tutorial", "tech", "personal"],
    ),
]

TagQuery = Annotated[
    Optional[str],
    Query(
        description="Filter posts by tag",
        examples=["python", "fastapi", "react"],
    ),
]

SearchQuery = Annotated[
    Optional[str],
    Query(
        description="Search in post title and description",
        min_length=2,
        max_length=100,
        examples=["fastapi tutorial", "react hooks"],
    ),
]


# ============================================
# Helper Functions
# ============================================


def calculate_reading_time(content: str) -> int:
    """
    Calculate reading time in minutes based on word count.

    Uses an average reading speed of 200 words per minute.
    Returns minimum of 1 minute.
    """
    words = len(re.findall(r"\w+", content))
    return max(1, round(words / 200))


def generate_slug(title: str) -> str:
    """
    Generate URL-safe slug from title.

    Converts to lowercase, removes special characters,
    and replaces spaces with hyphens.
    """
    slug = title.lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[-\s]+", "-", slug)
    return slug.strip("-")


# ============================================
# Post Endpoints
# ============================================


@router.get(
    "/posts",
    response_model=list[PostPublic],
    summary="List Blog Posts",
    description="""
Retrieve a paginated list of blog posts with optional filtering.

**Features:**
- Filter by category, tag, or search term
- Show drafts (for admin) or published posts only
- Pagination with skip/limit
- Ordered by publication date (newest first)

**Rate Limit:** 60 requests per minute
    """,
    responses={
        200: {
            "description": "List of blog posts",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "550e8400-e29b-41d4-a716-446655440000",
                            "title": "Getting Started with FastAPI",
                            "slug": "getting-started-fastapi",
                            "description": "A beginner's guide to FastAPI",
                            "content": "# Introduction...",
                            "image": "https://example.com/cover.jpg",
                            "category": "tutorial",
                            "tags": ["python", "fastapi"],
                            "draft": False,
                            "lang": "en",
                            "reading_time": 10,
                            "published_at": "2025-11-26T00:00:00Z",
                            "updated_at": "2025-11-26T00:00:00Z",
                            "views": 150,
                        }
                    ]
                }
            },
        }
    },
)
@limiter.limit("60/minute")
async def list_posts(
    request: Request,
    session: AsyncSession = Depends(get_session),
    category: CategoryQuery = None,
    tag: TagQuery = None,
    search: SearchQuery = None,
    draft: bool = Query(
        False,
        description="Include draft posts (admin only)",
    ),
    skip: int = Query(
        0,
        ge=0,
        description="Number of posts to skip for pagination",
        examples=[0, 20, 40],
    ),
    limit: int = Query(
        20,
        ge=1,
        le=100,
        description="Maximum number of posts to return (1-100)",
        examples=[10, 20, 50],
    ),
):
    """List all blog posts with optional filters."""
    query = select(Post).where(Post.draft == draft)

    if category:
        query = query.where(Post.category == category)

    if tag:
        query = query.where(Post.tags.contains([tag]))  # type: ignore[union-attr]

    if search:
        search_filter = f"%{search}%"
        query = query.where(
            (Post.title.ilike(search_filter))  # type: ignore[union-attr]
            | (Post.description.ilike(search_filter))  # type: ignore[union-attr]
        )

    query = query.order_by(Post.published_at.desc()).offset(skip).limit(limit)  # type: ignore[union-attr]

    result = await session.execute(query)
    return result.scalars().all()


@router.get(
    "/posts/{slug}",
    response_model=PostDetail,
    summary="Get Post by Slug",
    description="""
Retrieve a single blog post by its URL slug.

**Features:**
- Full post content with markdown
- Reaction counts by type
- Auto-increments view counter

**Rate Limit:** 60 requests per minute
    """,
    responses={
        200: {
            "description": "Post details with reactions",
            "model": PostDetail,
        },
        404: {
            "description": "Post not found",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "type": "not_found",
                        "message": "Post not found",
                    }
                }
            },
        },
    },
)
@limiter.limit("60/minute")
async def get_post(
    request: Request,
    slug: SlugPath,
    session: AsyncSession = Depends(get_session),
):
    """Get a single post by slug with reaction counts."""
    query = select(Post).where(Post.slug == slug)
    result = await session.execute(query)
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    # Increment view count
    post.views += 1
    session.add(post)
    await session.commit()

    # Get reaction counts
    reactions_query = select(Reaction).where(Reaction.post_id == post.id)
    reactions_result = await session.execute(reactions_query)
    reactions = reactions_result.scalars().all()

    reactions_count = {r.type: r.count for r in reactions}

    return PostDetail(
        **post.model_dump(),
        reactions_count=reactions_count,
    )


@router.post(
    "/posts",
    response_model=PostPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Create New Post",
    description="""
Create a new blog post.

**Features:**
- Auto-generates reading time if not provided
- Validates slug uniqueness
- Validates slug format (lowercase, hyphens only)

**Rate Limit:** 10 requests per minute (write operation)
    """,
    responses={
        201: {
            "description": "Post created successfully",
            "model": PostPublic,
        },
        400: {
            "description": "Invalid request (e.g., duplicate slug)",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "type": "bad_request",
                        "message": "Slug already exists",
                    }
                }
            },
        },
        422: {
            "description": "Validation error",
        },
    },
)
@limiter.limit("10/minute")
async def create_post(
    request: Request,
    post_data: PostCreate,
    session: AsyncSession = Depends(get_session),
):
    """Create a new blog post."""
    # Check if slug already exists
    existing = await session.execute(select(Post).where(Post.slug == post_data.slug))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Slug already exists",
        )

    # Calculate reading time if not provided
    reading_time = post_data.reading_time or calculate_reading_time(post_data.content)

    post = Post(
        **post_data.model_dump(),
        reading_time=reading_time,
    )

    session.add(post)
    await session.commit()
    await session.refresh(post)

    return post


@router.put(
    "/posts/{slug}",
    response_model=PostPublic,
    summary="Update Post",
    description="""
Update an existing blog post.

**Features:**
- Partial updates supported (only provided fields are updated)
- Auto-recalculates reading time if content changes
- Auto-updates the updated_at timestamp

**Rate Limit:** 10 requests per minute (write operation)
    """,
    responses={
        200: {
            "description": "Post updated successfully",
            "model": PostPublic,
        },
        404: {
            "description": "Post not found",
            "model": ErrorResponse,
        },
        422: {
            "description": "Validation error",
        },
    },
)
@limiter.limit("10/minute")
async def update_post(
    request: Request,
    slug: SlugPath,
    post_data: PostUpdate,
    session: AsyncSession = Depends(get_session),
):
    """Update an existing blog post."""
    query = select(Post).where(Post.slug == slug)
    result = await session.execute(query)
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    update_data = post_data.model_dump(exclude_unset=True)

    # Recalculate reading time if content changed
    if "content" in update_data:
        update_data["reading_time"] = calculate_reading_time(update_data["content"])

    update_data["updated_at"] = datetime.now(timezone.utc)

    for key, value in update_data.items():
        setattr(post, key, value)

    session.add(post)
    await session.commit()
    await session.refresh(post)

    return post


@router.delete(
    "/posts/{slug}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Post",
    description="""
Permanently delete a blog post.

**Warning:** This action is irreversible. All associated reactions will also be deleted.

**Rate Limit:** 10 requests per minute (write operation)
    """,
    responses={
        204: {
            "description": "Post deleted successfully",
        },
        404: {
            "description": "Post not found",
            "model": ErrorResponse,
        },
    },
)
@limiter.limit("10/minute")
async def delete_post(
    request: Request,
    slug: SlugPath,
    session: AsyncSession = Depends(get_session),
):
    """Delete a blog post permanently."""
    query = select(Post).where(Post.slug == slug)
    result = await session.execute(query)
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    await session.delete(post)
    await session.commit()


# ============================================
# Reaction Endpoints
# ============================================


@router.post(
    "/posts/{slug}/react",
    response_model=ReactionPublic,
    summary="React to Post",
    description=f"""
Add or increment a reaction to a blog post.

**Available Reaction Types:**
{chr(10).join(f"- `{r.value}`" for r in ReactionTypeEnum)}

**Behavior:**
- If the reaction type already exists, increments the count
- If new, creates the reaction with count of 1

**Rate Limit:** 30 requests per minute
    """,
    responses={
        200: {
            "description": "Reaction added/incremented",
            "model": ReactionPublic,
        },
        404: {
            "description": "Post not found",
            "model": ErrorResponse,
        },
        422: {
            "description": "Invalid reaction type",
        },
    },
)
@limiter.limit("30/minute")
async def react_to_post(
    request: Request,
    slug: SlugPath,
    reaction_data: ReactionCreate,
    session: AsyncSession = Depends(get_session),
):
    """Add a reaction to a post."""
    # Get the post
    post_query = select(Post).where(Post.slug == slug)
    post_result = await session.execute(post_query)
    post = post_result.scalar_one_or_none()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    # Check if reaction type exists for this post
    reaction_query = select(Reaction).where(
        (Reaction.post_id == post.id) & (Reaction.type == reaction_data.type)
    )
    reaction_result = await session.execute(reaction_query)
    reaction = reaction_result.scalar_one_or_none()

    if reaction:
        # Increment existing reaction
        reaction.count += 1
    else:
        # Create new reaction
        reaction = Reaction(
            post_id=post.id,
            type=reaction_data.type,
            count=1,
        )

    session.add(reaction)
    await session.commit()
    await session.refresh(reaction)

    return reaction


@router.get(
    "/posts/{slug}/reactions",
    response_model=list[ReactionPublic],
    summary="Get Post Reactions",
    description="""
Get all reactions for a specific post.

Returns a list of all reaction types with their counts for the specified post.

**Rate Limit:** 60 requests per minute
    """,
    responses={
        200: {
            "description": "List of reactions",
            "content": {
                "application/json": {
                    "example": [
                        {"type": "like", "count": 42},
                        {"type": "love", "count": 15},
                        {"type": "fire", "count": 8},
                    ]
                }
            },
        },
        404: {
            "description": "Post not found",
            "model": ErrorResponse,
        },
    },
)
@limiter.limit("60/minute")
async def get_post_reactions(
    request: Request,
    slug: SlugPath,
    session: AsyncSession = Depends(get_session),
):
    """Get all reactions for a post."""
    # Get the post
    post_query = select(Post).where(Post.slug == slug)
    post_result = await session.execute(post_query)
    post = post_result.scalar_one_or_none()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    # Get reactions
    reactions_query = select(Reaction).where(Reaction.post_id == post.id)
    reactions_result = await session.execute(reactions_query)

    return reactions_result.scalars().all()


# ============================================
# Category and Tag Endpoints
# ============================================


@router.get(
    "/categories",
    response_model=list[CategoryCount],
    summary="List Categories",
    description="""
Get all categories with their post counts.

Returns categories sorted by post count (descending).
Only includes categories from published (non-draft) posts.

**Rate Limit:** 60 requests per minute
    """,
    responses={
        200: {
            "description": "List of categories with counts",
            "content": {
                "application/json": {
                    "example": [
                        {"name": "tutorial", "count": 15},
                        {"name": "tech", "count": 12},
                        {"name": "personal", "count": 5},
                    ]
                }
            },
        },
    },
)
@limiter.limit("60/minute")
async def list_categories(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """List all categories with post counts."""
    query = (
        select(Post.category, func.count(Post.id).label("count"))
        .where(Post.draft == False)  # noqa: E712
        .group_by(Post.category)
        .order_by(func.count(Post.id).desc())
    )

    result = await session.execute(query)
    rows = result.all()

    return [CategoryCount(name=row[0], count=row[1]) for row in rows]


@router.get(
    "/tags",
    response_model=list[TagCount],
    summary="List Tags",
    description="""
Get all tags with their post counts.

Returns tags sorted by usage count (descending).
Only includes tags from published (non-draft) posts.

**Rate Limit:** 60 requests per minute
    """,
    responses={
        200: {
            "description": "List of tags with counts",
            "content": {
                "application/json": {
                    "example": [
                        {"name": "python", "count": 25},
                        {"name": "fastapi", "count": 18},
                        {"name": "react", "count": 12},
                    ]
                }
            },
        },
    },
)
@limiter.limit("60/minute")
async def list_tags(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """List all tags with post counts."""
    # Get all posts and aggregate tags
    query = select(Post.tags).where(Post.draft == False)  # noqa: E712
    result = await session.execute(query)
    all_tags = result.scalars().all()

    # Count occurrences
    tag_counts: dict[str, int] = {}
    for tags in all_tags:
        if tags:  # Check if tags is not None
            for tag in tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

    # Sort by count
    sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)

    return [TagCount(name=name, count=count) for name, count in sorted_tags]


# ============================================
# Statistics Endpoint
# ============================================


@router.get(
    "/stats",
    summary="Get Blog Statistics",
    description="""
Get overall blog statistics.

Returns aggregate statistics including:
- Total posts (published and drafts)
- Total views across all posts
- Total reactions
- Top categories and tags

**Rate Limit:** 30 requests per minute
    """,
    responses={
        200: {
            "description": "Blog statistics",
            "content": {
                "application/json": {
                    "example": {
                        "total_posts": 50,
                        "published_posts": 45,
                        "draft_posts": 5,
                        "total_views": 12500,
                        "total_reactions": 890,
                        "categories_count": 6,
                        "tags_count": 25,
                    }
                }
            },
        },
    },
)
@limiter.limit("30/minute")
async def get_blog_stats(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """Get overall blog statistics."""
    # Total posts
    total_query = select(func.count(Post.id))
    total_result = await session.execute(total_query)
    total_posts = total_result.scalar() or 0

    # Published posts
    published_query = select(func.count(Post.id)).where(Post.draft == False)  # noqa: E712
    published_result = await session.execute(published_query)
    published_posts = published_result.scalar() or 0

    # Total views
    views_query = select(func.sum(Post.views))
    views_result = await session.execute(views_query)
    total_views = views_result.scalar() or 0

    # Total reactions
    reactions_query = select(func.sum(Reaction.count))
    reactions_result = await session.execute(reactions_query)
    total_reactions = reactions_result.scalar() or 0

    # Categories count
    categories_query = select(func.count(func.distinct(Post.category))).where(
        Post.draft == False  # noqa: E712
    )
    categories_result = await session.execute(categories_query)
    categories_count = categories_result.scalar() or 0

    # Tags count (unique)
    tags_query = select(Post.tags).where(Post.draft == False)  # noqa: E712
    tags_result = await session.execute(tags_query)
    all_tags = tags_result.scalars().all()
    unique_tags = set()
    for tags in all_tags:
        if tags:
            unique_tags.update(tags)

    return {
        "total_posts": total_posts,
        "published_posts": published_posts,
        "draft_posts": total_posts - published_posts,
        "total_views": total_views,
        "total_reactions": total_reactions,
        "categories_count": categories_count,
        "tags_count": len(unique_tags),
    }
