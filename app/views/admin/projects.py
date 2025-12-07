"""
Admin projects views.

Why: Gerenciamento de projetos no admin.

How: CRUD de Project usando JinjaX.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from app.catalog import catalog
from app.core.utils import get_form_bool, get_form_list, get_form_str
from app.db import get_session
from app.models.project import Project
from app.models.user import User
from app.views.admin.deps import get_admin_user

router = APIRouter(prefix="/projects")


@router.get("", response_class=HTMLResponse)
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
    return catalog.render(
        "admin/projects-list.jinja",
        request=request,
        user=user,
        projects=list(projects),
    )


@router.get("/new", response_class=HTMLResponse)
async def new_project(request: Request, user: User = Depends(get_admin_user)):
    """Formulário de criação de novo projeto."""
    return catalog.render(
        "admin/project-edit.jinja",
        request=request,
        user=user,
        project=None,
    )


@router.post("/new")
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


@router.get("/{project_id}", response_class=HTMLResponse)
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

    return catalog.render(
        "admin/project-edit.jinja",
        request=request,
        user=user,
        project=project,
    )


@router.post("/{project_id}")
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


@router.post("/{project_id}/delete")
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
