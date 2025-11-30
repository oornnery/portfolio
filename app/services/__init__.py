"""
Services layer for business logic.

Why: Separa a lógica de negócio dos routers/views,
     permitindo reutilização e testes isolados.

How: Cada service encapsula operações de um domínio específico,
     recebendo o repository como dependência.
"""

from app.services.auth import AuthService
from app.services.blog import BlogService, GitHubBlogService
from app.services.profile import ProfileService
from app.services.project import ProjectService

__all__ = [
    "AuthService",
    "BlogService",
    "GitHubBlogService",
    "ProfileService",
    "ProjectService",
]
