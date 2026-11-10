"""Tests for the grounded answering service."""

from types import SimpleNamespace

from pydantic import SecretStr

from app.models.schemas import Citation
from app.security import AuthenticatedUser
from app.services import answering
from app.services.retrieval import RetrievedDocument


class FakeConnection:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class FakeLLM:
    def __init__(self, settings):
        self.closed = False
        self.prompt = ""

    def complete(self, prompt):
        self.prompt = prompt
        return "The policy allows five days. [company_policies]"

    def close(self):
        self.closed = True


def setup_dependencies(monkeypatch, documents):
    settings = SimpleNamespace(
        postgres_host="localhost",
        postgres_port=5432,
        postgres_db="test_db",
        postgres_user="test_user",
        postgres_password=SecretStr("test_password"),
        context_token_budget=2000,
    )

    monkeypatch.setattr(answering, "get_settings", lambda: settings)
    monkeypatch.setattr(answering.psycopg, "connect", lambda **kwargs: FakeConnection())
    monkeypatch.setattr(answering, "get_embedder", lambda: object())
    monkeypatch.setattr(
        answering,
        "retrieve_documents",
        lambda *args, **kwargs: documents,
    )
    monkeypatch.setattr(answering, "count_tokens", lambda text: len(text.split()))

    clients = []

    def fake_llm_client(settings):
        client = FakeLLM(settings)
        clients.append(client)
        return client

    monkeypatch.setattr(answering, "LLMClient", fake_llm_client)
    return clients


def test_answer_question_returns_grounded_answer_and_citation(monkeypatch):
    documents = [
        RetrievedDocument(
            document_id=1,
            passage="Employees may take five days of leave.",
            source="company_policies",
            distance=0.1,
        )
    ]
    clients = setup_dependencies(monkeypatch, documents)
    user = AuthenticatedUser(tenant_id="company_a", roles=["employee"])

    result = answering.answer_question("How many leave days?", user)

    assert result.answer.startswith("The policy allows five days")
    assert result.citations == [
        Citation(
            source="company_policies",
            passage="Employees may take five days of leave.",
        )
    ]
    assert "How many leave days?" in clients[0].prompt
    assert "Employees may take five days of leave." in clients[0].prompt
    assert clients[0].closed is True


def test_answer_question_without_documents_returns_safe_fallback(monkeypatch):
    clients = setup_dependencies(monkeypatch, [])
    user = AuthenticatedUser(tenant_id="company_a", roles=["employee"])

    result = answering.answer_question("What is the loan limit?", user)

    assert result.answer == "I don't know based on the available sources."
    assert result.citations == []
    assert clients == []
