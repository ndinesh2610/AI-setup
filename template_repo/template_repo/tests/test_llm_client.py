import json

import httpx
import pytest
from pydantic import SecretStr, ValidationError

from app.config import Settings
from app.services.llm_client import LLMClient


def test_llm_client_can_be_created() -> None:
    client = LLMClient()
    assert client is not None


def test_llm_client_sends_correct_request() -> None:
    def mock_response(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert str(request.url) == ("https://llm.example.test/v1/chat/completions")
        assert request.headers["Authorization"] == "Bearer test-key"

        payload = json.loads(request.content)
        assert payload["model"] == "test-model"
        assert payload["messages"] == [{"role": "user", "content": "Hello"}]

        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": "Hello from the model"}}]},
        )

    settings = Settings(
        llm_base_url="https://llm.example.test/v1",
        llm_model="test-model",
        llm_api_key=SecretStr("test-key"),
        llm_timeout_seconds=2.0,
    )

    transport = httpx.MockTransport(mock_response)
    client = LLMClient(settings=settings, transport=transport)

    result = client.complete("Hello")

    assert result == "Hello from the model"


def test_llm_client_raises_for_http_error() -> None:
    def mock_response(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"error": "Internal server error"})

    settings = Settings(
        llm_base_url="https://llm.example.test/v1",
        llm_model="test-model",
        llm_api_key=SecretStr("test-key"),
        llm_timeout_seconds=2.0,
    )

    transport = httpx.MockTransport(mock_response)
    client = LLMClient(settings=settings, transport=transport)

    with pytest.raises(httpx.HTTPStatusError):
        client.complete("Hello")

    client.close()


def test_llm_client_rejects_malformed_response() -> None:
    def mock_response(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"choices": []})

    settings = Settings(
        llm_base_url="https://llm.example.test/v1",
        llm_model="test-model",
        llm_api_key=SecretStr("test-key"),
        llm_timeout_seconds=2.0,
    )

    transport = httpx.MockTransport(mock_response)
    client = LLMClient(settings=settings, transport=transport)

    with pytest.raises(ValidationError):
        client.complete("Hello")

    client.close()
