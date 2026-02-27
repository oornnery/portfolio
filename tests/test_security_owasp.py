from __future__ import annotations

from collections.abc import Iterator
import re

from fastapi.testclient import TestClient
import pytest

from app.main import create_app
from app.core.config import settings


@pytest.fixture(scope="module")
def client() -> Iterator[TestClient]:
    app = create_app()
    with TestClient(app) as c:
        yield c


def _extract_csrf_token(html: str) -> str:
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert match is not None
    return match.group(1)


def _contact_payload(csrf_token: str, **overrides: str) -> dict[str, str]:
    payload = {
        "name": "Alice Example",
        "email": "alice@example.com",
        "subject": "Portfolio Contact",
        "message": "Hello, this is a valid contact message for security tests.",
        "csrf_token": csrf_token,
    }
    payload.update(overrides)
    return payload


def test_owasp_security_headers_are_set(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert response.headers["Cross-Origin-Opener-Policy"] == "same-origin"
    assert response.headers["Cross-Origin-Resource-Policy"] == "same-origin"
    assert "camera=()" in response.headers["Permissions-Policy"]
    assert "max-age=63072000" in response.headers["Strict-Transport-Security"]
    csp = response.headers["Content-Security-Policy"]
    assert "unsafe-inline" not in csp
    assert "object-src 'none'" in csp
    assert "frame-ancestors 'none'" in csp


def test_owasp_contact_reflects_user_input_escaped(client: TestClient) -> None:
    payload = "<img src=x onerror=alert(1)>"

    response = client.post(
        "/contact",
        data={
            "name": payload,
            "email": "alice@example.com",
            "subject": "Security Test",
            "message": "This message is long enough for server-side validation.",
            "csrf_token": "invalid-token",
        },
        headers={"user-agent": "pytest-agent"},
    )

    assert response.status_code == 403
    assert payload not in response.text
    assert "&lt;img src=x onerror=alert(1)&gt;" in response.text


def test_owasp_path_traversal_attempt_returns_404(client: TestClient) -> None:
    response = client.get("/projects/..%2F..%2Fetc%2Fpasswd")
    assert response.status_code == 404
    assert "root:x:0:0" not in response.text


def test_owasp_rejects_extra_fields_in_analytics_payload(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/analytics/track",
        json={
            "events": [
                {
                    "event_name": "page_view",
                    "page_path": "/",
                    "unexpected_field": "bad",
                }
            ]
        },
    )

    assert response.status_code == 422


def test_owasp_contact_requires_csrf_token_field(client: TestClient) -> None:
    response = client.post(
        "/contact",
        data={
            "name": "Alice Example",
            "email": "alice@example.com",
            "subject": "Portfolio Contact",
            "message": "Hello, this is a valid contact message.",
        },
        headers={"user-agent": "pytest-agent"},
    )

    assert response.status_code == 422


def test_owasp_contact_csrf_token_is_user_agent_bound(
    client: TestClient,
) -> None:
    get_response = client.get("/contact", headers={"user-agent": "agent-a"})
    csrf_token = _extract_csrf_token(get_response.text)

    response = client.post(
        "/contact",
        data=_contact_payload(csrf_token),
        headers={"user-agent": "agent-b"},
    )

    assert response.status_code == 403
    assert "Invalid or expired security token" in response.text


def test_owasp_contact_rate_limit_blocks_bruteforce(client: TestClient) -> None:
    get_response = client.get("/contact", headers={"user-agent": "pytest-agent"})
    csrf_token = _extract_csrf_token(get_response.text)
    payload = _contact_payload(csrf_token)

    statuses: list[int] = []
    for _ in range(12):
        response = client.post(
            "/contact",
            data=payload,
            headers={"user-agent": "pytest-agent"},
        )
        statuses.append(response.status_code)

    assert 429 in statuses


def test_owasp_contact_rejects_oversized_message_payload(
    client: TestClient,
) -> None:
    get_response = client.get("/contact", headers={"user-agent": "pytest-agent"})
    csrf_token = _extract_csrf_token(get_response.text)

    response = client.post(
        "/contact",
        data=_contact_payload(csrf_token, message="A" * 5001),
        headers={"user-agent": "pytest-agent"},
    )

    assert response.status_code == 422


def test_owasp_contact_handles_injection_strings_as_plain_data(
    client: TestClient,
) -> None:
    get_response = client.get("/contact", headers={"user-agent": "pytest-agent"})
    csrf_token = _extract_csrf_token(get_response.text)

    response = client.post(
        "/contact",
        data=_contact_payload(
            csrf_token,
            name="' OR 1=1 --",
            subject="test'); DROP TABLE users; --",
        ),
        headers={"user-agent": "pytest-agent"},
    )

    assert response.status_code == 200
    assert "Message sent successfully" in response.text


def test_owasp_analytics_rejects_batch_flood_payload(
    client: TestClient,
) -> None:
    events = [{"event_name": "page_view", "page_path": "/"} for _ in range(51)]

    response = client.post("/api/v1/analytics/track", json={"events": events})
    assert response.status_code == 422


def test_owasp_analytics_rejects_oversized_event_field(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/analytics/track",
        json={
            "events": [
                {
                    "event_name": "page_view",
                    "page_path": "/",
                    "element_text": "A" * 513,
                }
            ]
        },
    )
    assert response.status_code == 422


def test_owasp_analytics_blocks_disallowed_source_ip(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "analytics_allowed_sources", "203.0.113.10")
    app = create_app()
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/analytics/track",
            json={"events": [{"event_name": "page_view", "page_path": "/"}]},
        )
        assert response.status_code == 403


