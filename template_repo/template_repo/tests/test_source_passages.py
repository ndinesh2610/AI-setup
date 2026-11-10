"""Tests for permission-filtered source passage lookup."""

from app.security import AuthenticatedUser
from app.services.source_passages import get_source_passage


class FakeCursor:
    def __init__(self, row):
        self.row = row
        self.query = ""
        self.params = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def execute(self, query, params):
        self.query = query
        self.params = params

    def fetchone(self):
        return self.row


class FakeConnection:
    def __init__(self, row):
        self.fake_cursor = FakeCursor(row)

    def cursor(self):
        return self.fake_cursor


def test_source_lookup_returns_exact_authorized_passage():
    connection = FakeConnection((1, "company_policies", "Employees receive 20 days of leave."))
    user = AuthenticatedUser(tenant_id="company_a", roles=["employee"])

    result = get_source_passage(
        1,
        user,
        connection=connection,
    )

    assert result.document_id == 1
    assert result.source == "company_policies"
    assert result.passage == "Employees receive 20 days of leave."
    assert "tenant_id = %s" in connection.fake_cursor.query
    assert "allowed_roles && %s::text[]" in connection.fake_cursor.query
    assert connection.fake_cursor.params == (1, "company_a", ["employee"])


def test_source_lookup_returns_none_when_document_is_not_authorized():
    connection = FakeConnection(None)
    user = AuthenticatedUser(tenant_id="company_b", roles=["employee"])

    result = get_source_passage(
        1,
        user,
        connection=connection,
    )

    assert result is None
