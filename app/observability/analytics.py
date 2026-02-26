from dataclasses import dataclass
from functools import lru_cache
import hashlib
import hmac
import logging
from typing import Any

from app.core.config import settings
from app.observability.events import LogEvent
from app.core.logger import event_message
from app.domain.schemas import AnalyticsTrackEvent
from app.observability.telemetry import get_meter, get_tracer

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AnalyticsIngestResult:
    accepted: int
    rejected: int
    errors: tuple[str, ...]


class AnalyticsService:
    def __init__(self) -> None:
        meter = get_meter(__name__)
        self._event_counter = meter.create_counter(
            name="portfolio.analytics.events_total",
            description="Total analytics events accepted.",
            unit="1",
        )
        self._rejected_counter = meter.create_counter(
            name="portfolio.analytics.events_rejected_total",
            description="Total analytics events rejected.",
            unit="1",
        )
        self._tracer = get_tracer(__name__)

    @staticmethod
    def _redact_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
        redacted: dict[str, Any] = {}
        sensitive_keys = {
            "email",
            "name",
            "phone",
            "message",
            "password",
            "token",
            "secret",
            "subject",
            "client_ip",
            "ip",
            "user_agent",
        }
        for key, value in metadata.items():
            normalized_key = str(key).strip().lower()
            if normalized_key in sensitive_keys:
                redacted[normalized_key] = "[redacted]"
                continue
            if isinstance(value, str):
                redacted[normalized_key] = value[:256]
                continue
            if isinstance(value, (int, float, bool)) or value is None:
                redacted[normalized_key] = value
                continue
            redacted[normalized_key] = str(value)[:256]
        return redacted

    @staticmethod
    def _hash_identifier(value: str, *, namespace: str) -> str:
        normalized = value.strip().lower()
        if not normalized:
            return "unknown"
        digest = hmac.new(
            settings.secret_key.encode(),
            f"{namespace}:{normalized}".encode(),
            hashlib.sha256,
        ).hexdigest()
        return digest[:16]

    def ingest_events(
        self,
        events: list[AnalyticsTrackEvent],
        *,
        request_id: str,
        client_ip: str,
        user_agent: str,
    ) -> AnalyticsIngestResult:
        if not settings.analytics_enabled:
            return AnalyticsIngestResult(
                accepted=0,
                rejected=len(events),
                errors=("Analytics is disabled by configuration.",),
            )

        accepted = 0
        rejected = 0
        errors: list[str] = []

        with self._tracer.start_as_current_span("analytics.ingest_batch") as span:
            span.set_attribute("analytics.event_count", len(events))
            span.set_attribute("http.request_id", request_id)
            span.set_attribute(
                "client.ip_hash",
                self._hash_identifier(client_ip, namespace="client_ip"),
            )
            span.set_attribute(
                "client.user_agent_hash",
                self._hash_identifier(user_agent, namespace="user_agent"),
            )

            for event in events:
                try:
                    attributes = {
                        "event_name": event.event_name,
                        "page_path": event.page_path,
                    }
                    self._event_counter.add(1, attributes=attributes)
                    accepted += 1

                    if settings.analytics_log_events:
                        logger.info(
                            event_message(
                                LogEvent.ANALYTICS_EVENT_ACCEPTED,
                                event_name=event.event_name,
                                page_path=event.page_path,
                                request_id=request_id,
                                metadata=self._redact_metadata(event.metadata),
                            )
                        )
                except Exception as exc:  # pragma: no cover
                    rejected += 1
                    self._rejected_counter.add(
                        1, attributes={"reason": "processing_exception"}
                    )
                    error = (
                        f"Failed to process analytics event event_name={event.event_name}: "
                        f"{exc.__class__.__name__}"
                    )
                    errors.append(error)
                    logger.exception(
                        event_message(
                            LogEvent.ANALYTICS_EVENT_REJECTED,
                            event_name=event.event_name,
                            request_id=request_id,
                            reason=exc.__class__.__name__,
                        )
                    )

            span.set_attribute("analytics.accepted", accepted)
            span.set_attribute("analytics.rejected", rejected)

        return AnalyticsIngestResult(
            accepted=accepted,
            rejected=rejected,
            errors=tuple(errors),
        )


@lru_cache(maxsize=1)
def build_analytics_service() -> AnalyticsService:
    return AnalyticsService()
