"""Security tests for the ask endpoint."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_ask_without_authentication_returns_401():
    response = client.post(
        "/ask",
        json={"question": "What is the annual leave policy?"},
    )

    assert response.status_code == 401
