from dataclasses import dataclass
from functools import lru_cache
import logging
from typing import Any

from app.config import settings
from app.schemas import AnalyticsTrackEvent
from app.telemetry import get_meter, get_tracer

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
        }
        for key, value in metadata.items():
            normalized_key = str(key).strip().lower()
            if normalized_key in sensitive_keys:
                redacted[normalized_key] = "[redacted]"
                continue
            redacted[normalized_key] = value
        return redacted

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
            span.set_attribute("client.ip", client_ip)
            span.set_attribute("client.user_agent", user_agent[:256])

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
                            f"Analytics event accepted event_name={event.event_name} "
                            f"page_path={event.page_path} request_id={request_id} "
                            f"metadata={self._redact_metadata(event.metadata)}"
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
                    logger.exception(f"{error} request_id={request_id}")

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
