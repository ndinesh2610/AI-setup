# Show Source — Implementation Plan

## Goal
Allow an authenticated user to view the exact passage behind a retrieved citation.

## Plan
1. Define the endpoint and response contract.
2. Retrieve the requested passage using its document ID.
3. Apply tenant and role filters in the database query.
4. Return the exact source and passage for authorized documents.
5. Return 404 for missing or unauthorized documents to avoid revealing their existence.
6. Test authorized access, unauthorized access, missing documents, and unauthenticated requests.

## Security
- Identity comes from the authentication dependency.
- Tenant and roles are never accepted from request parameters.
- Authentication remains fail-closed until production JWT validation is configured.
