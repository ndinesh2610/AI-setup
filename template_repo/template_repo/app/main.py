"""Application entry point: builds the FastAPI app.

Reading order for a new engineer:  main.py -> routers/ -> services/ -> models/.
Routers are thin (they only translate HTTP), services hold the logic, models describe data
(Playbook ARC-01).
"""

import logging
import uuid
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.logging_config import request_id_var, setup_logging
from app.request_size_limit import RequestSizeLimitMiddleware
from app.routers import ask, auth, health, sources, ui, uploads, user_notes

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Build the app. A function (not a global) makes it easy to test."""
    settings = get_settings()
    setup_logging()

    app = FastAPI(
        title="FDE service",
        # Interactive docs are handy in development and off elsewhere (ARC-09).
        docs_url="/docs" if settings.docs_enabled else None,
        redoc_url=None,
        openapi_url="/openapi.json" if settings.docs_enabled else None,
        root_path=settings.app_base_path,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["Content-Type", "Authorization", "X-CSRF-Token"],
    )

    app.add_middleware(
        RequestSizeLimitMiddleware,
        max_bytes=settings.max_request_bytes,
    )

    @app.middleware("http")
    async def add_request_id(request: Request, call_next):
        """Give every request an ID, log with it, and return it to the caller (LOG-03)."""
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        token = request_id_var.set(request_id)
        try:
            response = await call_next(request)
        finally:
            request_id_var.reset(token)
        response.headers["X-Request-ID"] = request_id
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; "
            "style-src 'self'; object-src 'none'; "
            "frame-ancestors 'none'; base-uri 'none'; "
            "form-action 'self'"
        )
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response

    @app.exception_handler(Exception)
    async def unhandled_error(request: Request, exc: Exception) -> JSONResponse:
        """One error format and no internals in the response (ARC-03, SEC-13)."""
        logger.error("unhandled error", exc_info=exc)
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "internal_error",
                    "message": "Something went wrong.",
                    "request_id": request_id_var.get(),
                }
            },
        )

    app.mount(
        "/static",
        StaticFiles(directory=Path(__file__).resolve().parent / "static"),
        name="static",
    )
    app.include_router(ui.router)
    app.include_router(health.router)
    app.include_router(ask.router)
    app.include_router(auth.router)
    app.include_router(sources.router)
    app.include_router(user_notes.router)
    app.include_router(uploads.router)
    return app


app = create_app()
