"""Database-backed login attempt throttling."""

import psycopg

MAX_FAILED_ATTEMPTS = 5
WINDOW_MINUTES = 15


def is_login_blocked(
    cur: psycopg.Cursor,
    email: str,
) -> bool:
    """Check recent failed attempts for an email address."""
    cur.execute(
        """
        SELECT COUNT(*)
        FROM login_attempts
        WHERE LOWER(email) = LOWER(%s)
          AND attempted_at > NOW() - INTERVAL '15 minutes'
        """,
        (email,),
    )
    result = cur.fetchone()
    return bool(result and result[0] >= MAX_FAILED_ATTEMPTS)


def record_failed_attempt(
    cur: psycopg.Cursor,
    email: str,
) -> None:
    """Record an unsuccessful login attempt."""
    cur.execute(
        """
        INSERT INTO login_attempts (email)
        VALUES (%s)
        """,
        (email,),
    )


def clear_failed_attempts(
    cur: psycopg.Cursor,
    email: str,
) -> None:
    """Clear failed attempts following successful login."""
    cur.execute(
        """
        DELETE FROM login_attempts
        WHERE LOWER(email) = LOWER(%s)
        """,
        (email,),
    )
