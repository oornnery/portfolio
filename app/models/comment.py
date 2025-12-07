"""
Comment models for blog post discussions.

Why: Comentários permitem interação dos leitores com o conteúdo,
     com validação e sanitização para segurança.

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
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    parent_id: Optional[uuid.UUID] = Field(default=None, foreign_key="comments.id")
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    is_deleted: bool = Field(default=False)
    is_flagged: bool = Field(default=False)


class CommentCreate(CommentBase):
    parent_id: Optional[uuid.UUID] = None


class CommentUpdate(SQLModel):
    content: str = Field(min_length=1, max_length=2000)


class CommentPublic(CommentBase):
    id: uuid.UUID
    user_id: uuid.UUID
    parent_id: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime
    # Include user data
    user_name: str
    user_avatar: Optional[str]
    replies: list["CommentPublic"] = []
