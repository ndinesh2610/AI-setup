"""Retrieve documents restricted to the authenticated user's permissions."""

from dataclasses import dataclass
from typing import Any, Protocol

from app.security import AuthenticatedUser


class Embedder(Protocol):
    """Interface for converting a question into an embedding."""

    def encode(self, question: str) -> Any:
        """Return the question embedding."""


@dataclass
class RetrievedDocument:
    """A document returned by permission-filtered vector search."""

    document_id: int
    passage: str
    source: str
    distance: float


def retrieve_documents(
    question: str,
    user: AuthenticatedUser,
    *,
    connection: Any,
    embedder: Embedder,
    limit: int = 5,
) -> list[RetrievedDocument]:
    """Retrieve nearest documents belonging to the user's tenant and roles."""
    if limit < 1:
        raise ValueError("limit must be greater than zero")

    embedding = embedder.encode(question)
    if hasattr(embedding, "tolist"):
        embedding = embedding.tolist()

    vector_text = "[" + ",".join(str(value) for value in embedding) + "]"

    query = """
        WITH authorized_docs AS MATERIALIZED (
            SELECT id, content, source, embedding
            FROM documents
            WHERE tenant_id = %s
              AND allowed_roles && %s::text[]
        )
        SELECT
            id,
            content,
            source,
            embedding <=> %s::vector AS distance
        FROM authorized_docs
        ORDER BY distance
        LIMIT %s
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (user.tenant_id, user.roles, vector_text, limit),
        )
        rows = cursor.fetchall()

    return [
        RetrievedDocument(
            document_id=row[0],
            passage=row[1],
            source=row[2],
            distance=float(row[3]),
        )
        for row in rows
    ]
