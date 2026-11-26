"""Secure session token generation and hashing."""

import hashlib
import secrets

SESSION_COOKIE_NAME = "fde_session"
SESSION_DURATION_SECONDS = 3600


def generate_session_token() -> str:
    """Generate a cryptographically secure session token."""
    return secrets.token_urlsafe(32)


def hash_session_token(token: str) -> str:
    """Hash the session token before database storage."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def get_session_user_id(token: str) -> int | None:
    """Return the user ID for a valid, active session."""
    import psycopg

    from app.config import get_settings

    if not token:
        return None

    settings = get_settings()

    with (
        psycopg.connect(
            host=settings.postgres_host,
            port=settings.postgres_port,
            dbname=settings.postgres_db,
            user=settings.postgres_user,
            password=settings.postgres_password.get_secret_value(),
            connect_timeout=5,
        ) as conn,
        conn.cursor() as cur,
    ):
        cur.execute(
            """
            SELECT user_id
            FROM user_sessions
            WHERE token_hash = %s
              AND revoked_at IS NULL
              AND expires_at > NOW()
            """,
            (hash_session_token(token),),
        )
        result = cur.fetchone()

    return int(result[0]) if result else None
