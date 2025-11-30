"""
Project service for portfolio projects business logic.

Why: Centraliza operações de projetos, permitindo
     reutilização entre API e admin views.

How: Encapsula queries e validações, abstraindo
     detalhes do ORM dos routers.
"""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from app.models.project import Project, ProjectCreate, ProjectUpdate


class ProjectService:
    """
    Serviço para operações de projetos do portfolio.

    Why: Mantém lógica de negócio separada dos handlers HTTP,
         facilitando testes e manutenção.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_projects(
        self,
        *,
        category: str | None = None,
        featured: bool | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Project]:
        """
        Busca projetos com filtros opcionais.

        Args:
            category: Filtra por categoria
            featured: Filtra por destaque
            limit: Máximo de resultados
            offset: Paginação

        Returns:
            Lista de projetos ordenados por data de criação
        """
        query = select(Project)

        if category:
            query = query.where(Project.category == category)

        if featured is not None:
            query = query.where(Project.featured == featured)

        query = (
            query.order_by(col(Project.created_at).desc()).offset(offset).limit(limit)
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_featured_projects(self, limit: int = 3) -> list[Project]:
        """Busca projetos em destaque para a home."""
        return await self.get_projects(featured=True, limit=limit)

    async def get_project_by_slug(self, slug: str) -> Project | None:
        """Busca um projeto pelo slug."""
        query = select(Project).where(Project.slug == slug)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_project_by_id(self, project_id: UUID) -> Project | None:
        """Busca um projeto pelo ID."""
        return await self.session.get(Project, project_id)

    async def create_project(self, data: ProjectCreate) -> Project:
        """Cria um novo projeto."""
        project = Project.model_validate(data)
        self.session.add(project)
        await self.session.commit()
        await self.session.refresh(project)
        return project

    async def update_project(self, project: Project, data: ProjectUpdate) -> Project:
        """Atualiza um projeto existente."""
        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(project, field, value)

        self.session.add(project)
        await self.session.commit()
        await self.session.refresh(project)
        return project

    async def delete_project(self, project: Project) -> None:
        """Remove um projeto."""
        await self.session.delete(project)
        await self.session.commit()

    async def get_categories(self) -> list[str]:
        """Retorna lista de categorias únicas."""
        query = select(Project.category).distinct()
        result = await self.session.execute(query)
        return [row[0] for row in result.all() if row[0]]
