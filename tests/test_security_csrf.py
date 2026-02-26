import hashlib
import hmac
import secrets
import time

from app.config import settings
from app.security import generate_csrf_token, validate_csrf_token


def test_csrf_roundtrip_valid_for_same_user_agent() -> None:
    user_agent = "pytest-agent"
    token = generate_csrf_token(user_agent=user_agent)

    assert validate_csrf_token(token, user_agent=user_agent) is True


def test_csrf_rejects_different_user_agent() -> None:
    token = generate_csrf_token(user_agent="agent-a")

    assert validate_csrf_token(token, user_agent="agent-b") is False


def test_csrf_rejects_expired_token() -> None:
    timestamp = int(time.time()) - (settings.csrf_token_expiry + 10)
    random_part = secrets.token_hex(16)
    user_agent_hash = hashlib.sha256("pytest-agent".encode()).hexdigest()[:16]
    payload = f"{timestamp}:{random_part}:{user_agent_hash}"
    signature = hmac.new(
        settings.secret_key.encode(),
        payload.encode(),
        hashlib.sha256,
    ).hexdigest()
    token = f"{payload}:{signature}"

    assert validate_csrf_token(token, user_agent="pytest-agent") is False

