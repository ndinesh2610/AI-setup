"""Tests for permission-filtered document retrieval."""

from app.security import AuthenticatedUser
from app.services.retrieval import retrieve_documents


class FakeEmbedder:
    def encode(self, question: str) -> list[float]:
        assert question == "What is the leave policy?"
        return [0.1, 0.2, 0.3]


class FakeCursor:
    def __init__(self) -> None:
        self.query = ""
        self.params = ()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None

    def execute(self, query: str, params: tuple) -> None:
        self.query = query
        self.params = params

    def fetchall(self):
        return [(1, "20 days annual leave", "company_policies", 0.1)]


class FakeConnection:
    def __init__(self) -> None:
        self.cursor_instance = FakeCursor()

    def cursor(self):
        return self.cursor_instance


def test_retrieval_filters_tenant_and_roles_before_ranking():
    connection = FakeConnection()
    user = AuthenticatedUser(tenant_id="company_a", roles=["employee"])

    results = retrieve_documents(
        "What is the leave policy?",
        user,
        connection=connection,
        embedder=FakeEmbedder(),
    )

    query = connection.cursor_instance.query.upper()
    params = connection.cursor_instance.params

    assert "TENANT_ID" in query
    assert "ALLOWED_ROLES" in query
    assert "ORDER BY" in query
    assert params[0] == "company_a"
    assert params[1] == ["employee"]
    assert len(results) == 1
    assert results[0].source == "company_policies"
    assert results[0].passage == "20 days annual leave"
