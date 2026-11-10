"""Health and ask endpoint tests."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.security import AuthenticatedUser, get_current_user

client = TestClient(app)


@pytest.fixture(autouse=True)
def authenticated_test_user():
    """Inject a test identity for tests in this module only."""
    app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(
        tenant_id="test_tenant",
        roles=["employee"],
    )
    yield
    app.dependency_overrides.pop(get_current_user, None)


def test_health_alive_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_no_problems_returns_ready():
    response = client.get("/health/ready")
    assert response.status_code == 200


def test_request_id_is_returned_and_reused():
    response = client.get("/health", headers={"X-Request-ID": "abc-123"})
    assert response.headers["X-Request-ID"] == "abc-123"


def test_ask_without_sources_says_i_dont_know():
    response = client.post("/ask", json={"question": "What is the loan limit?"})
    assert response.status_code == 200
    assert response.json()["answer"].startswith("I don't know")


def test_ask_empty_question_is_rejected_with_422():
    response = client.post("/ask", json={"question": ""})
    assert response.status_code == 422


def test_ask_very_long_question_is_rejected_with_422():
    response = client.post("/ask", json={"question": "x" * 5000})
    assert response.status_code == 422
