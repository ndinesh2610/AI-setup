"""The /ask endpoint for the grounded assistant."""

from fastapi import APIRouter, Depends

from app.models.schemas import AskRequest, AskResponse
from app.security import AuthenticatedUser, get_current_user
from app.services import answering

router = APIRouter()


@router.post("/ask", response_model=AskResponse)
def ask(
    body: AskRequest,
    user: AuthenticatedUser = Depends(get_current_user),  # noqa: B008
) -> AskResponse:
    """Answer a question using documents the authenticated user can access."""
    return answering.answer_question(body.question, user)
