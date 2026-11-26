"""Password validation and Argon2id hashing."""

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

_hasher = PasswordHasher()

# Starter blocklist; expand with a maintained compromised-password list.
_BLOCKED_PASSWORDS = {
    "password123456789",
    "123456789012345",
    "qwerty123456789",
}


def validate_password(password: str) -> None:
    """Apply minimum length and common-password checks."""
    if len(password) < 15:
        raise ValueError("Password must contain at least 15 characters.")

    if password.casefold() in _BLOCKED_PASSWORDS:
        raise ValueError("Choose a less common password.")


def hash_password(password: str) -> str:
    """Validate and hash a password using Argon2id."""
    validate_password(password)
    return _hasher.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    """Verify a password without exposing the stored hash."""
    try:
        return _hasher.verify(password_hash, password)
    except VerifyMismatchError:
        return False
