"""Generate answers grounded in permission-filtered documents."""

from functools import lru_cache
from pathlib import Path

import psycopg
import tiktoken
from sentence_transformers import SentenceTransformer

from app.config import get_settings
from app.models.schemas import AskResponse, Citation
from app.security import AuthenticatedUser
from app.services.context import assemble_context
from app.services.llm_client import LLMClient
from app.services.retrieval import retrieve_documents

PROMPT_PATH = Path(__file__).resolve().parents[2] / "prompts" / "ask.txt"


@lru_cache
def get_embedder() -> SentenceTransformer:
    """Load the embedding model once."""
    return SentenceTransformer("all-MiniLM-L6-v2")


def count_tokens(text: str) -> int:
    """Count tokens using the cl100k_base tokenizer."""
    return len(tiktoken.get_encoding("cl100k_base").encode(text))


def answer_question(
    question: str,
    user: AuthenticatedUser,
) -> AskResponse:
    """Retrieve authorized context and generate a grounded answer."""
    settings = get_settings()

    with psycopg.connect(
        host=settings.postgres_host,
        port=settings.postgres_port,
        dbname=settings.postgres_db,
        user=settings.postgres_user,
        password=settings.postgres_password.get_secret_value(),
        connect_timeout=5,
    ) as connection:
        documents = retrieve_documents(
            question,
            user,
            connection=connection,
            embedder=get_embedder(),
        )

    if not documents:
        return AskResponse(
            answer="I don't know based on the available sources.",
            citations=[],
        )

    passages = [(doc.source, doc.passage) for doc in documents]
    selected = assemble_context(
        passages,
        token_budget=settings.context_token_budget,
        token_counter=count_tokens,
    )

    if not selected:
        return AskResponse(
            answer="I don't know based on the available sources.",
            citations=[],
        )

    context = "\n\n".join(f"Source: {source}\nPassage: {passage}" for source, passage in selected)

    prompt_template = PROMPT_PATH.read_text(encoding="utf-8")
    prompt = prompt_template.format(question=question, context=context)

    client = LLMClient(settings)
    try:
        answer = client.complete(prompt)
    finally:
        client.close()

    citations = [Citation(source=source, passage=passage) for source, passage in selected]

    return AskResponse(answer=answer, citations=citations)
