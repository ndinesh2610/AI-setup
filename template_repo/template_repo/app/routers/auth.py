"""User registration endpoints."""

import logging

import psycopg
from fastapi import APIRouter, HTTPException, Request, Response, status
from psycopg.errors import UniqueViolation
from pydantic import BaseModel, EmailStr, Field

from app.config import get_settings
from app.services.password_security import hash_password
from app.services.session_security import (
    SESSION_COOKIE_NAME,
    SESSION_DURATION_SECONDS,
    generate_session_token,
    hash_session_token,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = logging.getLogger(__name__)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=15)


class RegisterResponse(BaseModel):
    message: str


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(data: RegisterRequest) -> RegisterResponse:
    """Register a user with the default reader role."""
    try:
        password_hash = hash_password(data.password)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    settings = get_settings()

    try:
        with (
            psycopg.connect(
                host=settings.postgres_host,
                port=settings.postgres_port,
                dbname=settings.postgres_db,
                user=settings.postgres_user,
                password=settings.postgres_password.get_secret_value(),
                connect_timeout=5,
            ) as conn,
            conn.cursor() as cur,
        ):
            cur.execute(
                """
                    INSERT INTO users (email, password_hash, role)
                    VALUES (%s, %s, 'reader')
                    """,
                (str(data.email).lower(), password_hash),
            )
            cur.execute(
                """
                    INSERT INTO auth_audit_events (event_type)
                    VALUES ('registration_success')
                    """
            )
    except UniqueViolation as exc:
        raise HTTPException(
            status_code=409,
            detail="Registration could not be completed.",
        ) from exc
    except psycopg.Error:
        logger.exception("Registration database error")
        raise HTTPException(
            status_code=503,
            detail="Registration temporarily unavailable.",
        ) from None

    return RegisterResponse(message="Registration successful")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    message: str


@router.post("/login", response_model=LoginResponse)
def login_user(data: LoginRequest, response: Response) -> LoginResponse:
    """Verify user credentials and record the login attempt."""
    from app.services.login_throttling import (
        clear_failed_attempts,
        is_login_blocked,
        record_failed_attempt,
    )
    from app.services.password_security import verify_password

    settings = get_settings()
    invalid_credentials = HTTPException(
        status_code=401,
        detail="Invalid email or password.",
    )

    try:
        with (
            psycopg.connect(
                host=settings.postgres_host,
                port=settings.postgres_port,
                dbname=settings.postgres_db,
                user=settings.postgres_user,
                password=settings.postgres_password.get_secret_value(),
                connect_timeout=5,
            ) as conn,
            conn.cursor() as cur,
        ):
            # Serialize attempts for the same email address.
            cur.execute(
                "SELECT pg_advisory_xact_lock(hashtextextended(LOWER(%s), 0))",
                (str(data.email),),
            )

            if is_login_blocked(cur, str(data.email)):
                raise HTTPException(
                    status_code=429,
                    detail="Too many failed login attempts. Try again later.",
                    headers={"Retry-After": "900"},
                )

            cur.execute(
                """
                    SELECT id, password_hash
                    FROM users
                    WHERE LOWER(email) = LOWER(%s)
                    """,
                (str(data.email),),
            )
            user = cur.fetchone()

            if user is None:
                record_failed_attempt(cur, str(data.email))
                cur.execute(
                    """
                        INSERT INTO auth_audit_events (event_type)
                        VALUES ('login_failed')
                        """
                )
                conn.commit()
                raise invalid_credentials

            user_id, stored_hash = user

            if not verify_password(stored_hash, data.password):
                record_failed_attempt(cur, str(data.email))
                cur.execute(
                    """
                        INSERT INTO auth_audit_events (user_id, event_type)
                        VALUES (%s, 'login_failed')
                        """,
                    (user_id,),
                )
                conn.commit()
                raise invalid_credentials

            clear_failed_attempts(cur, str(data.email))

            token = generate_session_token()

            cur.execute(
                """
                INSERT INTO user_sessions (
                    user_id, token_hash, expires_at
                )
                VALUES (
                    %s, %s,
                    NOW() + (%s * INTERVAL '1 second')
                )
                """,
                (user_id, hash_session_token(token), SESSION_DURATION_SECONDS),
            )

            cur.execute(
                """
                INSERT INTO auth_audit_events (user_id, event_type)
                VALUES (%s, 'login_success')
                """,
                (user_id,),
            )
    except HTTPException:
        raise
    except psycopg.Error:
        logger.exception("Login database error")
        raise HTTPException(
            status_code=503,
            detail="Login temporarily unavailable.",
        ) from None

    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        max_age=SESSION_DURATION_SECONDS,
        httponly=True,
        secure=settings.app_environment == "production",
        samesite="lax",
        path="/",
    )
    return LoginResponse(message="Login successful")


