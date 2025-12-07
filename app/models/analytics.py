"""
Visitor Analytics and Fingerprinting models.

Why: Capturar informações de visitantes para analytics, segurança
     e permitir comentários anônimos identificáveis.

How: SQLModel com fingerprint único baseado em características
     do browser/dispositivo + IP para rastreamento.
"""

import hashlib
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import ConfigDict
from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class EventType(str, Enum):
    """Tipos de eventos rastreados."""

    PAGE_VIEW = "page_view"
    CLICK = "click"
    SCROLL = "scroll"
    COMMENT = "comment"
    REACTION = "reaction"
    SHARE = "share"
    DOWNLOAD = "download"
    FORM_SUBMIT = "form_submit"
    SEARCH = "search"
    ERROR = "error"
    SESSION_START = "session_start"
    SESSION_END = "session_end"


class VisitorBase(SQLModel):
    """Base visitor/fingerprint model."""

    fingerprint_hash: str = Field(max_length=64, index=True)
    ip_address: Optional[str] = Field(default=None, max_length=45)  # IPv6 max length
    user_agent: Optional[str] = Field(default=None, max_length=500)

    # Browser info
    browser_name: Optional[str] = Field(default=None, max_length=50)
    browser_version: Optional[str] = Field(default=None, max_length=20)
    os_name: Optional[str] = Field(default=None, max_length=50)
    os_version: Optional[str] = Field(default=None, max_length=20)
    device_type: Optional[str] = Field(
        default=None, max_length=20
    )  # desktop, mobile, tablet

    # Screen/Display
    screen_width: Optional[int] = None
    screen_height: Optional[int] = None
    viewport_width: Optional[int] = None
    viewport_height: Optional[int] = None
    color_depth: Optional[int] = None
    pixel_ratio: Optional[float] = None

    # Language & Timezone
    language: Optional[str] = Field(default=None, max_length=10)
    timezone: Optional[str] = Field(default=None, max_length=50)
    timezone_offset: Optional[int] = None

    # Connection info
    connection_type: Optional[str] = Field(default=None, max_length=20)

    # Geolocation (from IP)
    country: Optional[str] = Field(default=None, max_length=2)
    region: Optional[str] = Field(default=None, max_length=100)
    city: Optional[str] = Field(default=None, max_length=100)

    # Feature detection
    has_touch: Optional[bool] = None
    has_cookies: Optional[bool] = None
    has_local_storage: Optional[bool] = None
    has_session_storage: Optional[bool] = None
    has_webgl: Optional[bool] = None
    webgl_vendor: Optional[str] = Field(default=None, max_length=100)
    webgl_renderer: Optional[str] = Field(default=None, max_length=200)

    # Canvas fingerprint (hash)
    canvas_hash: Optional[str] = Field(default=None, max_length=64)

    # Audio fingerprint (hash)
    audio_hash: Optional[str] = Field(default=None, max_length=64)

    # Fonts installed (hash of font list)
    fonts_hash: Optional[str] = Field(default=None, max_length=64)

    # Plugins hash
    plugins_hash: Optional[str] = Field(default=None, max_length=64)


class Visitor(VisitorBase, table=True):
    """Database model for visitors with fingerprinting."""

    __tablename__ = "visitors"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    # Optional user association (if logged in)
    user_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="users.id", index=True
    )

    # Guest display name (for anonymous comments)
    display_name: Optional[str] = Field(default=None, max_length=50)

    # First and last seen
    first_seen_at: datetime = Field(default_factory=utc_now)
    last_seen_at: datetime = Field(default_factory=utc_now)

    # Visit count
    visit_count: int = Field(default=1)

    # Trust score (for spam prevention) 0-100
    trust_score: int = Field(default=50)

    # Flags
    is_bot: bool = Field(default=False)
    is_blocked: bool = Field(default=False)

    # Extra data as JSON (renamed from 'metadata' which is reserved by SQLAlchemy)
    extra_data: dict = Field(default={}, sa_column=Column(JSON))

    model_config = ConfigDict(arbitrary_types_allowed=True)


class VisitorCreate(SQLModel):
    """Schema for creating/updating a visitor."""

    fingerprint_data: dict[str, Any]
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    display_name: Optional[str] = None


class VisitorPublic(SQLModel):
    """Public visitor info for display."""

    id: uuid.UUID
    display_name: Optional[str]
    first_seen_at: datetime
    visit_count: int


# =============================================================================
# Analytics Event Model
# =============================================================================


