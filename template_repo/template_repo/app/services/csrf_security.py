"""CSRF token generation and validation for browser sessions."""

import hashlib
import hmac
import secrets


def generate_csrf_token(session_token: str) -> str:
    """Generate a token cryptographically bound to a session."""
    nonce = secrets.token_hex(16)
    signature = hmac.new(
        session_token.encode(),
        nonce.encode(),
        hashlib.sha256,
    ).hexdigest()
    return f"{nonce}.{signature}"


def verify_csrf_token(session_token: str, csrf_token: str) -> bool:
    """Verify a session-bound CSRF token."""
    try:
        nonce, signature = csrf_token.split(".")
        if len(nonce) != 32 or len(signature) != 64:
            return False
        bytes.fromhex(nonce)
        bytes.fromhex(signature)
    except ValueError:
        return False

    expected = hmac.new(
        session_token.encode(),
        nonce.encode(),
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected, signature)
