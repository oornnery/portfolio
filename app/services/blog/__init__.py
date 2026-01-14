"""
Blog services package.

Why: Organiza serviços do blog em módulos separados,
     facilitando manutenção e reduzindo tamanho de arquivos.

How: Exporta os serviços para manter compatibilidade com imports existentes.
"""

from app.services.blog.github_service import GitHubBlogService
from app.services.blog.post_service import BlogService

__all__ = ["BlogService", "GitHubBlogService"]
