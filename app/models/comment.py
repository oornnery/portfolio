"""
Comment models for blog post discussions.

Why: Comentários permitem interação dos leitores com o conteúdo,
     com validação e sanitização para segurança.
     Suporta comentários anônimos com fingerprinting.

How: SQLModel com validadores Pydantic para sanitização automática
     de input antes de salvar no banco.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from pydantic import ConfigDict, field_validator
from sqlmodel import Field, SQLModel

from app.core.utils import sanitize_html


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class CommentBase(SQLModel):
    """Base comment model with validation."""

    content: str = Field(min_length=1, max_length=2000)

    model_config = ConfigDict(
        json_schema_extra={"example": {"content": "Great post! Thanks for sharing."}}
    )

    @field_validator("content", mode="before")
    @classmethod
    def sanitize_content(cls, v: str) -> str:
        """
        Sanitiza conteúdo do comentário para prevenir XSS.

        Why: User-generated content DEVE ser sanitizado antes de
             qualquer processamento ou armazenamento.
        """
        if not v:
            return v
        # Remove tags HTML e escapa caracteres especiais
        return sanitize_html(v.strip())


class Comment(CommentBase, table=True):
    """Database model for comments."""

    __tablename__ = "comments"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    post_id: uuid.UUID = Field(foreign_key="posts.id", index=True)

    # User pode ser null para comentários anônimos
    user_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="users.id", index=True
    )

    # Visitor para comentários anônimos (fingerprint tracking)
    visitor_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="visitors.id", index=True
    )

    # Guest info para comentários anônimos
    guest_name: Optional[str] = Field(default=None, max_length=50)
    guest_email: Optional[str] = Field(
        default=None, max_length=254
    )  # Para gravatar/notificações

    parent_id: Optional[uuid.UUID] = Field(default=None, foreign_key="comments.id")
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    is_deleted: bool = Field(default=False)
    is_flagged: bool = Field(default=False)

    # IP e info de segurança
    ip_address: Optional[str] = Field(default=None, max_length=45)
    user_agent: Optional[str] = Field(default=None, max_length=500)


class CommentCreate(CommentBase):
    """Schema para criar comentário (authenticated ou guest)."""

    parent_id: Optional[uuid.UUID] = None
    guest_name: Optional[str] = Field(default=None, max_length=50)
    guest_email: Optional[str] = Field(default=None, max_length=254)


class CommentCreateGuest(CommentBase):
    """Schema específico para comentários de guests."""

    parent_id: Optional[uuid.UUID] = None
    guest_name: str = Field(min_length=2, max_length=50)
    guest_email: Optional[str] = Field(default=None, max_length=254)

    @field_validator("guest_name", mode="before")
    @classmethod
    def sanitize_guest_name(cls, v: str) -> str:
        """Sanitiza nome do guest."""
        if not v:
            return v
        return sanitize_html(v.strip())


class CommentUpdate(SQLModel):
    content: str = Field(min_length=1, max_length=2000)


class CommentPublic(CommentBase):
    id: uuid.UUID
    user_id: Optional[uuid.UUID]
    visitor_id: Optional[uuid.UUID]
    guest_name: Optional[str]
    parent_id: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime
    # Include user data (pode ser None para guests)
    user_name: Optional[str] = None
    user_avatar: Optional[str] = None
    # Display name (user.name ou guest_name)
    display_name: str = ""
    is_guest: bool = False
    replies: list["CommentPublic"] = []
