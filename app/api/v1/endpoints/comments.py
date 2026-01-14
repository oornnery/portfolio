"""
Comments API endpoints v1.

Why: API para gerenciamento de comentários em posts,
     permitindo comentários de usuários autenticados E guests.

How: Usa JWT em cookies para autenticação opcional,
     guests podem comentar informando nome e opcionalmente email.
     Fingerprinting via visitor_id para tracking.
"""

import hashlib
import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Path, Request, status
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from app.catalog import catalog
from app.core.deps import get_current_user_optional
from app.db import get_session
from app.models.blog import Post
from app.models.comment import Comment, CommentPublic
from app.models.user import User

router = APIRouter()


# ==========================================
# Type Aliases
# ==========================================

PostSlugPath = Annotated[
    str,
    Path(
        description="Slug do post",
        min_length=1,
        max_length=200,
    ),
]


def get_client_ip(request: Request) -> str:
    """Extrai IP real do cliente considerando proxies."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    if request.client:
        return request.client.host

    return "unknown"


# ==========================================
# Endpoints
# ==========================================


@router.get("/{post_slug}", response_model=list[CommentPublic])
async def list_comments(
    post_slug: PostSlugPath,
    session: AsyncSession = Depends(get_session),
):
    """
    Lista comentários de um post.

    Ordenados por data (mais recentes primeiro).
    Inclui dados públicos do autor (nome, avatar).
    Suporta comentários de usuários logados e guests.
    """
    # Busca o post
    post_query = select(Post).where(Post.slug == post_slug)
    post_result = await session.execute(post_query)
    post = post_result.scalar_one_or_none()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    # Busca comentários (com ou sem user)
    query = (
        select(Comment, User)
        .outerjoin(User, Comment.user_id == User.id)  # LEFT JOIN para incluir guests
        .where(Comment.post_id == post.id)
        .where(Comment.is_deleted == False)  # noqa: E712
        .where(Comment.parent_id == None)  # noqa: E711 - Apenas top-level
        .order_by(col(Comment.created_at).desc())
    )
    result = await session.execute(query)

    comments = []
    for comment, user in result.all():
        # Determina display name e se é guest
        is_guest = comment.user_id is None

        if user:
            display_name = user.name or user.email.split("@")[0]
            user_avatar = user.avatar_url
        else:
            display_name = comment.guest_name or "Anonymous"
            # Gravatar para email de guest
            if comment.guest_email:
                email_hash = hashlib.md5(
                    comment.guest_email.lower().strip().encode()
                ).hexdigest()
                user_avatar = (
                    f"https://www.gravatar.com/avatar/{email_hash}?d=identicon&s=80"
                )
            else:
                user_avatar = None

        comment_public = CommentPublic(
            id=comment.id,
            content=comment.content,
            user_id=comment.user_id,
            visitor_id=comment.visitor_id,
            guest_name=comment.guest_name,
            parent_id=comment.parent_id,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
            user_name=user.name if user else None,
            user_avatar=user_avatar,
            display_name=display_name,
            is_guest=is_guest,
            replies=[],  # TODO: Buscar replies
        )
        comments.append(comment_public)

    return comments


@router.post(
    "/{post_slug}", response_model=CommentPublic, status_code=status.HTTP_201_CREATED
)
async def create_comment(
    post_slug: PostSlugPath,
    request: Request,
    content: str = Form(..., min_length=1, max_length=2000),
    guest_name: Optional[str] = Form(default=None, max_length=50),
    guest_email: Optional[str] = Form(default=None, max_length=254),
    parent_id: Optional[uuid.UUID] = Form(default=None),
    session: AsyncSession = Depends(get_session),
):
    """
    Cria um comentário em um post.

    Suporta:
    - Usuários autenticados via cookie JWT
    - Guests com nome obrigatório e email opcional

    Captura IP e user agent para segurança e moderação.
    """
    # Verifica autenticação (opcional)
    user = await get_current_user_optional(request, session)

    # Se não está logado, precisa de guest_name
    if not user and not guest_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Guest name is required for anonymous comments",
        )

    # Busca o post
    post_query = select(Post).where(Post.slug == post_slug)
    post_result = await session.execute(post_query)
    post = post_result.scalar_one_or_none()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    # Captura info do request
    client_ip = get_client_ip(request)
    user_agent = request.headers.get("User-Agent", "")[:500]

    # Tenta pegar visitor_id do cookie (analytics)
    visitor_id_str = request.cookies.get("_visitor_id")
    visitor_id = uuid.UUID(visitor_id_str) if visitor_id_str else None

    # Cria comentário
    comment = Comment(
        content=content,
        post_id=post.id,
        user_id=user.id if user else None,
        visitor_id=visitor_id,
        guest_name=guest_name if not user else None,
        guest_email=guest_email if not user else None,
        parent_id=parent_id,
        ip_address=client_ip,
        user_agent=user_agent,
    )

    session.add(comment)
    await session.commit()
    await session.refresh(comment)

    # Prepara resposta
    is_guest = user is None

    if user:
        display_name = user.name or user.email.split("@")[0]
        user_avatar = user.avatar_url
    else:
        display_name = guest_name or "Anonymous"
        if guest_email:
            email_hash = hashlib.md5(guest_email.lower().strip().encode()).hexdigest()
            user_avatar = (
                f"https://www.gravatar.com/avatar/{email_hash}?d=identicon&s=80"
            )
        else:
            user_avatar = None

    comment_public = CommentPublic(
        id=comment.id,
        content=comment.content,
        user_id=comment.user_id,
        visitor_id=comment.visitor_id,
        guest_name=comment.guest_name,
        parent_id=comment.parent_id,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
        user_name=user.name if user else None,
        user_avatar=user_avatar,
        display_name=display_name,
        is_guest=is_guest,
        replies=[],
    )

    # If HTMX request, return rendered HTML component
    if request.headers.get("HX-Request"):
        # Fetch all comments to re-render the section
        all_comments = await _get_comments_for_post(post, session)
        html = catalog.render(
            "blog/Comments.jinja",
            comments=all_comments,
            post_slug=post_slug,
            user=user,
        )
        return HTMLResponse(content=html, status_code=201)

    return comment_public


async def _get_comments_for_post(
    post: Post, session: AsyncSession
) -> list[CommentPublic]:
    """Helper to fetch and format comments for a post."""
    query = (
        select(Comment, User)
        .outerjoin(User, Comment.user_id == User.id)
        .where(Comment.post_id == post.id)
        .where(Comment.is_deleted == False)  # noqa: E712
        .where(Comment.parent_id == None)  # noqa: E711
        .order_by(col(Comment.created_at).desc())
    )
    result = await session.execute(query)

    comments = []
    for comment, user in result.all():
        is_guest = comment.user_id is None

        if user:
            display_name = user.name or user.email.split("@")[0]
            user_avatar = user.avatar_url
        else:
            display_name = comment.guest_name or "Anonymous"
            if comment.guest_email:
                email_hash = hashlib.md5(
                    comment.guest_email.lower().strip().encode()
                ).hexdigest()
                user_avatar = (
                    f"https://www.gravatar.com/avatar/{email_hash}?d=identicon&s=80"
                )
            else:
                user_avatar = None

        comments.append(
            CommentPublic(
                id=comment.id,
                content=comment.content,
                user_id=comment.user_id,
                visitor_id=comment.visitor_id,
                guest_name=comment.guest_name,
                parent_id=comment.parent_id,
                created_at=comment.created_at,
                updated_at=comment.updated_at,
                user_name=user.name if user else None,
                user_avatar=user_avatar,
                display_name=display_name,
                is_guest=is_guest,
                replies=[],
            )
        )
    return comments


@router.delete("/{post_slug}/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    post_slug: PostSlugPath,
    comment_id: uuid.UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """
    Remove um comentário (soft delete).

    Apenas o autor (logado) ou admin pode remover.
    Guests não podem deletar seus comentários.
    """
    user = await get_current_user_optional(request, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    comment = await session.get(Comment, comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    # Verifica permissão (autor logado ou admin)
    if comment.user_id != user.id and not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this comment",
        )

    # Soft delete
    comment.is_deleted = True
    session.add(comment)
    await session.commit()
