# Day 17 — Spot-the-Flaw Security Review

## Snippet 1: Ticket Search

**Issue:** SQL injection through string interpolation.

**Risk:** An attacker could manipulate the SQL query and access
or modify unauthorized data.

**PR comment:** Use parameterized queries instead of inserting
user input directly into SQL. Also enforce access controls.

## Snippet 2: Invoice Retrieval

**Issue:** Broken object-level authorization (IDOR/BOLA).

**Risk:** An authenticated user could retrieve another user's
invoice by changing the invoice ID.

**PR comment:** Filter by invoice ID and authorized owner or
tenant ID. Return 404 when access is not permitted.

## Snippet 3: Passwords and Tokens

**Issues:**
- Hardcoded JWT signing secret.
- MD5 is unsuitable for password storage.
- JWT has no expiration.
- JWT subject should be represented as a string.

**PR comment:** Use Argon2id for password hashing, load the
JWT signing key from secure configuration, and include
expiration and appropriate token validation claims.

## Snippet 4: Sessions and Preferences

**Issues:**
- Unverified third-party package suggestion.
- Unsafe pickle deserialization.

**Risk:** A malicious package could compromise the application.
Untrusted pickle data can execute arbitrary code.

**PR comment:** Verify package existence, publisher, release
history, and provenance before installation. Replace pickle
with JSON and validate the parsed structure.

## Snippet 5: Error Handler

**Issues:**
- Logs plaintext passwords.
- Returns internal exception messages and stack traces.
- Responds with HTTP 200 for failures.

**PR comment:** Never log passwords or tokens. Log sanitized
diagnostic information server-side, return a generic error
message, and use an appropriate HTTP error status.

## Snippet 6: Preview and Download

**Issues:**
- Server-side request forgery (SSRF) from arbitrary URLs.
- No outbound request timeout.
- Path traversal through user-controlled filenames.
- No authentication or authorization checks.

**PR comment:** Use an approved destination allowlist,
block private and internal network destinations, validate
redirects, and set request timeouts. For downloads, use
server-generated file IDs, enforce ownership, and resolve
paths within a private storage directory.

## Review Status

Six snippets reviewed. Findings documented with risks
and recommended remediation.
