"""
Blog service for post and reaction business logic.

Why: Centraliza regras de negócio do blog em um lugar,
     permitindo reutilização entre API e views.

How: Encapsula queries, validações e transformações de dados,
     abstraindo detalhes do ORM dos routers.
"""

import re
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from app.models.blog import (
    Post,
    PostCreate,
    PostUpdate,
    Reaction,
    ReactionTypeEnum,
)


class BlogService:
    """
    Serviço para operações do blog.

    Why: Abstrai a complexidade das queries e regras de negócio,
         mantendo os routers limpos e focados em HTTP.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # ==========================================
    # Post Operations
    # ==========================================

    async def get_posts(
        self,
        *,
        category: str | None = None,
        tag: str | None = None,
        search: str | None = None,
        include_drafts: bool = False,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Post]:
        """
        Busca posts com filtros opcionais.

        Args:
            category: Filtra por categoria
            tag: Filtra por tag
            search: Busca em título e descrição
            include_drafts: Se True, inclui rascunhos
            limit: Máximo de resultados
            offset: Paginação

        Returns:
            Lista de posts ordenados por data de publicação
        """
        query = select(Post)

        if not include_drafts:
            query = query.where(Post.draft == False)  # noqa: E712

        if category:
            query = query.where(Post.category == category)

        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                col(Post.title).ilike(search_pattern)
                | col(Post.description).ilike(search_pattern)
            )

        # Tag filtering - JSON array contains
        # TODO: Implementar filtro por tag quando necessário

        query = (
            query.order_by(col(Post.published_at).desc()).offset(offset).limit(limit)
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_post_by_slug(self, slug: str) -> Post | None:
        """Busca um post pelo slug."""
        query = select(Post).where(Post.slug == slug)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_post_by_id(self, post_id: UUID) -> Post | None:
        """Busca um post pelo ID."""
        return await self.session.get(Post, post_id)

    async def create_post(self, data: PostCreate) -> Post:
        """
        Cria um novo post.

        Why: Centraliza validações e transformações na criação,
             como geração de slug e cálculo de reading time.
        """
        post = Post.model_validate(data)

        # Calcula reading time se não fornecido
        if post.reading_time == 0:
            post.reading_time = self._calculate_reading_time(post.content)

        self.session.add(post)
        await self.session.commit()
        await self.session.refresh(post)
        return post

    async def update_post(self, post: Post, data: PostUpdate) -> Post:
        """Atualiza um post existente."""
        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(post, field, value)

        post.updated_at = datetime.now(timezone.utc)

        # Recalcula reading time se conteúdo mudou
        if "content" in update_data:
            post.reading_time = self._calculate_reading_time(post.content)

        self.session.add(post)
        await self.session.commit()
        await self.session.refresh(post)
        return post

    async def delete_post(self, post: Post) -> None:
        """Remove um post."""
        await self.session.delete(post)
        await self.session.commit()

    async def increment_views(self, post: Post) -> None:
        """Incrementa contador de views de um post."""
        post.views += 1
        self.session.add(post)
        await self.session.commit()

    # ==========================================
    # Category & Tag Aggregation
    # ==========================================

    async def get_categories_with_count(self) -> list[dict[str, Any]]:
        """Retorna categorias com contagem de posts."""
        query = (
            select(Post.category, func.count(Post.id).label("count"))
            .where(Post.draft == False)  # noqa: E712
            .group_by(Post.category)
            .order_by(func.count(Post.id).desc())
        )
        result = await self.session.execute(query)
        return [{"category": row[0], "count": row[1]} for row in result.all()]

    # ==========================================
    # Reaction Operations
    # ==========================================

    async def add_reaction(
        self, post_id: UUID, reaction_type: ReactionTypeEnum
    ) -> Reaction:
        """
        Adiciona uma reação a um post (incrementa contador).

        Why: Modelo simplificado de reações com contador por tipo,
             sem tracking individual de IPs.
        """
        # Verifica se já existe reação deste tipo para o post
        existing = await self.session.execute(
            select(Reaction).where(
                Reaction.post_id == post_id,
                Reaction.type == reaction_type.value,
            )
        )
        reaction = existing.scalar_one_or_none()

        if reaction:
            # Incrementa contador existente
            reaction.count += 1
        else:
            # Cria nova reação com contador = 1
            reaction = Reaction(
                post_id=post_id,
                type=reaction_type.value,
                count=1,
            )
            self.session.add(reaction)

        await self.session.commit()
        await self.session.refresh(reaction)
        return reaction

    async def get_reactions_count(self, post_id: UUID) -> dict[str, int]:
        """Retorna contagem de reações por tipo para um post."""
        query = select(Reaction.type, Reaction.count).where(Reaction.post_id == post_id)
        result = await self.session.execute(query)
        return {row[0]: row[1] for row in result.all()}

    # ==========================================
    # Private Helpers
    # ==========================================

    def _calculate_reading_time(self, content: str) -> int:
        """
        Calcula tempo de leitura em minutos.

        Why: Usa média de 200 palavras por minuto,
             padrão da indústria para tempo de leitura.
        """
        words = len(re.findall(r"\w+", content))
        return max(1, round(words / 200))

    @staticmethod
    def generate_slug(title: str) -> str:
        """
        Gera slug URL-friendly a partir do título.

        Why: Slugs melhoram SEO e legibilidade de URLs,
             convertendo título para formato lowercase-with-hyphens.
        """
        slug = title.lower().strip()
        slug = re.sub(r"[^\w\s-]", "", slug)
        slug = re.sub(r"[\s_]+", "-", slug)
        slug = re.sub(r"-+", "-", slug)
        return slug.strip("-")
