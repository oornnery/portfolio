"""
Admin dependencies.

Why: Centraliza dependências comuns das rotas admin.

How: Fornece dependency injection para autenticação admin.
"""

from fastapi import Depends, HTTPException, Request, status

from app.core.deps import get_current_user_optional
from app.models.user import User


async def get_admin_user(
    request: Request, user: User | None = Depends(get_current_user_optional)
) -> User:
    """
    Verifica se o usuário está autenticado para acessar o admin.

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
