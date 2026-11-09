# Vector Database Access Control Policy

## 1. Tenant Identification
The system identifies a user's tenant through the `tenant_id` claim in a cryptographically signed JWT issued by the Identity Provider. The backend validates the token before trusting the claim.

## 2. Role Identification
The system identifies user roles through the `roles` claim in the validated JWT or through a database lookup using the authenticated user ID.

## 3. Access Denied
If the user's role is not included in a document's `allowed_roles`, access is denied with HTTP 403 Forbidden. Unauthorized attempts should be logged.

## 4. Missing Information
If tenant ID or role information is missing or invalid, the system follows a fail-secure, default-deny approach. It rejects the request with HTTP 401 Unauthorized. No default permissions are granted.

## 5. Tenant Isolation
Users must never access documents belonging to another tenant. Every document retrieval query must filter by the authenticated user's tenant ID.

## 6. Core Security Principle
Only authenticated users with the correct tenant and permitted role can retrieve a document.
