from __future__ import annotations

from collections.abc import Callable, Iterator
from dataclasses import dataclass

import httpx
import pytest
from fastapi.testclient import TestClient

import app.api.telemetry as telemetry_api_module
import app.services.contact as contact_service_module
from app.core.dependencies import (
    get_blog_page_service,
    get_contact_orchestrator,
    get_projects_page_service,
)
from app.models.schemas import SEOMeta
from app.models.schemas import ContactForm
from app.infrastructure.notifications.email import (
    NotificationChannelResult,
    NotificationDispatchResult,
)
from app.main import create_app
from app.services.contact import ContactOrchestrator, ContactPageService
from app.services.types import BlogPostsPageContext, ContactFormResult, PageRenderData


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
        "subject": "Site Contact",
        "message": "Hello, this is a valid contact message for route tests.",
        "csrf_token": csrf_token,
    }


def _seo() -> SEOMeta:
    return SEOMeta(
        title="Route Test",
        description="Route coverage test description.",
    )


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


class StubTelemetryAsyncClient:
    def __init__(
        self,
        *,
        response: httpx.Response | None = None,
        error: httpx.HTTPError | None = None,
    ) -> None:
        self._response = response or httpx.Response(status_code=202, content=b"")
        self._error = error
        self.calls: list[dict[str, object]] = []
        self.init_kwargs: dict[str, object] = {}

    async def __aenter__(self) -> "StubTelemetryAsyncClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        del exc_type, exc, tb

    async def post(
        self,
        url: str,
        *,
        content: bytes,
        headers: dict[str, str],
    ) -> httpx.Response:
        self.calls.append(
            {
                "url": url,
                "content": content,
                "headers": headers,
            }
        )
        if self._error is not None:
            raise self._error
        return self._response


class WrongBlogTagsPageService:
    def build_tags_page(self, tag: str | None = None) -> PageRenderData:
        del tag
        return PageRenderData(
            template="pages/blog/tags.jinja",
            context=BlogPostsPageContext(seo=_seo(), posts=()),
        )


class WrongProjectsPageService:
    def build_list_page(
        self,
        *,
        q: str = "",
        tag: str = "",
        page: int = 1,
    ) -> PageRenderData:
        del q, tag, page
        return PageRenderData(
            template="pages/projects/list.jinja",
            context=BlogPostsPageContext(seo=_seo(), posts=()),
        )


class WrongContactOrchestrator:
    async def handle_submission(
        self,
        *,
        name: str,
        email: str,
        subject: str,
        message: str,
        csrf_token: str,
        content_type: str,
        client_ip: str,
        user_agent: str,
        request_id: str,
    ) -> ContactFormResult:
        del (
            name,
            email,
            subject,
            message,
            csrf_token,
            content_type,
            client_ip,
            user_agent,
            request_id,
        )
        return ContactFormResult(
            page=PageRenderData(
                template="pages/contact.jinja",
                context=BlogPostsPageContext(seo=_seo(), posts=()),
            ),
            status_code=422,
            outcome="validation_error",
        )


def _make_orchestrator(
    *,
    submission_service: object | None = None,
    notification_service: object | None = None,
) -> ContactOrchestrator:
    """Build a ContactOrchestrator with optional stub services."""
    return ContactOrchestrator(
        page_service=ContactPageService(),
        submission_service=submission_service,  # type: ignore[arg-type]
        notification_service=notification_service  # type: ignore[arg-type]
        or StubNotificationService(NotificationDispatchResult(results=())),
    )


def test_health_endpoint_returns_ok() -> None:
    for client in _build_client():
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


