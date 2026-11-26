"""Authenticated, size-limited PDF uploads."""

import secrets
from pathlib import Path
from typing import Annotated

import psycopg
from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from starlette.concurrency import run_in_threadpool

from app.services.csrf_security import verify_csrf_token
from app.services.session_security import (
    SESSION_COOKIE_NAME,
    get_session_user_id,
)

router = APIRouter(prefix="/uploads", tags=["uploads"])

MAX_FILE_BYTES = 2 * 1024 * 1024
UPLOAD_DIR = Path("data/private_uploads")


@router.post("")
async def upload_pdf(
    request: Request,
    file: Annotated[UploadFile, File()],
) -> dict[str, str]:
    """Save an authenticated PDF with a server-generated filename."""
    token = request.cookies.get(SESSION_COOKIE_NAME, "")
    if not token:
        raise HTTPException(401, "Authentication required.")

    csrf_token = request.headers.get("X-CSRF-Token", "")
    if not verify_csrf_token(token, csrf_token):
        raise HTTPException(403, "Invalid CSRF token.")

    try:
        user_id = get_session_user_id(token)
    except psycopg.Error:
        raise HTTPException(503, "Session service unavailable.") from None

    if user_id is None:
        raise HTTPException(401, "Invalid or expired session.")

    if file.content_type != "application/pdf":
        raise HTTPException(415, "Only PDF uploads are allowed.")

    content = await file.read(MAX_FILE_BYTES + 1)

    if len(content) > MAX_FILE_BYTES:
        raise HTTPException(413, "File exceeds 2 MB.")

    if not content.startswith(b"%PDF-"):
        raise HTTPException(415, "Invalid PDF file content.")

    filename = await run_in_threadpool(save_pdf, content)

    return {"message": "Upload successful", "file_id": filename}


def save_pdf(content: bytes) -> str:
    """Store a PDF outside the public directory."""
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True, mode=0o700)

    filename = f"{secrets.token_hex(16)}.pdf"
    destination = UPLOAD_DIR / filename

    with destination.open("xb") as output:
        output.write(content)

    destination.chmod(0o600)
    return filename
