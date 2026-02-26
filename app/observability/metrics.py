from functools import lru_cache

from app.observability.telemetry import get_meter


class AppMetrics:
    def __init__(self) -> None:
        meter = get_meter(__name__)
        self._requests_total = meter.create_counter(
            name="portfolio.http.requests_total",
            description="Total HTTP requests served.",
            unit="1",
        )
        self._request_duration_ms = meter.create_histogram(
            name="portfolio.http.request_duration_ms",
            description="HTTP request duration in milliseconds.",
            unit="ms",
        )
        self._requests_in_flight = meter.create_up_down_counter(
            name="portfolio.http.requests_in_flight",
            description="In-flight HTTP requests.",
            unit="1",
        )
        self._contact_submissions_total = meter.create_counter(
            name="portfolio.contact.submissions_total",
            description="Total contact submissions by outcome.",
            unit="1",
        )
        self._notification_duration_ms = meter.create_histogram(
            name="portfolio.contact.notification_duration_ms",
            description="Notification channel send duration in milliseconds.",
            unit="ms",
        )
        self._notification_total = meter.create_counter(
            name="portfolio.contact.notification_total",
            description="Notification channel outcomes.",
            unit="1",
        )

    def request_started(self, *, method: str, path: str) -> None:
        self._requests_in_flight.add(1, attributes={"method": method, "path": path})

    def request_finished(
        self,
        *,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        exception_class: str = "",
    ) -> None:
        attributes = {
            "method": method,
            "path": path,
            "status_code": str(status_code),
            "exception_class": exception_class or "none",
        }
        self._requests_total.add(1, attributes=attributes)
        self._request_duration_ms.record(duration_ms, attributes=attributes)
        self._requests_in_flight.add(-1, attributes={"method": method, "path": path})

    def record_contact_submission(self, *, outcome: str) -> None:
        self._contact_submissions_total.add(1, attributes={"outcome": outcome})

    def record_notification(
        self, *, channel: str, outcome: str, duration_ms: float
    ) -> None:
        attributes = {"channel": channel, "outcome": outcome}
        self._notification_total.add(1, attributes=attributes)
        self._notification_duration_ms.record(duration_ms, attributes=attributes)


@lru_cache(maxsize=1)
def get_app_metrics() -> AppMetrics:
    return AppMetrics()
