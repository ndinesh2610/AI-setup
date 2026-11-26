"""Tests for Day 16 password security."""

import pytest

from app.services.password_security import (
    hash_password,
    validate_password,
    verify_password,
)


def test_correct_password():
    password = "MySecurePassphrase2026"  # noqa: S105 - Test-only password
    hashed = hash_password(password)
    assert hashed.startswith("$argon2id$")
    assert verify_password(hashed, password)


def test_wrong_password():
    hashed = hash_password("MySecurePassphrase2026")
    assert not verify_password(hashed, "WrongPassword2026")


def test_short_password_rejected():
    with pytest.raises(ValueError, match="at least 15 characters"):
        validate_password("shortpassword")


def test_common_password_rejected():
    with pytest.raises(ValueError, match="less common password"):
        validate_password("password123456789")


def test_long_password_accepted():
    validate_password("a" * 64)


def test_no_special_character_requirement():
    validate_password("thisisalongpassphrase")
