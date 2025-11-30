"""
Blog service for post and reaction business logic.

Why: Centraliza regras de negócio do blog em um lugar,
     permitindo reutilização entre API e views.

How: Encapsula queries, validações e transformações de dados,
     abstraindo detalhes do ORM dos routers.
     Inclui integração com GitHub para buscar posts de repositórios.
"""

import re
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

import httpx
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


# ==========================================
# GitHub Blog Service
# ==========================================


class GitHubBlogService:
    """
    Serviço para buscar posts de um repositório GitHub.

    Why: Permite usar um repositório GitHub como CMS para posts do blog,
         facilitando versionamento e colaboração via Git.

    How: Usa a GitHub API para buscar arquivos markdown do repositório,
         parseando frontmatter YAML para metadados dos posts.
    """

    def __init__(
        self,
        repo_owner: str,
        repo_name: str,
        posts_path: str = "posts",
        token: str | None = None,
    ) -> None:
        """
        Inicializa o serviço com as credenciais do repositório.

        Args:
            repo_owner: Dono do repositório (username ou org)
            repo_name: Nome do repositório
            posts_path: Caminho da pasta de posts no repo (default: "posts")
            token: Token de acesso GitHub (opcional, aumenta rate limit)
        """
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.posts_path = posts_path
        self.base_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
        self.headers: dict[str, str] = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Portfolio-Blog-Service",
        }
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    async def get_all_posts(self) -> list[dict[str, Any]]:
        """
        Busca todos os posts do repositório GitHub.

        Returns:
            Lista de posts com metadados e conteúdo

        Raises:
            httpx.HTTPStatusError: Se a API retornar erro
        """
        async with httpx.AsyncClient() as client:
            # Lista arquivos na pasta de posts
            response = await client.get(
                f"{self.base_url}/contents/{self.posts_path}",
                headers=self.headers,
            )
            response.raise_for_status()
            files = response.json()

            posts = []
            for file in files:
                if file.get("name", "").endswith(".md"):
                    post = await self._fetch_post_content(client, file)
                    if post:
                        posts.append(post)

            # Ordena por data (mais recente primeiro)
            posts.sort(key=lambda p: p.get("date", ""), reverse=True)
            return posts

    async def get_post(self, slug: str) -> dict[str, Any] | None:
        """
        Busca um post específico pelo slug.

        Args:
            slug: Identificador URL-friendly do post

        Returns:
            Dados do post ou None se não encontrado
        """
        async with httpx.AsyncClient() as client:
            # Tenta buscar arquivo com nome do slug
            filename = f"{slug}.md"
            try:
                response = await client.get(
                    f"{self.base_url}/contents/{self.posts_path}/{filename}",
                    headers=self.headers,
                )
                response.raise_for_status()
                file = response.json()
                return await self._fetch_post_content(client, file)
            except httpx.HTTPStatusError:
                return None

    async def _fetch_post_content(
        self, client: httpx.AsyncClient, file: dict[str, Any]
    ) -> dict[str, Any] | None:
        """
        Busca e parseia conteúdo de um arquivo markdown.

        Args:
            client: Cliente HTTP ativo
            file: Metadados do arquivo da API GitHub

        Returns:
            Post parseado com metadados e conteúdo
        """
        try:
            # Busca conteúdo raw do arquivo
            download_url = file.get("download_url")
            if not download_url:
                return None

            response = await client.get(download_url)
            response.raise_for_status()
            content = response.text

            # Parseia frontmatter e conteúdo
            metadata, body = self._parse_frontmatter(content)

            # Extrai slug do nome do arquivo
            filename = file.get("name", "")
            slug = filename.replace(".md", "")

            return {
                "slug": slug,
                "title": metadata.get("title", slug.replace("-", " ").title()),
                "description": metadata.get("description", ""),
                "content": body,
                "date": metadata.get("date", ""),
                "category": metadata.get("category", "Uncategorized"),
                "tags": metadata.get("tags", []),
                "image": metadata.get("image"),
                "author": metadata.get("author", self.repo_owner),
                "github_url": file.get("html_url"),
            }
        except Exception:
            return None

    def _parse_frontmatter(self, content: str) -> tuple[dict[str, Any], str]:
        """
        Parseia frontmatter YAML do conteúdo markdown.

        Why: Frontmatter permite definir metadados no início do arquivo,
             formato padrão usado por Jekyll, Hugo, etc.

        Args:
            content: Conteúdo completo do arquivo markdown

        Returns:
            Tupla (metadados, corpo do post)
        """
        # Verifica se tem frontmatter (--- no início)
        if not content.startswith("---"):
            return {}, content

        # Encontra fim do frontmatter
        end_marker = content.find("---", 3)
        if end_marker == -1:
            return {}, content

        frontmatter_str = content[3:end_marker].strip()
        body = content[end_marker + 3 :].strip()

        # Parseia YAML simples (sem dependência externa)
        metadata = self._parse_simple_yaml(frontmatter_str)

        return metadata, body

    def _parse_simple_yaml(self, yaml_str: str) -> dict[str, Any]:
        """
        Parser YAML simplificado para frontmatter.

        Why: Evita dependência de PyYAML para casos simples,
             suporta strings, listas e datas básicas.
        """
        result: dict[str, Any] = {}
        current_key = None
        current_list: list[str] = []

        for line in yaml_str.split("\n"):
            line = line.rstrip()

            # Linha de lista (- item)
            if line.startswith("  - ") or line.startswith("- "):
                item = line.lstrip("- ").strip()
                current_list.append(item)
                continue

            # Se tinha lista pendente, salva
            if current_list and current_key:
                result[current_key] = current_list
                current_list = []

            # Linha key: value
            if ":" in line:
                parts = line.split(":", 1)
                key = parts[0].strip()
                value = parts[1].strip() if len(parts) > 1 else ""

                # Remove aspas
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]

                current_key = key

                if value:
                    # Lista inline [a, b, c]
                    if value.startswith("[") and value.endswith("]"):
                        items = value[1:-1].split(",")
                        result[key] = [i.strip().strip("\"'") for i in items]
                    else:
                        result[key] = value

        # Salva última lista se houver
        if current_list and current_key:
            result[current_key] = current_list

        return result

    async def sync_posts_to_db(
        self, session: AsyncSession, author_id: UUID | None = None
    ) -> list[Post]:
        """
        Sincroniza posts do GitHub com o banco de dados.

        Why: Permite manter posts do GitHub em sync com o banco local,
             útil para cache e busca avançada.

        Args:
            session: Sessão do banco de dados
            author_id: ID do autor para associar aos posts

        Returns:
            Lista de posts criados/atualizados
        """
        github_posts = await self.get_all_posts()
        synced_posts: list[Post] = []

        for gp in github_posts:
            # Verifica se já existe
            query = select(Post).where(Post.slug == gp["slug"])
            result = await session.execute(query)
            existing = result.scalar_one_or_none()

            if existing:
                # Atualiza existente
                existing.title = gp["title"]
                existing.description = gp["description"]
                existing.content = gp["content"]
                existing.category = gp["category"]
                existing.tags = gp["tags"]
                existing.image = gp.get("image")
                existing.updated_at = datetime.now(timezone.utc)
                session.add(existing)
                synced_posts.append(existing)
            else:
                # Cria novo
                post = Post(
                    title=gp["title"],
                    slug=gp["slug"],
                    description=gp["description"],
                    content=gp["content"],
                    category=gp["category"],
                    tags=gp["tags"],
                    image=gp.get("image"),
                    draft=False,
                    author_id=author_id,
                )
                session.add(post)
                synced_posts.append(post)

        await session.commit()
        return synced_posts
