"""Build an LLM context without exceeding its token budget."""

from collections.abc import Callable, Sequence


def assemble_context(
    passages: Sequence[tuple[str, str]],
    token_budget: int,
    token_counter: Callable[[str], int],
) -> list[tuple[str, str]]:
    """Include complete passages while respecting the context-token budget."""
    if token_budget < 0:
        raise ValueError("token_budget cannot be negative")

    selected: list[tuple[str, str]] = []
    used_tokens = 0

    for source, passage in passages:
        passage_tokens = token_counter(passage)

        if passage_tokens < 0:
            raise ValueError("token_counter cannot return a negative value")

        if used_tokens + passage_tokens > token_budget:
            continue

        selected.append((source, passage))
        used_tokens += passage_tokens

    return selected
