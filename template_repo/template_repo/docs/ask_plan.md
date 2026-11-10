# Ask Feature Implementation Plan

## Phase 1: Retrieval foundation
- Reuse the existing PostgreSQL pgvector documents table.
- Define an authenticated user context containing tenant ID and roles.
- Apply tenant and role filters before similarity ranking.
- Add automated tests for tenant and role isolation.

## Phase 2: Context assembly
- Add a configurable context-token budget.
- Assemble complete retrieved passages without exceeding the budget.
- Test empty results and budget limits.

## Phase 3: Grounded answering
- Use the existing provider-agnostic LLM client.
- Build prompts that treat retrieved documents as untrusted reference data.
- Validate the answer and citation structure.
- Return "I don't know" when evidence is missing.
- Test citations and unsupported questions.

## Phase 4: Source passage feature
- Write the feature specification and task breakdown.
- Write failing tests first.
- Implement retrieval of the exact cited passage.
- Enforce the same tenant and role authorization.
- Test authorized and unauthorized access.

## Phase 5: Retrieval evaluation
- Create 15 golden questions with expected source chunk IDs.
- Run retrieval against the golden set.
- Calculate recall@k and record the results.

## Phase 6: Documentation and review
- Complete the architecture document.
- Complete the AI-assist log.
- Review every changed line and run the full test and lint suites.

## Security dependency
Production authentication remains incomplete until Microsoft Entra ID
configuration is supplied. The API must fail closed without a real
validated authentication dependency. Tests may inject test-only users.