class AnalyticsEventBase(SQLModel):
    """Base analytics event model."""

    event_type: EventType
    page_url: str = Field(max_length=2000)
    page_title: Optional[str] = Field(default=None, max_length=200)

    # Referrer
    referrer_url: Optional[str] = Field(default=None, max_length=2000)
    referrer_domain: Optional[str] = Field(default=None, max_length=200)

    # UTM parameters
    utm_source: Optional[str] = Field(default=None, max_length=100)
    utm_medium: Optional[str] = Field(default=None, max_length=100)
    utm_campaign: Optional[str] = Field(default=None, max_length=100)
    utm_term: Optional[str] = Field(default=None, max_length=100)
    utm_content: Optional[str] = Field(default=None, max_length=100)

    # Event specific data
    element_id: Optional[str] = Field(default=None, max_length=100)
    element_class: Optional[str] = Field(default=None, max_length=200)
    element_text: Optional[str] = Field(default=None, max_length=200)

    # Scroll tracking
    scroll_depth: Optional[int] = None  # percentage 0-100

    # Time on page (in seconds)
    time_on_page: Optional[int] = None

    # Session info
    session_id: Optional[str] = Field(default=None, max_length=64, index=True)
    page_load_time: Optional[int] = None  # milliseconds


class AnalyticsEvent(AnalyticsEventBase, table=True):
    """Database model for analytics events."""

    __tablename__ = "analytics_events"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    visitor_id: uuid.UUID = Field(foreign_key="visitors.id", index=True)

    # Timestamp
    created_at: datetime = Field(default_factory=utc_now, index=True)

    # Extra event data as JSON
    event_data: dict = Field(default={}, sa_column=Column(JSON))

    # OpenTelemetry trace ID for correlation
    trace_id: Optional[str] = Field(default=None, max_length=32)
    span_id: Optional[str] = Field(default=None, max_length=16)

    model_config = ConfigDict(arbitrary_types_allowed=True)


class AnalyticsEventCreate(SQLModel):
    """Schema for creating an analytics event."""

    event_type: EventType
    page_url: str
    page_title: Optional[str] = None
    referrer_url: Optional[str] = None
    session_id: Optional[str] = None
    event_data: Optional[dict] = None
    scroll_depth: Optional[int] = None
    time_on_page: Optional[int] = None


# =============================================================================
# Session Model
# =============================================================================


class SessionBase(SQLModel):
    """Base session model for tracking user sessions."""

    session_token: str = Field(max_length=64, unique=True, index=True)

    # Session timing
    started_at: datetime = Field(default_factory=utc_now)
    last_activity_at: datetime = Field(default_factory=utc_now)
    ended_at: Optional[datetime] = None

    # Entry point
    landing_page: str = Field(max_length=2000)
    exit_page: Optional[str] = Field(default=None, max_length=2000)

    # Session stats
    page_views: int = Field(default=1)
    events_count: int = Field(default=0)
    total_time_seconds: int = Field(default=0)

    # Is active
    is_active: bool = Field(default=True)


class Session(SessionBase, table=True):
    """Database model for user sessions."""

    __tablename__ = "sessions"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    visitor_id: uuid.UUID = Field(foreign_key="visitors.id", index=True)

    # Campaign attribution
    utm_source: Optional[str] = Field(default=None, max_length=100)
    utm_medium: Optional[str] = Field(default=None, max_length=100)
    utm_campaign: Optional[str] = Field(default=None, max_length=100)

    # Referrer
    referrer_domain: Optional[str] = Field(default=None, max_length=200)

    model_config = ConfigDict(arbitrary_types_allowed=True)


# =============================================================================
# Utility Functions
# =============================================================================


def generate_fingerprint_hash(data: dict[str, Any]) -> str:
    """
    Gera um hash único baseado nos dados de fingerprint.

    Why: Criar identificador único para visitantes anônimos
         sem armazenar dados sensíveis diretamente.
    """
    # Campos usados para o fingerprint (ordem importa)
    fingerprint_fields = [
        str(data.get("user_agent", "")),
        str(data.get("screen_width", "")),
        str(data.get("screen_height", "")),
        str(data.get("color_depth", "")),
        str(data.get("timezone_offset", "")),
        str(data.get("language", "")),
        str(data.get("canvas_hash", "")),
        str(data.get("webgl_vendor", "")),
        str(data.get("webgl_renderer", "")),
        str(data.get("fonts_hash", "")),
        str(data.get("audio_hash", "")),
    ]

    fingerprint_string = "|".join(fingerprint_fields)
    return hashlib.sha256(fingerprint_string.encode()).hexdigest()


def generate_session_token() -> str:
    """Gera um token único para sessão."""
    return hashlib.sha256(
        f"{uuid.uuid4()}{datetime.now().timestamp()}".encode()
    ).hexdigest()
