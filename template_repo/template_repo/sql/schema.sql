-- Variant 3: Parcel logistics schema
-- Source CSVs: data/variant_3_parcels/tables/

CREATE TABLE IF NOT EXISTS parcels (
    id         INTEGER PRIMARY KEY,
    name       TEXT NOT NULL,
    status     TEXT NOT NULL,
    category   TEXT NOT NULL,
    created_at DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS hubs (
    id        INTEGER PRIMARY KEY,
    parent_id INTEGER NOT NULL REFERENCES parcels(id),
    label     TEXT NOT NULL,
    amount    NUMERIC(10, 2) NOT NULL
);

CREATE TABLE IF NOT EXISTS scan_events (
    id          INTEGER PRIMARY KEY,
    parent_id   INTEGER NOT NULL REFERENCES hubs(id),
    event       TEXT NOT NULL,
    happened_at DATE NOT NULL
);

-- Indexes support joins through the parent relationships.
CREATE INDEX IF NOT EXISTS idx_hubs_parent_id
    ON hubs(parent_id);

CREATE INDEX IF NOT EXISTS idx_scan_events_parent_id
    ON scan_events(parent_id);

-- Day 16: Authentication and session management

CREATE TABLE IF NOT EXISTS users (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'reader'
        CHECK (role IN ('reader', 'admin')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email
    ON users (LOWER(email));

CREATE TABLE IF NOT EXISTS user_sessions (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash TEXT NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    revoked_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id
    ON user_sessions(user_id);

CREATE TABLE IF NOT EXISTS auth_audit_events (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    event_type TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Day 16: Track failed login attempts for throttling.
CREATE TABLE IF NOT EXISTS login_attempts (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email TEXT NOT NULL,
    attempted_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_login_attempts_email_time
ON login_attempts (LOWER(email), attempted_at);

-- Day 16: User-owned records for object-level authorization.
CREATE TABLE IF NOT EXISTS user_notes (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    owner_user_id BIGINT NOT NULL
        REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_notes_owner
    ON user_notes(owner_user_id);
