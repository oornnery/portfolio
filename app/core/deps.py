"""
Dependency injection utilities for FastAPI.

Why: Centraliza lógica de autenticação e autorização,
     garantindo consistência em todos os endpoints.

How: Dependencies que extraem usuário do JWT em cookies,
     com versões obrigatória e opcional.
"""

import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.db import get_session
from app.models.user import User


def _extract_token_from_cookie(request: Request) -> str | None:
    """
    Extrai token JWT do cookie de autenticação.

    Formato esperado: "Bearer <token>"
    """
    token_cookie = request.cookies.get("access_token")
    if not token_cookie:
        return None

    # Extrai token do formato "Bearer <token>"
    scheme, _, token = token_cookie.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None

    return token


async def _get_user_from_token(
    token: str,
    session: AsyncSession,
) -> User | None:
    """
    Busca usuário a partir do token JWT.

    Returns:
        User se token válido e usuário existe, None caso contrário.
    """
    payload = decode_access_token(token)
    if not payload:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    try:
        user = await session.get(User, uuid.UUID(user_id))
        # Verifica se usuário ainda está ativo
        if user and not getattr(user, "is_active", True):
            return None
        return user
    except (ValueError, TypeError):
        return None


async def get_current_user_optional(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> User | None:
    """
    Retorna usuário atual se autenticado, None caso contrário.

    Use para páginas públicas que podem ter funcionalidades extras
    para usuários autenticados.
    """
    token = _extract_token_from_cookie(request)
    if not token:
        return None

    return await _get_user_from_token(token, session)


async def get_current_user(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> User:
    """
    Retorna usuário atual ou raises HTTPException 401.

    Use para endpoints que REQUEREM autenticação.
    """
    token = _extract_token_from_cookie(request)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await _get_user_from_token(token, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_admin_user(
    user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Retorna usuário atual se for admin, caso contrário raises 403.

    Use para endpoints administrativos.
    """
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return user


# Type aliases para uso nos endpoints
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentUserOptional = Annotated[User | None, Depends(get_current_user_optional)]
CurrentAdminUser = Annotated[User, Depends(get_current_admin_user)]
