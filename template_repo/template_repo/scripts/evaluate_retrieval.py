"""Evaluate retrieval recall@k against the golden question set."""

import json
import logging
from pathlib import Path

import psycopg

from app.config import get_settings
from app.security import AuthenticatedUser
from app.services.answering import get_embedder
from app.services.retrieval import retrieve_documents


def recall_at_k(results: list[list[int]], expected: list[list[int]], k: int) -> float:
    """Calculate micro-averaged recall at k."""
    relevant = 0
    retrieved = 0

    for actual_ids, expected_ids in zip(results, expected, strict=True):
        relevant += len(set(actual_ids[:k]) & set(expected_ids))
        retrieved += len(expected_ids)

    return relevant / retrieved if retrieved else 0.0


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logger = logging.getLogger(__name__)
    dataset_path = Path("data/golden_questions.json")
    questions = json.loads(dataset_path.read_text(encoding="utf-8"))
    settings = get_settings()
    user = AuthenticatedUser(tenant_id="company_a", roles=["employee"])

    results = []
    expected = []

    with psycopg.connect(
        host=settings.postgres_host,
        port=settings.postgres_port,
        dbname=settings.postgres_db,
        user=settings.postgres_user,
        password=settings.postgres_password.get_secret_value(),
        connect_timeout=5,
    ) as connection:
        embedder = get_embedder()

        for item in questions:
            documents = retrieve_documents(
                item["question"],
                user,
                connection=connection,
                embedder=embedder,
                limit=5,
            )
            results.append([doc.document_id for doc in documents])
            expected.append(item["expected_document_ids"])

    logger.info("Evaluated questions: %s", len(questions))
    for k in (1, 3, 5):
        score = recall_at_k(results, expected, k)
        logger.info("Recall@%s: %.2f%%", k, score * 100)


if __name__ == "__main__":
    main()
