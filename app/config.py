"""
Application configuration via environment variables.

Why: Centraliza configurações em um único lugar,
     com validação automática via Pydantic.

How: Pydantic-settings carrega do .env e valida tipos.
     Valores sensíveis DEVEM ser definidos via variáveis de ambiente.
"""

import secrets
import warnings

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with security validations."""

    PROJECT_NAME: str = "Portfolio API"
    ENV: str = "development"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./portfolio.db"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "portfolio_db"
    SEED_DB_ON_STARTUP: bool = True

    # Security - MUST be set in production
    SECRET_KEY: str = ""

    # OAuth providers
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""

    # CORS - origins permitidas
    ALLOW_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

    # Hosts permitidos (sem wildcard em produção)
    ALLOWED_HOSTS: list[str] = ["localhost", "127.0.0.1"]

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # HTTPS enforcement
    FORCE_HTTPS: bool = False  # Set True em produção com SSL

    @field_validator("SECRET_KEY", mode="before")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """
        Valida SECRET_KEY.

        Em produção: DEVE ser definida via env var.
        Em desenvolvimento: gera uma chave aleatória com warning.
        """
        if not v or v == "your-secret-key-here":
            # Gera chave aleatória para desenvolvimento
            generated_key = secrets.token_urlsafe(32)
            warnings.warn(
                "SECRET_KEY not set! Using randomly generated key. "
                "Set SECRET_KEY environment variable in production.",
                UserWarning,
                stacklevel=2,
            )
            return generated_key
        return v

    @field_validator("ALLOWED_HOSTS", mode="after")
    @classmethod
    def validate_allowed_hosts(cls, v: list[str]) -> list[str]:
        """Remove wildcard em produção."""
        return [h for h in v if h != "*"]

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.ENV.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.ENV.lower() == "development"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
