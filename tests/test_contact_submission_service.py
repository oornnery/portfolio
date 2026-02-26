from app.services.use_cases import ContactSubmissionService


def test_contact_submission_success_normalizes_fields() -> None:
    service = ContactSubmissionService(
        csrf_validator=lambda token, user_agent="": bool(token and user_agent)
    )

    result = service.process(
        name="  Alice  ",
        email="  alice@example.com ",
        subject="  Hello  ",
        message="  This is a valid message body.  ",
        csrf_token="token-123",
        client_ip="127.0.0.1",
        user_agent="pytest-agent",
    )

    assert result.is_valid is True
    assert result.status_code == 200
    assert result.contact is not None
    assert result.contact.name == "Alice"
    assert str(result.contact.email) == "alice@example.com"
    assert result.contact.subject == "Hello"
    assert result.contact.message == "This is a valid message body."
    assert result.errors == {}


def test_contact_submission_rejects_invalid_csrf() -> None:
    service = ContactSubmissionService(csrf_validator=lambda token, user_agent="": False)

    result = service.process(
        name="Alice",
        email="alice@example.com",
        subject="Hello",
        message="This is a valid message body.",
        csrf_token="invalid",
        client_ip="127.0.0.1",
        user_agent="pytest-agent",
    )

    assert result.is_valid is False
    assert result.status_code == 403
    assert result.contact is None
    assert "csrf" in result.errors


def test_contact_submission_returns_validation_errors() -> None:
    service = ContactSubmissionService(csrf_validator=lambda token, user_agent="": True)

    result = service.process(
        name="A",
        email="not-an-email",
        subject="Hi",
        message="short",
        csrf_token="token-123",
        client_ip="127.0.0.1",
        user_agent="pytest-agent",
    )

    assert result.is_valid is False
    assert result.status_code == 422
    assert result.contact is None
    assert set(result.errors).intersection({"name", "email", "subject", "message"})
