from __future__ import annotations

from collections.abc import Callable, Iterator
from dataclasses import dataclass

from fastapi.testclient import TestClient

import app.services.contact as contact_service_module
from app.core.dependencies import (
    get_analytics_service,
    get_contact_orchestrator,
)
from app.domain.schemas import ContactForm
from app.infrastructure.notifications.email import (
    NotificationChannelResult,
    NotificationDispatchResult,
)
from app.main import create_app
from app.observability.analytics import AnalyticsIngestResult
from app.services.contact import ContactOrchestrator, ContactPageService


def _build_client(
    *,
    overrides: dict[Callable[..., object], Callable[[], object]] | None = None,
) -> Iterator[TestClient]:
    app = create_app()
    if overrides:
        app.dependency_overrides.update(overrides)
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()


def _contact_payload(*, csrf_token: str = "csrf-token") -> dict[str, str]:
    return {
        "name": "Alice Example",
        "email": "alice@example.com",
        "subject": "Portfolio Contact",
        "message": "Hello, this is a valid contact message for route tests.",
        "csrf_token": csrf_token,
    }


class StubAnalyticsService:
    def __init__(self, result: AnalyticsIngestResult) -> None:
        self._result = result

    def ingest_events(
        self,
        events: list[object],
        *,
        request_id: str,
        client_ip: str,
        user_agent: str,
    ) -> AnalyticsIngestResult:
        del events, request_id, client_ip, user_agent
        return self._result


class AcceptAllAnalyticsService:
    def ingest_events(
        self,
        events: list[object],
        *,
        request_id: str,
        client_ip: str,
        user_agent: str,
    ) -> AnalyticsIngestResult:
        del request_id, client_ip, user_agent
        return AnalyticsIngestResult(accepted=len(events), rejected=0, errors=())


@dataclass(frozen=True)
class StubSubmissionResult:
    is_valid: bool
    contact: ContactForm | None
    form_data: dict[str, str]
    errors: dict[str, str]
    status_code: int


class StubSubmissionService:
    def __init__(self, result: StubSubmissionResult) -> None:
        self._result = result

    def process(
        self,
        *,
        name: str,
        email: str,
        subject: str,
        message: str,
        csrf_token: str,
        client_ip: str,
        user_agent: str,
    ) -> StubSubmissionResult:
        del name, email, subject, message, csrf_token, client_ip, user_agent
        return self._result


class StubNotificationService:
    def __init__(self, dispatch_result: NotificationDispatchResult) -> None:
        self._dispatch_result = dispatch_result

    async def notify_submission(
        self,
        contact: ContactForm,
        context: object,
    ) -> NotificationDispatchResult:
        del contact, context
        return self._dispatch_result


def _make_orchestrator(
    *,
    submission_service: object | None = None,
    notification_service: object | None = None,
    analytics_service: object | None = None,
) -> ContactOrchestrator:
    """Build a ContactOrchestrator with optional stub services."""
    return ContactOrchestrator(
        page_service=ContactPageService(),
        submission_service=submission_service,  # type: ignore[arg-type]
        notification_service=notification_service  # type: ignore[arg-type]
        or StubNotificationService(NotificationDispatchResult(results=())),
        analytics_service=analytics_service or AcceptAllAnalyticsService(),  # type: ignore[arg-type]
    )


def test_health_endpoint_returns_ok() -> None:
    for client in _build_client():
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


