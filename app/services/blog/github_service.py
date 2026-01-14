"""
GitHub Blog Service - fetches posts from a GitHub repository.

Why: Permite usar um repositório GitHub como CMS para posts do blog,
     facilitando versionamento e colaboração via Git.

How: Usa a GitHub API para buscar arquivos markdown do repositório,
     parseando frontmatter YAML para metadados dos posts.
"""

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.blog import Post


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
