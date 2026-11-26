"""Tests for user-owned note access."""

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.services.user_notes import get_owned_note


class FakeCursor:
    def __init__(self, row):
        self.row = row
        self.params = None
        self.query = ""

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


def test_owner_can_read_note():
    connection = FakeConnection((7, "Private note"))

    result = get_owned_note(7, 1, connection=connection)

    assert result == {"id": 7, "content": "Private note"}
    assert connection.fake_cursor.params == (7, 1)
    assert "owner_user_id = %s" in connection.fake_cursor.query


def test_other_user_cannot_read_note():
    connection = FakeConnection(None)

    result = get_owned_note(7, 2, connection=connection)

    assert result is None
    assert connection.fake_cursor.params == (7, 2)


def test_anonymous_user_is_rejected():
    with patch("app.routers.user_notes.get_session_user_id") as session_lookup:
        response = TestClient(app).get("/notes/7")

    assert response.status_code == 401
    session_lookup.assert_not_called()
