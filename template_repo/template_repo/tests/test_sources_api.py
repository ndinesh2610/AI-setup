"""API tests for authorized source passage access."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routers import sources
from app.security import AuthenticatedUser, get_current_user
from app.services.source_passages import SourcePassage

client = TestClient(app)


class FakeConnection:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


@pytest.fixture
def authorized_user():
    user = AuthenticatedUser(tenant_id="company_a", roles=["employee"])
    app.dependency_overrides[get_current_user] = lambda: user
    yield user
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture
def fake_database(monkeypatch):
    monkeypatch.setattr(
        sources.psycopg,
        "connect",
        lambda **kwargs: FakeConnection(),
    )


def test_authorized_user_receives_exact_source(monkeypatch, authorized_user, fake_database):
    monkeypatch.setattr(
        sources,
        "get_source_passage",
        lambda document_id, user, connection: SourcePassage(
            document_id=1,
            source="company_policies",
            passage="Employees receive 20 days of leave.",
        ),
    )

    response = client.get("/sources/1")

    assert response.status_code == 200
    assert response.json() == {
        "document_id": 1,
        "source": "company_policies",
        "passage": "Employees receive 20 days of leave.",
    }


@pytest.mark.parametrize("document_id", [1, 6, 999])
def test_missing_or_unauthorized_source_returns_404(
    monkeypatch, authorized_user, fake_database, document_id
):
    monkeypatch.setattr(
        sources,
        "get_source_passage",
        lambda document_id, user, connection: None,
    )

    response = client.get(f"/sources/{document_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Source passage not found."


def test_source_without_authentication_returns_401():
    app.dependency_overrides.pop(get_current_user, None)

    response = client.get("/sources/1")

    assert response.status_code == 401
