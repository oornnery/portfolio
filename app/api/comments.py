from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.db import get_session
from app.models.comment import Comment, CommentCreate, CommentPublic
from app.models.user import User
from app.models.blog import Post
from app.core.security import decode_access_token
from typing import Optional
import uuid

router = APIRouter(prefix="/comments", tags=["Comments"])

async def get_current_user(request: Request, session: AsyncSession = Depends(get_session)) -> Optional[User]:
    token = request.cookies.get("access_token")
    if not token:
        return None
    
    try:
        scheme, _, param = token.partition(" ")
        payload = decode_access_token(param)
        if not payload:
            return None
        user_id = payload.get("sub")
        if not user_id:
            return None
            
        user = await session.get(User, uuid.UUID(user_id))
        return user
    except Exception:
        return None

@router.get("/{post_slug}", response_model=list[CommentPublic])
async def list_comments(post_slug: str, session: AsyncSession = Depends(get_session)):
    # Get post first
    post_query = select(Post).where(Post.slug == post_slug)
    post_result = await session.execute(post_query)
    post = post_result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    # Get comments
    query = select(Comment, User).join(User).where(Comment.post_id == post.id).order_by(Comment.created_at.desc())
    result = await session.execute(query)
    comments = []
    for comment, user in result.all():
        c_dict = comment.model_dump()
        c_dict["user_name"] = user.name
        c_dict["user_avatar"] = user.avatar_url
        comments.append(CommentPublic(**c_dict))
        
    return comments

@router.post("/{post_slug}", response_model=CommentPublic)
async def create_comment(
    post_slug: str, 
    comment_data: CommentCreate,
    request: Request,
    session: AsyncSession = Depends(get_session)
):
    user = await get_current_user(request, session)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
        
    post_query = select(Post).where(Post.slug == post_slug)
    post_result = await session.execute(post_query)
    post = post_result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    comment = Comment(
        content=comment_data.content,
        post_id=post.id,
        user_id=user.id,
        parent_id=comment_data.parent_id
    )
    
    session.add(comment)
    await session.commit()
    await session.refresh(comment)
    
    return CommentPublic(
        **comment.model_dump(),
        user_name=user.name,
        user_avatar=user.avatar_url
    )
