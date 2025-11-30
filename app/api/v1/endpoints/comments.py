"""
Comments API endpoints v1.

Why: API para gerenciamento de comentários em posts,
     com autenticação obrigatória para criar.

How: Usa JWT em cookies para autenticação,
     comentários vinculados a posts e usuários.
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from app.core.deps import get_current_user_optional
from app.db import get_session
from app.models.blog import Post
from app.models.comment import Comment, CommentCreate, CommentPublic
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

    # Busca comentários com dados do usuário
    query = (
        select(Comment, User)
        .join(User)
        .where(Comment.post_id == post.id)
        .where(Comment.is_deleted == False)  # noqa: E712
        .order_by(col(Comment.created_at).desc())
    )
    result = await session.execute(query)

    comments = []
    for comment, user in result.all():
        comment_dict = comment.model_dump()
        comment_dict["user_name"] = user.name
        comment_dict["user_avatar"] = user.avatar_url
        comments.append(CommentPublic(**comment_dict))

    return comments


@router.post(
    "/{post_slug}", response_model=CommentPublic, status_code=status.HTTP_201_CREATED
)
async def create_comment(
    post_slug: PostSlugPath,
    comment_data: CommentCreate,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """
    Cria um comentário em um post.

    Requer autenticação via cookie JWT.
    """
    # Verifica autenticação
    user = await get_current_user_optional(request, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to comment",
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

    # Cria comentário
    comment = Comment(
        content=comment_data.content,
        post_id=post.id,
        user_id=user.id,
        parent_id=comment_data.parent_id,
    )

    session.add(comment)
    await session.commit()
    await session.refresh(comment)

    # Retorna com dados do usuário
    return CommentPublic(
        id=comment.id,
        content=comment.content,
        user_id=comment.user_id,
        parent_id=comment.parent_id,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
        user_name=user.name,
        user_avatar=user.avatar_url,
    )


@router.delete("/{post_slug}/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    post_slug: PostSlugPath,
    comment_id: uuid.UUID,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """
    Remove um comentário (soft delete).

    Apenas o autor ou admin pode remover.
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

    # Verifica permissão (autor ou admin)
    if comment.user_id != user.id and not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this comment",
        )

    # Soft delete
    comment.is_deleted = True
    session.add(comment)
    await session.commit()
