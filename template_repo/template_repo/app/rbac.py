"""Centralized role-based authorization."""

from collections.abc import Iterable

from fastapi import HTTPException, status

from app.security import AuthenticatedUser


def require_roles(
    user: AuthenticatedUser,
    allowed_roles: Iterable[str],
) -> None:
    """Reject users without an explicitly permitted role."""
    if not set(user.roles).intersection(allowed_roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions.",
        )
