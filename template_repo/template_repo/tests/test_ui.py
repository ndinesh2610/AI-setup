from fastapi.testclient import TestClient

from app.main import create_app
from app.models.schemas import AskResponse, Citation
from app.security import AuthenticatedUser, get_current_user
from app.services import answering


def make_client() -> TestClient:
    app = create_app()
    app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(
        tenant_id="test-tenant",
        roles=["reader"],
    )
    return TestClient(app)


def test_ui_page():
    client = make_client()
    response = client.get("/")
    assert response.status_code == 200
    assert "Knowledge Assistant" in response.text
    assert "csrf_token" in response.cookies
    assert 'for="question"' in response.text


def test_csp_header():
    client = make_client()
    response = client.get("/")
    csp = response.headers["Content-Security-Policy"]
    assert "script-src 'self'" in csp
    assert "object-src 'none'" in csp
    assert "frame-ancestors 'none'" in csp


def test_invalid_csrf():
    client = make_client()
    client.get("/")
    response = client.post(
        "/ui/ask",
        data={"question": "Test question", "csrf_token": "invalid"},
    )
    assert response.status_code == 403


def test_empty_question():
    client = make_client()
    client.get("/")
    response = client.post(
        "/ui/ask",
        data={
            "question": " ",
            "csrf_token": client.cookies["csrf_token"],
        },
    )
    assert response.status_code == 400


def test_answer_and_script_escaping(monkeypatch):
    client = make_client()
    client.get("/")

    def fake_answer(question, user):
        return AskResponse(
            answer="Test answer",
            citations=[
                Citation(
                    source="test.txt",
                    passage="<script>alert('XSS')</script>",
                )
            ],
        )

    monkeypatch.setattr(answering, "answer_question", fake_answer)

    response = client.post(
        "/ui/ask",
        data={
            "question": "Test question",
            "csrf_token": client.cookies["csrf_token"],
        },
        headers={"HX-Request": "true"},
    )

    assert response.status_code == 200
    assert "Test answer" in response.text
    assert "test.txt" in response.text
    assert "<script>" not in response.text
    assert "&lt;script&gt;" in response.text


def test_unauthenticated_request():
    client = TestClient(create_app())
    client.get("/")
    response = client.post(
        "/ui/ask",
        data={
            "question": "Test question",
            "csrf_token": client.cookies["csrf_token"],
        },
    )
    assert response.status_code == 401
