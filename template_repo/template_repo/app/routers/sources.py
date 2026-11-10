"""API endpoint for viewing authorized source passages."""

import psycopg
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.config import get_settings
from app.security import AuthenticatedUser, get_current_user
from app.services.source_passages import get_source_passage

router = APIRouter()


class SourcePassageResponse(BaseModel):
    document_id: int
    source: str
    passage: str


@router.get(
    "/sources/{document_id}",
    response_model=SourcePassageResponse,
)
def show_source(
    document_id: int,
    user: AuthenticatedUser = Depends(get_current_user),  # noqa: B008
) -> SourcePassageResponse:
    """Return the exact passage if the user is authorized to access it."""
    if document_id < 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source passage not found.",
        )

    settings = get_settings()

    with psycopg.connect(
        host=settings.postgres_host,
        port=settings.postgres_port,
        dbname=settings.postgres_db,
        user=settings.postgres_user,
        password=settings.postgres_password.get_secret_value(),
        connect_timeout=5,
    ) as connection:
        result = get_source_passage(
            document_id,
            user,
            connection=connection,
        )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source passage not found.",
        )

    return SourcePassageResponse(
        document_id=result.document_id,
        source=result.source,
        passage=result.passage,
    )
