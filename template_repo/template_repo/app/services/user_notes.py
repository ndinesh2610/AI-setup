"""Database operations for user-owned notes."""

from typing import Any


def get_owned_note(
    note_id: int,
    user_id: int,
    *,
    connection: Any,
) -> dict[str, object] | None:
    """Return a note only when its owner matches the user."""
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, content
            FROM user_notes
            WHERE id = %s
              AND owner_user_id = %s
            """,
            (note_id, user_id),
        )
        row = cursor.fetchone()

    if row is None:
        return None

    return {"id": row[0], "content": row[1]}
