from datetime import datetime, timezone
from typing import Optional
import uuid
from sqlmodel import Field, SQLModel
from pydantic import ConfigDict


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class UserBase(SQLModel):
    """Base user model."""

    email: str = Field(unique=True, index=True)
    name: str = Field(max_length=100)
    avatar_url: Optional[str] = Field(default=None)
    provider: str = Field(
        default="email", description="OAuth provider: github, google, discord, or email"
    )
    provider_id: Optional[str] = Field(default=None, description="Provider user ID")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "name": "John Doe",
                "avatar_url": "https://example.com/avatar.jpg",
                "provider": "github",
                "provider_id": "12345678",
            }
        }
    )


class User(UserBase, table=True):
    """Database model for users."""

    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=utc_now)
    last_login: datetime = Field(default_factory=utc_now)
    is_admin: bool = Field(default=False)
    is_banned: bool = Field(default=False)
    hashed_password: Optional[str] = Field(default=None)


class UserPublic(SQLModel):
    """Public user data (safe to expose)."""

    id: uuid.UUID
    name: str
    avatar_url: Optional[str]
    created_at: datetime
