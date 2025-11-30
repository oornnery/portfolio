"""
Public views for the portfolio frontend.

Why: Separa as rotas públicas do site das rotas de API e admin,
     mantendo a lógica de renderização de templates isolada.

How: Usa Jinja2 templates com HTMX para interações dinâmicas,
     SQLModel para queries async e dependency injection para auth.
"""

import markdown
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, or_, select

from app.config import settings
from app.core.deps import get_current_user_optional
from app.db import get_session
from app.models.blog import Post
from app.models.comment import Comment
from app.models.profile import Profile
from app.models.project import Project
from app.models.user import User

router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory="app/templates")
templates.env.globals["settings"] = settings


@router.get("/")
async def home(
    request: Request,
    session: AsyncSession = Depends(get_session),
    user: User | None = Depends(get_current_user_optional),
):
    """Página inicial com projetos e posts em destaque."""
    # Busca os 3 projetos mais recentes
    projects_query = select(Project).order_by(col(Project.created_at).desc()).limit(3)
    projects_result = await session.execute(projects_query)
    projects_list = projects_result.scalars().all()

    # Busca os 3 posts publicados mais recentes
    posts_query = (
        select(Post)
        .where(Post.draft == False)  # noqa: E712
        .order_by(col(Post.published_at).desc())
        .limit(3)
    )
    posts_result = await session.execute(posts_query)
    posts_list = posts_result.scalars().all()

    return templates.TemplateResponse(
        "pages/home.html",
        {
            "request": request,
            "title": "Home",
            "user": user,
            "projects": projects_list,
            "posts": posts_list,
        },
    )


@router.get("/login")
async def login_page(
    request: Request, user: User | None = Depends(get_current_user_optional)
):
    """Página de login - redireciona se já autenticado."""
    if user:
        return RedirectResponse(url="/")
    return templates.TemplateResponse(
        "pages/login.html", {"request": request, "title": "Login", "user": user}
    )


@router.get("/contact")
async def contact(
    request: Request, user: User | None = Depends(get_current_user_optional)
):
    """Página de contato."""
    return templates.TemplateResponse(
        "pages/contact.html", {"request": request, "title": "Contact", "user": user}
    )


@router.get("/about")
async def about(
    request: Request,
    session: AsyncSession = Depends(get_session),
    user: User | None = Depends(get_current_user_optional),
):
    """Página sobre com perfil do usuário."""
    query = select(Profile).limit(1)
    result = await session.execute(query)
    profile = result.scalar_one_or_none()

    return templates.TemplateResponse(
        "pages/about.html",
        {"request": request, "title": "About", "user": user, "profile": profile},
    )


@router.get("/projects")
async def projects(
    request: Request,
    category: str | None = None,
    tech: str | None = None,
    session: AsyncSession = Depends(get_session),
    user: User | None = Depends(get_current_user_optional),
):
    """Lista de projetos com filtro opcional por categoria."""
    query = select(Project)
    if category:
        query = query.where(Project.category == category)

    result = await session.execute(query)
    projects_list = result.scalars().all()

    # HTMX partial response
    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(
            "partials/project_list.html",
            {"request": request, "projects": projects_list, "user": user},
        )

    return templates.TemplateResponse(
        "pages/projects.html",
        {
            "request": request,
            "title": "Projects",
            "projects": projects_list,
            "category": category,
            "user": user,
        },
    )


@router.get("/projects/{slug}")
async def project_detail(
    slug: str,
    request: Request,
    session: AsyncSession = Depends(get_session),
    user: User | None = Depends(get_current_user_optional),
):
    """Detalhe de um projeto específico."""
    query = select(Project).where(Project.slug == slug)
    result = await session.execute(query)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    html_content = markdown.markdown(
        project.content, extensions=["fenced_code", "codehilite", "tables"]
    )

    return templates.TemplateResponse(
        "pages/project_detail.html",
        {
            "request": request,
            "title": project.title,
            "project": project,
            "content": html_content,
            "user": user,
        },
    )


@router.get("/blog")
async def blog(
    request: Request,
    category: str | None = None,
    tag: str | None = None,
    search: str | None = None,
    session: AsyncSession = Depends(get_session),
    user: User | None = Depends(get_current_user_optional),
):
    """Lista de posts do blog com filtros opcionais."""
    query = select(Post).where(not Post.draft).order_by(col(Post.published_at).desc())  # noqa: E712

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
    posts = result.scalars().all()

    # HTMX partial response
    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(
            "partials/post_list.html",
            {"request": request, "posts": posts, "user": user},
        )

    return templates.TemplateResponse(
        "blog/list.html",
        {"request": request, "title": "Blog", "posts": posts, "user": user},
    )


@router.get("/blog/{slug}")
async def blog_post(
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

    html_content = markdown.markdown(
        post.content, extensions=["fenced_code", "codehilite", "tables"]
    )

    return templates.TemplateResponse(
        "blog/detail.html",
        {
            "request": request,
            "title": post.title,
            "post": post,
            "content": html_content,
            "user": user,
        },
    )


@router.get("/comments/post/{slug}")
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
        return "Post not found"

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
        c_dict["user_name"] = comment_user.name
        c_dict["user_avatar"] = comment_user.avatar_url
        comments.append(c_dict)

    return templates.TemplateResponse(
        "partials/comments.html",
        {"request": request, "comments": comments, "post": post, "user": user},
    )


@router.post("/comments/post/{slug}")
async def post_comment(
    slug: str,
    request: Request,
    session: AsyncSession = Depends(get_session),
    user: User | None = Depends(get_current_user_optional),
):
    """Adiciona um comentário a um post."""
    if not user:
        return "Please login to comment"

    form = await request.form()
    content = form.get("content")

    if not content:
        return "Content required"

    post_query = select(Post).where(Post.slug == slug)
    post_result = await session.execute(post_query)
    post = post_result.scalar_one_or_none()

    if not post:
        return "Post not found"

    comment = Comment(content=str(content), post_id=post.id, user_id=user.id)

    session.add(comment)
    await session.commit()

    # Return updated comments list
    return await get_comments(slug, request, session, user)
