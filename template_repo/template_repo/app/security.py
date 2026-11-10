"""Authentication boundary for protected API endpoints."""

from fastapi import HTTPException, status
from pydantic import BaseModel


class AuthenticatedUser(BaseModel):
    """Identity information obtained only from a validated access token."""

    tenant_id: str
    roles: list[str]


def get_current_user() -> AuthenticatedUser:
    """Reject requests until production JWT validation is configured."""
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication is not configured.",
        headers={"WWW-Authenticate": "Bearer"},
    )
