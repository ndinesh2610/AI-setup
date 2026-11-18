"""Knowledge Assistant web interface."""

import secrets
from pathlib import Path

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from jinja2 import select_autoescape

from app.security import AuthenticatedUser, get_current_user
from app.services import answering

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[1] / "templates"))
templates.env.autoescape = select_autoescape(["html", "xml"])


@router.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    """Render the question form."""
    token = secrets.token_urlsafe(32)
    response = templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"csrf_token": token},
    )
    response.set_cookie(
        "csrf_token",
        token,
        httponly=True,
        samesite="strict",
        secure=request.url.scheme == "https",
    )
    response.headers["Cache-Control"] = "no-store"
    return response


@router.post("/ui/ask", response_class=HTMLResponse)
def ask_ui(
    request: Request,
    question: str = Form(...),
    csrf_token: str = Form(...),
    user: AuthenticatedUser = Depends(get_current_user),  # noqa: B008
) -> HTMLResponse:
    """Validate the form and render an answer fragment."""
    cookie = request.cookies.get("csrf_token", "")

    if not cookie or not secrets.compare_digest(cookie, csrf_token):
        return templates.TemplateResponse(
            request=request,
            name="answer.html",
            context={"error": "Refresh the page and try again."},
            status_code=403,
        )

    question = question.strip()
    if not question or len(question) > 2000:
        return templates.TemplateResponse(
            request=request,
            name="answer.html",
            context={"error": "Enter a question of 1 to 2000 characters."},
            status_code=400,
        )

    result = answering.answer_question(question, user)

    response = templates.TemplateResponse(
        request=request,
        name="answer.html",
        context={
            "answer": result.answer,
            "citations": result.citations,
        },
    )
    response.headers["Cache-Control"] = "no-store"
    return response
