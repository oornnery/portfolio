"""
Security utilities for authentication and password handling.

Why: Centraliza funções de segurança para garantir consistência
     e facilitar auditorias de segurança.

How: JWT com claims de segurança (iss, aud, iat, jti),
     bcrypt para hashing de senhas com salt automático.
"""

import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from jose import JWTError, jwt

from app.config import settings

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# JWT Claims
JWT_ISSUER = "portfolio-api"
JWT_AUDIENCE = "portfolio-web"


def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    """
    Cria JWT com claims de segurança.

    Claims incluídos:
        - sub: Subject (user ID)
        - exp: Expiration time
        - iat: Issued at
        - iss: Issuer
        - aud: Audience
        - jti: JWT ID (único para cada token)
    """
    to_encode = data.copy()
    now = datetime.now(timezone.utc)

    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update(
        {
            "exp": expire,
            "iat": now,
            "iss": JWT_ISSUER,
            "aud": JWT_AUDIENCE,
            "jti": secrets.token_urlsafe(16),  # Unique token ID
        }
    )

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any] | None:
    """
    Decodifica e valida JWT.

    Validações:
        - Assinatura válida
        - Token não expirado
        - Issuer correto
        - Audience correta
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM],
            issuer=JWT_ISSUER,
            audience=JWT_AUDIENCE,
        )
        return payload
    except JWTError:
        return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not hashed_password:
        return False
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