def test_analytics_track_route_returns_accept_message() -> None:
    analytics_service = StubAnalyticsService(
        AnalyticsIngestResult(accepted=1, rejected=0, errors=())
    )
    overrides = {get_analytics_service: lambda: analytics_service}

    for client in _build_client(overrides=overrides):
        response = client.post(
            "/api/v1/analytics/track",
            json={"events": [{"event_name": "page_view", "page_path": "/"}]},
            headers={"user-agent": "pytest-agent"},
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["accepted"] == 1
        assert payload["rejected"] == 0
        assert payload["message"] == "Events accepted."
        assert payload["errors"] == []


def test_analytics_track_route_returns_rejection_message() -> None:
    analytics_service = StubAnalyticsService(
        AnalyticsIngestResult(
            accepted=1,
            rejected=1,
            errors=("Invalid event metadata.",),
        )
    )
    overrides = {get_analytics_service: lambda: analytics_service}

    for client in _build_client(overrides=overrides):
        response = client.post(
            "/api/v1/analytics/track",
            json={"events": [{"event_name": "page_view", "page_path": "/"}]},
            headers={"user-agent": "pytest-agent"},
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["accepted"] == 1
        assert payload["rejected"] == 1
        assert payload["message"] == "Some events were rejected."
        assert payload["errors"] == ["Invalid event metadata."]


def test_contact_route_rejects_unsupported_content_type() -> None:
    contact_payload = _contact_payload()
    orchestrator = _make_orchestrator()
    overrides = {get_contact_orchestrator: lambda: orchestrator}

    original_checker = contact_service_module.is_allowed_form_content_type
    contact_service_module.is_allowed_form_content_type = lambda _: False
    try:
        for client in _build_client(overrides=overrides):
            response = client.post("/contact", data=contact_payload)
            assert response.status_code == 415
            assert "Unsupported content type." in response.text
    finally:
        contact_service_module.is_allowed_form_content_type = original_checker


def test_contact_route_handles_unexpected_submission_state() -> None:
    contact_payload = _contact_payload()
    submission_result = StubSubmissionResult(
        is_valid=True,
        contact=None,
        form_data=contact_payload,
        errors={},
        status_code=200,
    )
    orchestrator = _make_orchestrator(
        submission_service=StubSubmissionService(submission_result),
    )
    overrides = {get_contact_orchestrator: lambda: orchestrator}

    for client in _build_client(overrides=overrides):
        response = client.post("/contact", data=contact_payload)

        assert response.status_code == 500
        assert "Unexpected contact submission state." in response.text


def test_contact_route_returns_503_when_notifications_fail() -> None:
    contact_payload = _contact_payload()
    contact = ContactForm(**contact_payload)
    submission_result = StubSubmissionResult(
        is_valid=True,
        contact=contact,
        form_data=contact_payload,
        errors={},
        status_code=200,
    )
    failed_dispatch = NotificationDispatchResult(
        results=(
            NotificationChannelResult(
                channel="webhook",
                success=False,
                error="Webhook timeout.",
            ),
        )
    )
    orchestrator = _make_orchestrator(
        submission_service=StubSubmissionService(submission_result),
        notification_service=StubNotificationService(failed_dispatch),
    )
    overrides = {get_contact_orchestrator: lambda: orchestrator}

    for client in _build_client(overrides=overrides):
        response = client.post("/contact", data=contact_payload)

        assert response.status_code == 503
        assert "could not be delivered right now" in response.text


def test_contact_route_records_partial_success_outcome() -> None:
    contact_payload = _contact_payload()
    contact = ContactForm(**contact_payload)
    submission_result = StubSubmissionResult(
        is_valid=True,
        contact=contact,
        form_data=contact_payload,
        errors={},
        status_code=200,
    )
    partial_dispatch = NotificationDispatchResult(
        results=(
            NotificationChannelResult(channel="webhook", success=True),
            NotificationChannelResult(
                channel="email",
                success=False,
                error="Temporary SMTP error.",
            ),
        )
    )
    orchestrator = _make_orchestrator(
        submission_service=StubSubmissionService(submission_result),
        notification_service=StubNotificationService(partial_dispatch),
    )
    overrides = {get_contact_orchestrator: lambda: orchestrator}

    for client in _build_client(overrides=overrides):
        response = client.post("/contact", data=contact_payload)

        assert response.status_code == 200
        assert "Message sent successfully" in response.text


def test_contact_route_records_full_success_outcome() -> None:
    contact_payload = _contact_payload()
    contact = ContactForm(**contact_payload)
    submission_result = StubSubmissionResult(
        is_valid=True,
        contact=contact,
        form_data=contact_payload,
        errors={},
        status_code=200,
    )
    success_dispatch = NotificationDispatchResult(
        results=(
            NotificationChannelResult(channel="webhook", success=True),
            NotificationChannelResult(channel="email", success=True),
        )
    )
    orchestrator = _make_orchestrator(
        submission_service=StubSubmissionService(submission_result),
        notification_service=StubNotificationService(success_dispatch),
    )
    overrides = {get_contact_orchestrator: lambda: orchestrator}

    for client in _build_client(overrides=overrides):
        response = client.post("/contact", data=contact_payload)

        assert response.status_code == 200
        assert "Message sent successfully" in response.text
