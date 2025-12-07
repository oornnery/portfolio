"""
Blog views.

Why: Separa as rotas do blog (listagem, detalhe, comentários) em um módulo próprio,
     mantendo a lógica de blog isolada.

How: Usa JinjaX catalog para renderizar componentes de blog com suporte HTMX.
"""

import markdown
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, or_, select

from app.catalog import catalog
from app.core.deps import get_current_user_optional
from app.db import get_session
from app.models.blog import Post
from app.models.comment import Comment
from app.models.user import User

router = APIRouter()


@router.get("", response_class=HTMLResponse)
async def blog_list(
    request: Request,
    category: str | None = None,
    tag: str | None = None,
    search: str | None = None,
    session: AsyncSession = Depends(get_session),
    user: User | None = Depends(get_current_user_optional),
):
    """Lista de posts do blog com filtros opcionais."""
    query = (
        select(Post).where(Post.draft == False).order_by(col(Post.published_at).desc())  # noqa: E712
    )

    if category:
        query = query.where(Post.category == category)

    if search:
        query = query.where(
            or_(
                col(Post.title).ilike(f"%{search}%"),
                col(Post.description).ilike(f"%{search}%"),
                col(Post.content).ilike(f"%{search}%"),
            )
        )

    result = await session.execute(query)
    posts = list(result.scalars().all())

    # Get unique categories for filter
    categories_query = select(Post.category).where(Post.draft == False).distinct()  # noqa: E712
    categories_result = await session.execute(categories_query)
    categories = [c for c in categories_result.scalars().all() if c]

    # HTMX partial response
    if request.headers.get("HX-Request"):
        return catalog.render(
            "blog/post-list.jinja",
            posts=posts,
            categories=categories,
            current_category=category or "",
        )

    return catalog.render(
        "pages/blog-list.jinja",
        request=request,
        user=user,
        posts=posts,
        categories=categories,
        current_category=category or "",
    )


@router.get("/{slug}", response_class=HTMLResponse)
async def blog_detail(
    slug: str,
    request: Request,
    session: AsyncSession = Depends(get_session),
    user: User | None = Depends(get_current_user_optional),
):
    """Detalhe de um post do blog."""
    query = select(Post).where(Post.slug == slug)
    result = await session.execute(query)
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    # Convert markdown to HTML
    content_html = markdown.markdown(
        post.content, extensions=["fenced_code", "codehilite", "tables"]
    )

    # Get comments
    comments_query = (
        select(Comment, User)
        .join(User)
        .where(Comment.post_id == post.id)
        .order_by(col(Comment.created_at).desc())
    )
    comments_result = await session.execute(comments_query)
    comments = []
    for comment, comment_user in comments_result.all():
        c_dict = comment.model_dump()
        c_dict["author"] = {
            "name": comment_user.name,
            "avatar": comment_user.avatar_url,
        }
        comments.append(c_dict)

    return catalog.render(
        "pages/blog-detail.jinja",
        request=request,
        user=user,
        post=post,
        content=content_html,
        comments=comments,
    )


@router.get("/{slug}/comments", response_class=HTMLResponse)
async def get_comments(
    slug: str,
    request: Request,
    session: AsyncSession = Depends(get_session),
    user: User | None = Depends(get_current_user_optional),
):
    """Retorna os comentários de um post (partial HTMX)."""
    post_query = select(Post).where(Post.slug == slug)
    post_result = await session.execute(post_query)
    post = post_result.scalar_one_or_none()

    if not post:
        return HTMLResponse("Post not found", status_code=404)

    query = (
        select(Comment, User)
        .join(User)
        .where(Comment.post_id == post.id)
        .order_by(col(Comment.created_at).desc())
    )
    result = await session.execute(query)
    comments = []
    for comment, comment_user in result.all():
        c_dict = comment.model_dump()
        c_dict["author"] = {
            "name": comment_user.name,
            "avatar": comment_user.avatar_url,
        }
        comments.append(c_dict)

    return catalog.render(
        "blog/comments.jinja",
        comments=comments,
        post_slug=slug,
        user=user,
    )


@router.post("/{slug}/comments", response_class=HTMLResponse)
async def post_comment(
    slug: str,
    request: Request,
    session: AsyncSession = Depends(get_session),
    user: User | None = Depends(get_current_user_optional),
):
    """Adiciona um comentário a um post."""
    if not user:
        return HTMLResponse("Please login to comment", status_code=401)

    form = await request.form()
    content = form.get("content")

    if not content:
        return HTMLResponse("Content required", status_code=400)

    post_query = select(Post).where(Post.slug == slug)
    post_result = await session.execute(post_query)
    post = post_result.scalar_one_or_none()

    if not post:
        return HTMLResponse("Post not found", status_code=404)

    comment = Comment(content=str(content), post_id=post.id, user_id=user.id)

    session.add(comment)
    await session.commit()

    # Return updated comments list
    return await get_comments(slug, request, session, user)
