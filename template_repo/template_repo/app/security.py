"""JWT authentication for protected API endpoints."""

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from app.config import get_settings


class AuthenticatedUser(BaseModel):
    tenant_id: str
    roles: list[str]


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),  # noqa: B008
) -> AuthenticatedUser:
    """Validate a signed JWT and return the authenticated user."""
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired access token.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise unauthorized

    settings = get_settings()

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret_key.get_secret_value(),
            algorithms=["HS256"],
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience,
            options={"require": ["exp", "iat", "iss", "aud", "sub"]},
            leeway=0,
        )
    except jwt.InvalidTokenError as exc:
        raise unauthorized from exc

    tenant_id = payload.get("tenant_id")
    roles = payload.get("roles")
    subject = payload.get("sub")

    if (
        not isinstance(subject, str)
        or not subject.strip()
        or not isinstance(tenant_id, str)
        or not tenant_id.strip()
        or not isinstance(roles, list)
        or not all(isinstance(role, str) and role for role in roles)
    ):
        raise unauthorized

    from app.rbac import require_roles

    user = AuthenticatedUser(tenant_id=tenant_id, roles=roles)

    try:
        require_roles(user, ["n8n-agent"])
    except HTTPException:
        raise unauthorized from None

    return user
