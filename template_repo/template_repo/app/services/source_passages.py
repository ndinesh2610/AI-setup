"""Retrieve an exact source passage after checking document permissions."""

from dataclasses import dataclass
from typing import Any

from app.security import AuthenticatedUser


@dataclass
class SourcePassage:
    """A source passage the authenticated user is authorized to access."""

    document_id: int
    source: str
    passage: str


def get_source_passage(
    document_id: int,
    user: AuthenticatedUser,
    *,
    connection: Any,
) -> SourcePassage | None:
    """Return a passage only when tenant and role permissions match."""
    query = """
        SELECT id, source, content
        FROM documents
        WHERE id = %s
          AND tenant_id = %s
          AND allowed_roles && %s::text[]
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (document_id, user.tenant_id, user.roles),
        )
        row = cursor.fetchone()

    if row is None:
        return None

    return SourcePassage(
        document_id=row[0],
        source=row[1],
        passage=row[2],
    )