def test_owasp_default_rate_limit_applies_to_public_routes(
    client: TestClient,
) -> None:
    statuses: list[int] = []
    for _ in range(70):
        response = client.get("/")
        statuses.append(response.status_code)

    assert 429 in statuses


def test_owasp_trusted_host_blocks_unlisted_hosts(client: TestClient) -> None:
    response = client.get("/", headers={"host": "evil.example"})
    assert response.status_code == 400


def test_owasp_contact_body_size_limit_rejects_oversized_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "contact_max_body_bytes", 128)
    app = create_app()
    with TestClient(app) as client:
        get_response = client.get("/contact", headers={"user-agent": "pytest-agent"})
        csrf_token = _extract_csrf_token(get_response.text)
        response = client.post(
            "/contact",
            data=_contact_payload(csrf_token, message="A" * 500),
            headers={"user-agent": "pytest-agent"},
        )
        assert response.status_code == 413


def test_owasp_analytics_allows_forwarded_source_when_trusted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "analytics_allowed_sources", "203.0.113.10")
    monkeypatch.setattr(settings, "trust_forwarded_ip_headers", True)
    app = create_app()
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/analytics/track",
            json={"events": [{"event_name": "page_view", "page_path": "/"}]},
            headers={"x-forwarded-for": "203.0.113.10"},
        )
        assert response.status_code == 200


def test_owasp_analytics_ignores_forwarded_source_when_not_trusted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "analytics_allowed_sources", "203.0.113.10")
    monkeypatch.setattr(settings, "trust_forwarded_ip_headers", False)
    app = create_app()
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/analytics/track",
            json={"events": [{"event_name": "page_view", "page_path": "/"}]},
            headers={"x-forwarded-for": "203.0.113.10"},
        )
        assert response.status_code == 403


def test_owasp_cors_preflight_rejects_unlisted_origin(
    client: TestClient,
) -> None:
    response = client.options(
        "/api/v1/analytics/track",
        headers={
            "origin": "https://collector.example",
            "access-control-request-method": "POST",
            "access-control-request-headers": "content-type",
        },
    )
    assert response.status_code == 400
    assert response.headers.get("access-control-allow-origin") is None


def test_owasp_cors_preflight_allows_configured_origin(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "cors_allow_origins", "https://collector.example")
    monkeypatch.setattr(settings, "cors_allow_methods", "POST,OPTIONS")
    monkeypatch.setattr(settings, "cors_allow_headers", "Content-Type")
    # Need a fresh app because CORSMiddleware reads settings at construction time
    app = create_app()
    with TestClient(app) as client:
        response = client.options(
            "/api/v1/analytics/track",
            headers={
                "origin": "https://collector.example",
                "access-control-request-method": "POST",
                "access-control-request-headers": "content-type",
            },
        )
        assert response.status_code == 200
        assert response.headers.get("access-control-allow-origin") == (
            "https://collector.example"
        )


def test_owasp_global_body_limit_blocks_oversized_unknown_route(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "max_request_body_bytes", 100)
    app = create_app()
    with TestClient(app) as client:
        response = client.post(
            "/does-not-exist",
            content="A" * 300,
            headers={"content-type": "text/plain"},
        )
        assert response.status_code == 413


def test_owasp_invalid_content_length_header_is_rejected(
    client: TestClient,
) -> None:
    request = client.build_request(
        "POST",
        "/contact",
        data={
            "name": "Alice Example",
            "email": "alice@example.com",
            "subject": "Portfolio Contact",
            "message": "Hello, this is a valid contact message.",
            "csrf_token": "invalid-token",
        },
        headers={"user-agent": "pytest-agent"},
    )
    request.headers["content-length"] = "invalid-size"
    response = client.send(request)
    assert response.status_code == 400
