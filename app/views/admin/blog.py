"""
Admin blog views.

Why: Gerenciamento de posts do blog no admin.

How: CRUD de Post usando JinjaX.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from app.catalog import catalog
from app.core.utils import get_form_int, get_form_list, get_form_str
from app.db import get_session
from app.models.blog import Post
from app.models.user import User
from app.views.admin.deps import get_admin_user

router = APIRouter(prefix="/blog")


@router.get("", response_class=HTMLResponse)
async def list_posts(
    request: Request,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_admin_user),
):
    """Lista todos os posts do blog para gerenciamento."""
    posts = (
        (await session.execute(select(Post).order_by(col(Post.published_at).desc())))
        .scalars()
        .all()
    )
    return catalog.render(
        "admin/blog-list.jinja",
        request=request,
        user=user,
        posts=list(posts),
    )


@router.get("/new", response_class=HTMLResponse)
async def new_post(request: Request, user: User = Depends(get_admin_user)):
    """Formulário de criação de novo post."""
    return catalog.render(
        "admin/blog-edit.jinja",
        request=request,
        user=user,
        post=None,
    )


@router.post("/new")
async def create_post(
    request: Request,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_admin_user),
) -> RedirectResponse:
    """Cria um novo post no blog."""
    form = await request.form()
    post = Post(
        title=get_form_str(form, "title"),
        slug=get_form_str(form, "slug"),
        description=get_form_str(form, "description"),
        content=get_form_str(form, "content"),
        image=get_form_str(form, "image") or None,
        category=get_form_str(form, "category"),
        reading_time=get_form_int(form, "reading_time", default=5),
        tags=get_form_list(form, "tags"),
    )

    session.add(post)
    await session.commit()
    return RedirectResponse(url="/admin/blog", status_code=303)


@router.get("/{post_id}", response_class=HTMLResponse)
async def edit_post(
    request: Request,
    post_id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_admin_user),
):
    """Formulário de edição de post."""
    post = await session.get(Post, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    return catalog.render(
        "admin/blog-edit.jinja",
        request=request,
        user=user,
        post=post,
    )


@router.post("/{post_id}")
async def update_post(
    request: Request,
    post_id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_admin_user),
) -> RedirectResponse:
    """Atualiza um post existente."""
    post = await session.get(Post, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    form = await request.form()
    post.title = get_form_str(form, "title")
    post.slug = get_form_str(form, "slug")
    post.description = get_form_str(form, "description")
    post.content = get_form_str(form, "content")
    post.image = get_form_str(form, "image") or None
    post.category = get_form_str(form, "category")
    post.reading_time = get_form_int(form, "reading_time", default=5)
    post.tags = get_form_list(form, "tags")

    session.add(post)
    await session.commit()
    return RedirectResponse(url="/admin/blog", status_code=303)


@router.post("/{post_id}/delete")
async def delete_post(
    request: Request,
    post_id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_admin_user),
):
    """Remove um post do blog."""
    post = await session.get(Post, post_id)
    if post:
        await session.delete(post)
        await session.commit()
    return RedirectResponse(url="/admin/blog", status_code=303)
