"""
Authentication service for user management and JWT operations.

Why: Centraliza lógica de autenticação, incluindo
     OAuth, JWT e gerenciamento de sessões.

How: Abstrai detalhes de providers OAuth e geração de tokens,
     expondo interface limpa para os routers.
"""

from datetime import timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    get_password_hash,
    verify_password,
)
from app.models.user import User


class AuthService:
    """
    Serviço para operações de autenticação.

    Why: Mantém lógica de auth separada dos handlers,
         facilitando testes e mudanças de estratégia.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_user_by_email(self, email: str) -> User | None:
        """Busca usuário pelo email."""
        query = select(User).where(User.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        """Busca usuário pelo ID."""
        return await self.session.get(User, user_id)

    async def authenticate_user(self, email: str, password: str) -> User | None:
        """
        Autentica usuário com email e senha.

        Returns:
            User se credenciais válidas, None caso contrário
        """
        user = await self.get_user_by_email(email)

        if not user:
            return None

        if not user.hashed_password:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        return user

    async def create_user(
        self,
        *,
        email: str,
        name: str,
        password: str | None = None,
        avatar_url: str | None = None,
        provider: str = "email",
        provider_id: str | None = None,
    ) -> User:
        """
        Cria um novo usuário.

        Args:
            email: Email único do usuário
            name: Nome de exibição
            password: Senha (opcional para OAuth)
            avatar_url: URL do avatar
            provider: Provider de auth (email, github, google)
            provider_id: ID no provider OAuth
        """
        hashed_password = None
        if password:
            hashed_password = get_password_hash(password)

        user = User(
            email=email,
            name=name,
            hashed_password=hashed_password,
            avatar_url=avatar_url,
            provider=provider,
            provider_id=provider_id,
        )

        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_or_create_oauth_user(
        self,
        *,
        email: str,
        name: str,
        avatar_url: str | None = None,
        provider: str,
        provider_id: str,
    ) -> User:
        """
        Busca ou cria usuário OAuth.

        Why: OAuth users podem já existir de login anterior,
             então precisamos verificar antes de criar.
        """
        user = await self.get_user_by_email(email)

        if user:
            # Atualiza dados que podem ter mudado no provider
            user.name = name
            user.avatar_url = avatar_url
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            return user

        return await self.create_user(
            email=email,
            name=name,
            avatar_url=avatar_url,
            provider=provider,
            provider_id=provider_id,
        )

    def create_token_for_user(self, user: User) -> str:
        """
        Cria JWT access token para o usuário.

        Returns:
            Token JWT como string
        """
        return create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        )