def test_frontend_telemetry_route_forwards_payload_to_collector(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    telemetry_client = StubTelemetryAsyncClient(
        response=httpx.Response(
            status_code=202,
            content=b"accepted",
            headers={"content-type": "application/x-protobuf"},
        )
    )

    def _client_factory(*args: object, **kwargs: object) -> StubTelemetryAsyncClient:
        telemetry_client.init_kwargs = dict(kwargs)
        return telemetry_client

    monkeypatch.setattr(
        telemetry_api_module.httpx,
        "AsyncClient",
        _client_factory,
    )
    monkeypatch.setattr(
        telemetry_api_module.settings, "frontend_telemetry_enabled", True
    )
    monkeypatch.setattr(
        telemetry_api_module.settings,
        "frontend_telemetry_otlp_endpoint",
        "http://collector.test:4318/v1/traces",
    )

    for client in _build_client():
        response = client.post(
            "/otel/v1/traces",
            content=b"trace-payload",
            headers={
                "content-type": "application/x-protobuf",
                "content-encoding": "gzip",
                "user-agent": "pytest-agent",
            },
        )

        assert response.status_code == 202
        assert response.content == b"accepted"
        assert telemetry_client.init_kwargs == {"timeout": 10.0}
        assert telemetry_client.calls == [
            {
                "url": "http://collector.test:4318/v1/traces",
                "content": b"trace-payload",
                "headers": {
                    "content-type": "application/x-protobuf",
                    "content-encoding": "gzip",
                    "user-agent": "pytest-agent",
                },
            }
        ]


def test_frontend_telemetry_route_returns_not_found_when_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        telemetry_api_module.settings, "frontend_telemetry_enabled", False
    )
    monkeypatch.setattr(
        telemetry_api_module.settings,
        "frontend_telemetry_otlp_endpoint",
        "http://collector.test:4318/v1/traces",
    )

    for client in _build_client():
        response = client.post("/otel/v1/traces", content=b"trace-payload")

        assert response.status_code == 404


def test_frontend_telemetry_route_returns_bad_gateway_on_upstream_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    telemetry_client = StubTelemetryAsyncClient(
        error=httpx.ConnectError("collector unavailable")
    )

    monkeypatch.setattr(
        telemetry_api_module.httpx,
        "AsyncClient",
        lambda *args, **kwargs: telemetry_client,
    )
    monkeypatch.setattr(
        telemetry_api_module.settings, "frontend_telemetry_enabled", True
    )
    monkeypatch.setattr(
        telemetry_api_module.settings,
        "frontend_telemetry_otlp_endpoint",
        "http://collector.test:4318/v1/traces",
    )

    for client in _build_client():
        response = client.post("/otel/v1/traces", content=b"trace-payload")

        assert response.status_code == 502


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


def test_blog_tags_route_returns_fragment_for_htmx_requests() -> None:
    for client in _build_client():
        response = client.get("/blog/tags", headers={"HX-Request": "true"})

        assert response.status_code == 200
        assert 'id="tag-posts"' in response.text
        assert "<html" not in response.text.lower()


def test_blog_tag_detail_route_raises_type_error_for_invalid_htmx_context() -> None:
    overrides = {get_blog_page_service: lambda: WrongBlogTagsPageService()}

    for client in _build_client(overrides=overrides):
        with pytest.raises(TypeError, match="Expected BlogTagsPageContext"):
            client.get("/blog/tags/python", headers={"HX-Request": "true"})


def test_blog_tags_route_raises_type_error_for_invalid_htmx_context() -> None:
    overrides = {get_blog_page_service: lambda: WrongBlogTagsPageService()}

    for client in _build_client(overrides=overrides):
        with pytest.raises(TypeError, match="Expected BlogTagsPageContext"):
            client.get("/blog/tags", headers={"HX-Request": "true"})


def test_projects_route_raises_type_error_for_invalid_htmx_context() -> None:
    overrides = {get_projects_page_service: lambda: WrongProjectsPageService()}

    for client in _build_client(overrides=overrides):
        with pytest.raises(TypeError, match="Expected ProjectsListPageContext"):
            client.get("/projects", headers={"HX-Request": "true"})


def test_contact_route_raises_type_error_for_invalid_htmx_context() -> None:
    contact_payload = _contact_payload()
    overrides = {get_contact_orchestrator: lambda: WrongContactOrchestrator()}

    for client in _build_client(overrides=overrides):
        with pytest.raises(TypeError, match="Expected ContactPageContext"):
            client.post(
                "/contact",
                data=contact_payload,
                headers={"HX-Request": "true"},
            )


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
