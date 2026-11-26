"""API for accessing user-owned notes."""

import psycopg
from fastapi import APIRouter, HTTPException, Request

from app.config import get_settings
from app.services.session_security import (
    SESSION_COOKIE_NAME,
    get_session_user_id,
)
from app.services.user_notes import get_owned_note

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("/{note_id}")
def read_note(note_id: int, request: Request) -> dict[str, object]:
    """Return a note only to its authenticated owner."""
    token = request.cookies.get(SESSION_COOKIE_NAME, "")

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Authentication required.",
        )

    try:
        user_id = get_session_user_id(token)

        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired session.",
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
            note = get_owned_note(
                note_id,
                user_id,
                connection=connection,
            )

    except psycopg.Error:
        raise HTTPException(
            status_code=503,
            detail="Database temporarily unavailable.",
        ) from None

    if note is None:
        raise HTTPException(
            status_code=404,
            detail="Note not found.",
        )

    return note
