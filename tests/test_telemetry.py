from __future__ import annotations

import app.observability.telemetry as telemetry
from app.core.config import Settings


class RecordingSpan:
    def __init__(self, *, recording: bool = True) -> None:
        self._recording = recording
        self.events: list[tuple[str, dict[str, object]]] = []
        self.attributes: list[dict[str, object]] = []

    def is_recording(self) -> bool:
        return self._recording

    def add_event(self, name: str, attributes: dict[str, object]) -> None:
        self.events.append((name, attributes))

    def set_attributes(self, attributes: dict[str, object]) -> None:
        self.attributes.append(attributes)


def test_add_current_span_event_records_event(monkeypatch) -> None:
    span = RecordingSpan()
    monkeypatch.setattr(telemetry.trace, "get_current_span", lambda: span)

    telemetry.add_current_span_event(
        "contact.submission.received",
        {"channel_count": 2, "valid": True},
    )

    assert span.events == [
        ("contact.submission.received", {"channel_count": 2, "valid": True})
    ]


def test_add_current_span_event_skips_non_recording_span(monkeypatch) -> None:
    span = RecordingSpan(recording=False)
    monkeypatch.setattr(telemetry.trace, "get_current_span", lambda: span)

    telemetry.add_current_span_event("contact.submission.received")

    assert span.events == []


def test_set_current_span_attributes_sets_attributes(monkeypatch) -> None:
    span = RecordingSpan()
    monkeypatch.setattr(telemetry.trace, "get_current_span", lambda: span)

    telemetry.set_current_span_attributes({"outcome": "success", "attempts": 1})

    assert span.attributes == [{"outcome": "success", "attempts": 1}]


def test_frontend_telemetry_collector_endpoint_is_derived_from_backend_otlp() -> None:
    settings = Settings(
        secret_key="test-secret-key-with-sufficient-length",
        otel_exporter_otlp_endpoint="http://localhost:4317",
    )

    assert settings.frontend_telemetry_collector_endpoint() == (
        "http://localhost:4318/v1/traces"
    )


def test_frontend_telemetry_collector_endpoint_appends_http_path_for_root_https() -> (
    None
):
    settings = Settings(
        secret_key="test-secret-key-with-sufficient-length",
        otel_exporter_otlp_endpoint="https://ingest.us.signoz.cloud:443",
    )

    assert settings.frontend_telemetry_collector_endpoint() == (
        "https://ingest.us.signoz.cloud:443/v1/traces"
    )


def test_frontend_telemetry_browser_endpoint_uses_same_origin_proxy() -> None:
    settings = Settings(
        secret_key="test-secret-key-with-sufficient-length",
        frontend_telemetry_enabled=True,
        otel_exporter_otlp_endpoint="http://localhost:4317",
    )

    assert settings.frontend_telemetry_is_enabled() is True
    assert settings.frontend_telemetry_browser_endpoint() == "/otel/v1/traces"


def test_settings_accept_standard_otel_environment_aliases(monkeypatch) -> None:
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://collector:4317")
    monkeypatch.setenv(
        "FRONTEND_TELEMETRY_SERVICE_NAMESPACE",
        "site-browser",
    )

    settings = Settings(
        _env_file=None,
        secret_key="test-secret-key-with-sufficient-length",
    )

    assert settings.otel_exporter_otlp_endpoint == "http://collector:4317"
    assert settings.frontend_telemetry_service_namespace == "site-browser"
