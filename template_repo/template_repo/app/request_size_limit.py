"""ASGI middleware enforcing an HTTP request-body size limit."""

from collections.abc import Callable
from typing import Any

from starlette.datastructures import Headers
from starlette.responses import JSONResponse


class RequestSizeLimitMiddleware:
    def __init__(self, app: Callable[..., Any], max_bytes: int) -> None:
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(
        self,
        scope: dict[str, Any],
        receive: Callable[..., Any],
        send: Callable[..., Any],
    ) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        await self.handle_http(scope, receive, send)

    async def handle_http(
        self,
        scope: dict[str, Any],
        receive: Callable[..., Any],
        send: Callable[..., Any],
    ) -> None:
        """Validate and enforce HTTP request-body limits."""
        status = self.check_content_length(scope)
        if status is not None:
            await self.respond(scope, receive, send, status)
            return

        limited_receive = self.limit_receive(receive)
        started = False
        pending_start = None

        async def limited_send(message: dict[str, Any]) -> None:
            nonlocal started, pending_start

            if message["type"] == "http.response.start":
                pending_start = message
                return

            if pending_start is not None:
                await send(pending_start)
                pending_start = None
                started = True

            await send(message)

        try:
            await self.app(scope, limited_receive, limited_send)
            if pending_start is not None:
                await send(pending_start)
        except RequestTooLargeError:
            if started:
                raise
            await self.respond(scope, receive, send, 413)

    def limit_receive(
        self,
        receive: Callable[..., Any],
    ) -> Callable[..., Any]:
        """Count streamed request bytes and enforce the limit."""
        total = 0

        async def limited_receive() -> dict[str, Any]:
            nonlocal total
            message = await receive()

            if message["type"] == "http.request":
                total += len(message.get("body", b""))
                if total > self.max_bytes:
                    raise RequestTooLargeError

            return message

        return limited_receive

    def check_content_length(self, scope: dict[str, Any]) -> int | None:
        """Validate the declared request-body length."""
        length = Headers(scope=scope).get("content-length")
        if length is None:
            return None

        try:
            declared_size = int(length)
        except ValueError:
            return 400

        if declared_size < 0:
            return 400
        if declared_size > self.max_bytes:
            return 413
        return None

    @staticmethod
    async def respond(
        scope: dict[str, Any],
        receive: Callable[..., Any],
        send: Callable[..., Any],
        status: int,
    ) -> None:
        response = JSONResponse(
            {"detail": ("Request body too large" if status == 413 else "Invalid Content-Length")},
            status_code=status,
        )
        await response(scope, receive, send)


class RequestTooLargeError(Exception):
    """Request body exceeded the configured limit."""
