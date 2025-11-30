"""
Admin panel views for managing portfolio content.

Why: Separa as rotas de administração das rotas públicas,
     permitindo controle de acesso e lógica específica do admin.

How: Usa dependency injection para verificar autenticação,
     formulários HTML com parsing seguro via utils.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from app.config import settings
from app.core.deps import get_current_user_optional
from app.core.utils import (
    get_form_bool,
    get_form_int,
    get_form_json,
    get_form_list,
    get_form_str,
)
from app.db import get_session
from app.models.blog import Post
from app.models.profile import Profile
from app.models.project import Project
from app.models.user import User

router = APIRouter(prefix="/admin", include_in_schema=False)
templates = Jinja2Templates(directory="app/templates")
templates.env.globals["settings"] = settings


# ==========================================
# Dependencies
# ==========================================


async def get_admin_user(
    request: Request, user: User | None = Depends(get_current_user_optional)
) -> User:
    """
    Verifica se o usuário está autenticado para acessar o admin.

    Why: Todas as rotas admin precisam de autenticação,
         centraliza a verificação em uma dependency.

    Returns:
        User autenticado

    Raises:
        HTTPException 302: Redireciona para login se não autenticado
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_302_FOUND,
            headers={"Location": "/login"},
        )
    return user


# ==========================================
# Dashboard
# ==========================================


@router.get("/")
async def admin_dashboard(request: Request, user: User = Depends(get_admin_user)):
    """Dashboard principal do admin."""
    return templates.TemplateResponse(
        "admin/dashboard.html",
        {"request": request, "user": user, "title": "Admin Dashboard"},
    )


# ==========================================
# Profile Management
# ==========================================


@router.get("/profile")
async def edit_profile(
    request: Request,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_admin_user),
):
    """Página de edição do perfil."""
    query = select(Profile).where(Profile.user_id == user.id)
    result = await session.execute(query)
    profile = result.scalar_one_or_none()

    if not profile:
        profile = Profile(user_id=user.id)
        session.add(profile)
        await session.commit()
        await session.refresh(profile)

    return templates.TemplateResponse(
        "admin/profile.html",
        {"request": request, "user": user, "profile": profile, "title": "Edit Profile"},
    )


@router.post("/profile")
async def save_profile(
    request: Request,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_admin_user),
) -> RedirectResponse:
    """Salva as alterações do perfil do usuário."""
    form = await request.form()

    query = select(Profile).where(Profile.user_id == user.id)
    result = await session.execute(query)
    profile = result.scalar_one_or_none()

    if not profile:
        profile = Profile(user_id=user.id)

    # Atualiza campos básicos usando helpers type-safe
    profile.name = get_form_str(form, "name")
    profile.location = get_form_str(form, "location")
    profile.short_bio = get_form_str(form, "short_bio")
    profile.email = get_form_str(form, "email")
    profile.phone = get_form_str(form, "phone")
    profile.website = get_form_str(form, "website")
    profile.github = get_form_str(form, "github")
    profile.linkedin = get_form_str(form, "linkedin")
    profile.twitter = get_form_str(form, "twitter")
    profile.about_markdown = get_form_str(form, "about_markdown")

    # Campos JSON estruturados (Work, Education, Skills)
    work_data = get_form_json(form, "work_experience_json")
    if work_data is not None:
        profile.work_experience = work_data

    education_data = get_form_json(form, "education_json")
    if education_data is not None:
        profile.education = education_data

    skills_data = get_form_json(form, "skills_json")
    if skills_data is not None:
        profile.skills = skills_data

    session.add(profile)
    await session.commit()

    return RedirectResponse(url="/admin/profile", status_code=303)


# ==========================================
# Projects Management
# ==========================================


@router.get("/projects")
async def list_projects(
    request: Request,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_admin_user),
):
    """Lista todos os projetos para gerenciamento."""
    projects = (
        (
            await session.execute(
                select(Project).order_by(col(Project.created_at).desc())
            )
        )
        .scalars()
        .all()
    )
    return templates.TemplateResponse(
        "admin/projects_list.html",
        {
            "request": request,
            "user": user,
            "projects": projects,
            "title": "Manage Projects",
        },
    )


@router.get("/projects/new")
async def new_project(request: Request, user: User = Depends(get_admin_user)):
    """Formulário de criação de novo projeto."""
    return templates.TemplateResponse(
        "admin/project_edit.html",
        {"request": request, "user": user, "project": None, "title": "New Project"},
    )


@router.post("/projects/new")
async def create_project(
    request: Request,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_admin_user),
) -> RedirectResponse:
    """Cria um novo projeto."""
    form = await request.form()
    project = Project(
        title=get_form_str(form, "title"),
        slug=get_form_str(form, "slug"),
        description=get_form_str(form, "description"),
        content=get_form_str(form, "content"),
        image=get_form_str(form, "image") or None,
        category=get_form_str(form, "category"),
        github_url=get_form_str(form, "github_url") or None,
        demo_url=get_form_str(form, "demo_url") or None,
        featured=get_form_bool(form, "featured"),
        tech_stack=get_form_list(form, "tech_stack"),
    )

    session.add(project)
    await session.commit()
    return RedirectResponse(url="/admin/projects", status_code=303)


@router.get("/projects/{project_id}")
async def edit_project(
    request: Request,
    project_id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_admin_user),
):
    """Formulário de edição de projeto."""
    project = await session.get(Project, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return templates.TemplateResponse(
        "admin/project_edit.html",
        {"request": request, "user": user, "project": project, "title": "Edit Project"},
    )


@router.post("/projects/{project_id}")
async def update_project(
    request: Request,
    project_id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_admin_user),
) -> RedirectResponse:
    """Atualiza um projeto existente."""
    project = await session.get(Project, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    form = await request.form()
    project.title = get_form_str(form, "title")
    project.slug = get_form_str(form, "slug")
    project.description = get_form_str(form, "description")
    project.content = get_form_str(form, "content")
    project.image = get_form_str(form, "image") or None
    project.category = get_form_str(form, "category")
    project.github_url = get_form_str(form, "github_url") or None
    project.demo_url = get_form_str(form, "demo_url") or None
    project.featured = get_form_bool(form, "featured")
    project.tech_stack = get_form_list(form, "tech_stack")

    session.add(project)
    await session.commit()
    return RedirectResponse(url="/admin/projects", status_code=303)


@router.post("/projects/{project_id}/delete")
async def delete_project(
    request: Request,
    project_id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_admin_user),
):
    """Remove um projeto."""
    project = await session.get(Project, project_id)
    if project:
        await session.delete(project)
        await session.commit()
    return RedirectResponse(url="/admin/projects", status_code=303)


# ==========================================
# Blog Management
# ==========================================


@router.get("/blog")
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
    return templates.TemplateResponse(
        "admin/blog_list.html",
        {"request": request, "user": user, "posts": posts, "title": "Manage Blog"},
    )


@router.get("/blog/new")
async def new_post(request: Request, user: User = Depends(get_admin_user)):
    """Formulário de criação de novo post."""
    return templates.TemplateResponse(
        "admin/blog_edit.html",
        {"request": request, "user": user, "post": None, "title": "New Post"},
    )


@router.post("/blog/new")
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


@router.get("/blog/{post_id}")
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

    return templates.TemplateResponse(
        "admin/blog_edit.html",
        {"request": request, "user": user, "post": post, "title": "Edit Post"},
    )


@router.post("/blog/{post_id}")
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


@router.post("/blog/{post_id}/delete")
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
