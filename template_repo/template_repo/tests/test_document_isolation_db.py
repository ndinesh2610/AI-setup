"""Integration tests for document tenant and role isolation."""

import psycopg
import pytest

from app.config import get_settings
from app.security import AuthenticatedUser
from app.services.source_passages import get_source_passage


@pytest.mark.parametrize(
    ("tenant", "roles", "expected_access"),
    [
        ("company_a", ["employee"], True),
        ("company_b", ["employee"], False),
        ("company_a", ["reader"], False),
    ],
)
def test_document_access_isolation(tenant, roles, expected_access):
    settings = get_settings()

    with psycopg.connect(
        host=settings.postgres_host,
        port=settings.postgres_port,
        dbname=settings.postgres_db,
        user=settings.postgres_user,
        password=settings.postgres_password.get_secret_value(),
        connect_timeout=5,
    ) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id FROM documents
                WHERE tenant_id = %s
                  AND allowed_roles && %s::text[]
                LIMIT 1
                """,
                ("company_a", ["employee"]),
            )
            row = cur.fetchone()

        assert row is not None, "Company A test document is missing"

        user = AuthenticatedUser(tenant_id=tenant, roles=roles)
        result = get_source_passage(row[0], user, connection=conn)

        assert (result is not None) == expected_access
