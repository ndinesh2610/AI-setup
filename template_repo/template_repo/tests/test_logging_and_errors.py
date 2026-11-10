import json
import logging

from fastapi.testclient import TestClient

from app.logging_config import JsonFormatter, request_id_var
from app.main import app


def test_json_formatter_includes_request_id():
    token = request_id_var.set("test-123")
    try:
        record = logging.LogRecord("test", logging.INFO, "", 0, "test message", (), None)
        result = json.loads(JsonFormatter().format(record))
        assert result["message"] == "test message"
        assert result["request_id"] == "test-123"
    finally:
        request_id_var.reset(token)


def test_unhandled_error_does_not_expose_details():
    test_app = app

    @test_app.get("/test-error")
    def trigger_error():
        raise RuntimeError("secret internal detail")

    client = TestClient(test_app, raise_server_exceptions=False)
    response = client.get("/test-error")

    assert response.status_code == 500
    assert "secret internal detail" not in response.text
    assert response.json()["error"]["code"] == "internal_error"
