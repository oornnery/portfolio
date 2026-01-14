"""
Contact API endpoint v1.

Why: Provides a contact form endpoint for the portfolio,
     allowing visitors to send messages via the website.

How: Validates input, stores messages in database (optional),
     and can trigger email notifications.
"""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, EmailStr, Field
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)
logger = logging.getLogger(__name__)


# ==========================================
# Request/Response Models
# ==========================================


class ContactRequest(BaseModel):
    """Request body for contact form submission."""

    name: str = Field(
        min_length=2,
        max_length=100,
        description="Sender's name",
        examples=["João Silva"],
    )
    email: EmailStr = Field(
        description="Sender's email address",
        examples=["joao@example.com"],
    )
    message: str = Field(
        min_length=10,
        max_length=5000,
        description="Message content",
        examples=["Olá, gostaria de saber mais sobre seus serviços..."],
    )
    subject: str | None = Field(
        default=None,
        max_length=200,
        description="Optional subject line",
    )


class ContactResponse(BaseModel):
    """Response for successful contact form submission."""

    success: bool = True
    message: str = "Message sent successfully"
    timestamp: datetime


# ==========================================
# Endpoint
# ==========================================


@router.post(
    "",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Message sent successfully"},
        429: {"description": "Too many requests - rate limited"},
    },
)
@limiter.limit("10/minute")
async def send_contact_message(
    request: Request,
    contact: ContactRequest,
):
    """
    Submit a contact form message.

    Rate limited to 10 requests per minute per IP to prevent spam.
    Messages are logged and can be configured to send email notifications.
    """
    try:
        # Log the contact request
        logger.info(
            f"Contact form submission: name={contact.name}, "
            f"email={contact.email}, subject={contact.subject}"
        )

        # TODO: Add email notification if configured
        # TODO: Store in database if ContactMessage model exists

        # For now, just log and return success
        return ContactResponse(
            success=True,
            message="Thank you for your message! I'll get back to you soon.",
            timestamp=datetime.now(timezone.utc),
        )

    except Exception as e:
        logger.error(f"Failed to process contact form: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send message. Please try again later.",
        )
