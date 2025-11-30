"""
Projects API endpoints v1.

Why: API REST para projetos do portfolio com versionamento,
     permitindo listagem, filtros e CRUD completo.

How: Usa ProjectService para lógica de negócio,
     expõe endpoints RESTful com paginação.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models.project import ProjectCreate, ProjectPublic, ProjectUpdate
from app.services.project import ProjectService

router = APIRouter()


# ==========================================
# Type Aliases
# ==========================================

SlugPath = Annotated[
    str,
    Path(
        description="URL-friendly project identifier",
        min_length=1,
        max_length=200,
        examples=["portfolio-website"],
    ),
]


# ==========================================
# Dependencies
# ==========================================


def get_project_service(
    session: AsyncSession = Depends(get_session),
) -> ProjectService:
    """Dependency que injeta ProjectService."""
    return ProjectService(session)


# ==========================================
# Endpoints
# ==========================================


@router.get("", response_model=list[ProjectPublic])
async def list_projects(
    category: str | None = Query(None, description="Filter by category"),
    featured: bool | None = Query(None, description="Filter featured projects"),
    limit: int = Query(20, ge=1, le=100, description="Results per page"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    service: ProjectService = Depends(get_project_service),
):
    """
    Lista projetos do portfolio com filtros opcionais.

    Resultados ordenados por data de criação (mais recente primeiro).
    """
    projects = await service.get_projects(
        category=category,
        featured=featured,
        limit=limit,
        offset=offset,
    )
    return projects


@router.get("/categories")
async def list_categories(
    service: ProjectService = Depends(get_project_service),
):
    """
    Lista categorias únicas de projetos.

    Útil para filtros de navegação.
    """
    return await service.get_categories()


@router.get("/featured", response_model=list[ProjectPublic])
async def list_featured_projects(
    limit: int = Query(3, ge=1, le=10),
    service: ProjectService = Depends(get_project_service),
):
    """
    Lista projetos em destaque para a home page.
    """
    return await service.get_featured_projects(limit=limit)


@router.get("/{slug}", response_model=ProjectPublic)
async def get_project(
    slug: SlugPath,
    service: ProjectService = Depends(get_project_service),
):
    """
    Busca um projeto pelo slug.
    """
    project = await service.get_project_by_slug(slug)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with slug '{slug}' not found",
        )
    return project


@router.post("", response_model=ProjectPublic, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    service: ProjectService = Depends(get_project_service),
):
    """
    Cria um novo projeto.

    Requer autenticação de admin (TODO: adicionar dependency).
    """
    return await service.create_project(project_data)


@router.patch("/{slug}", response_model=ProjectPublic)
async def update_project(
    slug: SlugPath,
    project_data: ProjectUpdate,
    service: ProjectService = Depends(get_project_service),
):
    """
    Atualiza um projeto existente.

    Apenas campos fornecidos são atualizados.
    """
    project = await service.get_project_by_slug(slug)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with slug '{slug}' not found",
        )
    return await service.update_project(project, project_data)


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    slug: SlugPath,
    service: ProjectService = Depends(get_project_service),
):
    """
    Remove um projeto.

    Requer autenticação de admin (TODO: adicionar dependency).
    """
    project = await service.get_project_by_slug(slug)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with slug '{slug}' not found",
        )
    await service.delete_project(project)