@router.get("/me")
def get_my_account(request: Request) -> dict[str, int]:
    """Return the user ID for an active browser session."""
    from app.services.session_security import get_session_user_id

    token = request.cookies.get(SESSION_COOKIE_NAME, "")

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Authentication required.",
        )

    try:
        user_id = get_session_user_id(token)
    except psycopg.Error:
        logger.exception("Session validation database error")
        raise HTTPException(
            status_code=503,
            detail="Authentication temporarily unavailable.",
        ) from None

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired session.",
        )

    return {"user_id": user_id}


@router.post("/logout")
def logout_user(request: Request, response: Response) -> dict[str, str]:
    """Revoke the current session and clear its cookie."""
    from app.services.csrf_security import verify_csrf_token
    from app.services.session_security import get_session_user_id, hash_session_token

    token = request.cookies.get(SESSION_COOKIE_NAME, "")
    csrf_token = request.headers.get("X-CSRF-Token", "")

    if not token:
        raise HTTPException(status_code=401, detail="Authentication required.")

    if not verify_csrf_token(token, csrf_token):
        raise HTTPException(status_code=403, detail="Invalid CSRF token.")

    try:
        user_id = get_session_user_id(token)
    except psycopg.Error:
        logger.exception("Logout session validation error")
        raise HTTPException(
            status_code=503,
            detail="Authentication temporarily unavailable.",
        ) from None

    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid or expired session.")

    if token:
        settings = get_settings()

        try:
            with (
                psycopg.connect(
                    host=settings.postgres_host,
                    port=settings.postgres_port,
                    dbname=settings.postgres_db,
                    user=settings.postgres_user,
                    password=settings.postgres_password.get_secret_value(),
                    connect_timeout=5,
                ) as conn,
                conn.cursor() as cur,
            ):
                cur.execute(
                    """
                    UPDATE user_sessions
                    SET revoked_at = NOW()
                    WHERE token_hash = %s
                      AND revoked_at IS NULL
                    RETURNING user_id
                    """,
                    (hash_session_token(token),),
                )
                result = cur.fetchone()

                if result:
                    cur.execute(
                        """
                        INSERT INTO auth_audit_events (user_id, event_type)
                        VALUES (%s, 'logout_success')
                        """,
                        (result[0],),
                    )
        except psycopg.Error:
            logger.exception("Logout database error")
            raise HTTPException(
                status_code=503,
                detail="Logout temporarily unavailable.",
            ) from None

    response.delete_cookie(
        key=SESSION_COOKIE_NAME,
        path="/",
        httponly=True,
        secure=get_settings().app_environment == "production",
        samesite="lax",
    )

    return {"message": "Logged out successfully"}


@router.get("/csrf-token")
def get_csrf_token(request: Request) -> dict[str, str]:
    """Provide a CSRF token for an authenticated browser session."""
    from app.services.csrf_security import generate_csrf_token
    from app.services.session_security import get_session_user_id

    session_token = request.cookies.get(SESSION_COOKIE_NAME, "")

    if not session_token:
        raise HTTPException(
            status_code=401,
            detail="Authentication required.",
        )

    try:
        user_id = get_session_user_id(session_token)
    except psycopg.Error:
        logger.exception("CSRF session validation database error")
        raise HTTPException(
            status_code=503,
            detail="Authentication temporarily unavailable.",
        ) from None

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired session.",
        )

    return {"csrf_token": generate_csrf_token(session_token)}
