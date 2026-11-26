"""Tests for JWT authentication security."""

from datetime import UTC, datetime, timedelta

import jwt
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.config import get_settings
from app.security import get_current_user


def make_token(**overrides: object) -> str:
    """Generate a signed test token."""
    settings = get_settings()
    now = datetime.now(UTC)

    payload = {
        "sub": "test-agent",
        "tenant_id": "test-tenant",
        "roles": ["n8n-agent"],
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "iat": now,
        "exp": now + timedelta(minutes=5),
    }
    payload.update(overrides)

    return jwt.encode(
        payload,
        settings.jwt_secret_key.get_secret_value(),
        algorithm="HS256",
    )


def authenticate(token: str):
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=token,
    )
    return get_current_user(credentials)


def test_valid_token():
    user = authenticate(make_token())
    assert user.tenant_id == "test-tenant"
    assert "n8n-agent" in user.roles


def test_missing_token():
    with pytest.raises(HTTPException) as exc:
        get_current_user(None)
    assert exc.value.status_code == 401


def test_expired_token():
    token = make_token(exp=datetime.now(UTC) - timedelta(minutes=1))
    with pytest.raises(HTTPException) as exc:
        authenticate(token)
    assert exc.value.status_code == 401


def test_invalid_signature():
    token = jwt.encode(
        {
            "sub": "test-agent",
            "tenant_id": "test-tenant",
            "roles": ["n8n-agent"],
            "iss": get_settings().jwt_issuer,
            "aud": get_settings().jwt_audience,
            "iat": datetime.now(UTC),
            "exp": datetime.now(UTC) + timedelta(minutes=5),
        },
        "incorrect-test-signing-key-32bytes-long",
        algorithm="HS256",
    )

    with pytest.raises(HTTPException) as exc:
        authenticate(token)
    assert exc.value.status_code == 401


def test_missing_required_role():
    with pytest.raises(HTTPException) as exc:
        authenticate(make_token(roles=["reader"]))
    assert exc.value.status_code == 401


def test_missing_tenant():
    with pytest.raises(HTTPException) as exc:
        authenticate(make_token(tenant_id=""))
    assert exc.value.status_code == 401
