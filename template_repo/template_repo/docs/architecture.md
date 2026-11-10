# Day 9 — Solution Architecture

## Problem
Employees need reliable answers from company policy documents, with citations and access restricted to authorized users.

## Users
- Employees asking policy questions.
- Managers and other authorized roles, subject to document permissions.

## Data and rationale
- PostgreSQL with pgvector stores document text, metadata, and 384-dimensional embeddings.
- Sentence Transformers (all-MiniLM-L6-v2) generates question embeddings.
- Each document has a tenant ID and allowed roles.
- Tenant and role filters are applied before similarity ranking.

## Main components
1. FastAPI exposes /ask and /sources/{document_id}.
2. Authentication dependency supplies the user's tenant and roles.
3. Retrieval service performs authorized vector search.
4. Context service enforces the configured token budget.
5. Answering service builds a grounded prompt and calls the configured LLM.
6. Citations return the source passages used.
7. Show Source returns the exact stored passage after authorization checks.

## Request flow
1. Authenticate the user.
2. Embed the question.
3. Retrieve only documents matching the user's tenant and roles.
4. Select passages within the token budget.
5. Ask the LLM to answer only from those passages.
6. Return the answer and citations, or an "I don't know" fallback.
7. When requested, fetch a citation's exact passage through the protected source endpoint.

## Out of scope
- Production identity-provider/JWT integration until Entra ID configuration is available.
- Document upload and ingestion APIs.
- Production deployment, monitoring, and scaling.
- Evaluation on a large representative document corpus.

## Key decisions
- Fail closed when authentication is not configured.
- Never accept tenant or roles from user-supplied request parameters.
- Apply authorization filters in SQL before ranking.
- Return 404 for missing or unauthorized source documents.
- Evaluate retrieval independently of the LLM using a 15-question golden set.
