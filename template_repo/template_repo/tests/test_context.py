"""Tests for assembling retrieved passages within a context budget."""

import pytest

from app.services.context import assemble_context


def word_count(text: str) -> int:
    return len(text.split())


def test_assemble_context_includes_passages_within_budget():
    passages = [
        ("policy.txt", "Employees receive 20 days leave"),
        ("remote.txt", "Employees can work remotely"),
    ]

    result = assemble_context(passages, token_budget=10, token_counter=word_count)

    assert result == passages


def test_assemble_context_excludes_passage_that_exceeds_budget():
    passages = [
        ("policy.txt", "Employees receive 20 days leave"),
        ("remote.txt", "Employees can work remotely"),
    ]

    result = assemble_context(passages, token_budget=5, token_counter=word_count)

    assert result == [passages[0]]


def test_assemble_context_returns_empty_for_zero_budget():
    passages = [("policy.txt", "Employees receive 20 days leave")]

    result = assemble_context(passages, token_budget=0, token_counter=word_count)

    assert result == []


def test_assemble_context_rejects_negative_budget():
    with pytest.raises(ValueError, match="token_budget"):
        assemble_context([], token_budget=-1, token_counter=word_count)
