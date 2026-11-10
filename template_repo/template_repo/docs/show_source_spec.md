# Show Source Passage — Feature Specification

## Goal
Allow an authenticated user to view the exact original passage behind a retrieved citation.

## API
GET /sources/{document_id}

## Authorization
- Require an authenticated user.
- Return a passage only when the document belongs to the user's tenant.
- Require at least one matching role in allowed_roles.
- Apply authorization in the SQL query before returning document content.
- Return 404 when the document is missing or inaccessible.
- Never accept tenant ID or roles from request parameters.

## Response
- document_id
- source
- passage

## Error behavior
- 401 when authentication is not configured or missing.
- 404 when the document is missing or unauthorized.
- Do not expose database details or internal errors.

## Tests
- Authorized user receives the exact passage.
- Different tenant receives 404.
- User without a matching role receives 404.
- Missing document receives 404.
- Unauthenticated request receives 401.

## Out of scope
- Editing source documents.
- Returning documents from other tenants.
- Public or anonymous access.
