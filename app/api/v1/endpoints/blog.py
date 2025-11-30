"""
Blog API endpoints v1.

Why: API REST para operações do blog com versionamento,
     rate limiting e documentação OpenAPI completa.

How: Usa BlogService para lógica de negócio,
     expõe endpoints RESTful com paginação e filtros.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models.blog import (
    PostCreate,
    PostPublic,
    PostUpdate,
    ReactionCreate,
    ReactionPublic,
)
from app.services.blog import BlogService

router = APIRouter()

# Rate limiter para proteção contra abuso
limiter = Limiter(key_func=get_remote_address)


# ==========================================
# Type Aliases for Documentation
# ==========================================

SlugPath = Annotated[
    str,
    Path(
        description="URL-friendly post identifier",
        min_length=1,
        max_length=200,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
        examples=["getting-started-fastapi"],
    ),
]


# ==========================================
# Dependencies
# ==========================================


def get_blog_service(
    session: AsyncSession = Depends(get_session),
) -> BlogService:
    """Dependency que injeta BlogService."""
    return BlogService(session)


# ==========================================
# Post Endpoints
# ==========================================


@router.get("", response_model=list[PostPublic])
async def list_posts(
    request: Request,
    category: str | None = Query(None, description="Filter by category"),
    tag: str | None = Query(None, description="Filter by tag"),
    search: str | None = Query(
        None, min_length=2, description="Search in title/description"
    ),
    limit: int = Query(20, ge=1, le=100, description="Results per page"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    service: BlogService = Depends(get_blog_service),
):
    """
    Lista posts do blog com filtros opcionais.

    Suporta filtros por categoria, tag e busca textual.
    Resultados ordenados por data de publicação (mais recente primeiro).
    """
    posts = await service.get_posts(
        category=category,
        tag=tag,
        search=search,
        limit=limit,
        offset=offset,
    )
    return posts


@router.get("/categories")
async def list_categories(
    service: BlogService = Depends(get_blog_service),
):
    """
    Lista categorias com contagem de posts.

    Útil para sidebar/filtros de navegação.
    """
    return await service.get_categories_with_count()


@router.get("/{slug}", response_model=PostPublic)
async def get_post(
    slug: SlugPath,
    service: BlogService = Depends(get_blog_service),
):
    """
    Busca um post pelo slug.

    Incrementa contador de views automaticamente.
    """
    post = await service.get_post_by_slug(slug)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with slug '{slug}' not found",
        )

    # Incrementa views
    await service.increment_views(post)

    return post


@router.post("", response_model=PostPublic, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: PostCreate,
    service: BlogService = Depends(get_blog_service),
):
    """
    Cria um novo post.

    Requer autenticação de admin (TODO: adicionar dependency).
    """
    # TODO: Adicionar verificação de admin
    return await service.create_post(post_data)


@router.patch("/{slug}", response_model=PostPublic)
async def update_post(
    slug: SlugPath,
    post_data: PostUpdate,
    service: BlogService = Depends(get_blog_service),
):
    """
    Atualiza um post existente.

    Apenas campos fornecidos são atualizados.
    """
    post = await service.get_post_by_slug(slug)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with slug '{slug}' not found",
        )

    return await service.update_post(post, post_data)


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    slug: SlugPath,
    service: BlogService = Depends(get_blog_service),
):
    """
    Remove um post.

    Requer autenticação de admin (TODO: adicionar dependency).
    """
    post = await service.get_post_by_slug(slug)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with slug '{slug}' not found",
        )

    await service.delete_post(post)


# ==========================================
# Reaction Endpoints
# ==========================================


@router.post("/{slug}/reactions", response_model=ReactionPublic)
async def add_reaction(
    slug: SlugPath,
    reaction_data: ReactionCreate,
    service: BlogService = Depends(get_blog_service),
):
    """
    Adiciona uma reação a um post.

    Incrementa o contador do tipo de reação especificado.
    """
    post = await service.get_post_by_slug(slug)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with slug '{slug}' not found",
        )

    # Converte string para enum
    from app.models.blog import ReactionTypeEnum

    try:
        reaction_type = ReactionTypeEnum(reaction_data.type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid reaction type: {reaction_data.type}",
        )

    reaction = await service.add_reaction(
        post_id=post.id,
        reaction_type=reaction_type,
    )
    return reaction


@router.get("/{slug}/reactions")
async def get_reactions(
    slug: SlugPath,
    service: BlogService = Depends(get_blog_service),
):
    """
    Retorna contagem de reações por tipo para um post.
    """
    post = await service.get_post_by_slug(slug)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with slug '{slug}' not found",
        )

    return await service.get_reactions_count(post.id)
