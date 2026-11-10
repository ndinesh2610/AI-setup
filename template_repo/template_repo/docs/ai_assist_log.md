# AI Assistance Log — Day 9

## Date
2026-11-10

## Work completed
AI assistance was used to help:
- Draft the `/ask` and Show Source specifications and implementation plans.
- Design retrieval, context assembly, and answer-generation services.
- Create and refine unit and API tests.
- Draft the 15-question retrieval evaluation set.
- Implement the Recall@k evaluation script.
- Prepare the architecture and task documentation.

## Human review and validation
- Reviewed command outputs and corrected implementation issues.
- Ran the test suite: 28 tests passed.
- Ran Ruff checks: all checks passed.
- Ran retrieval evaluation: 15 questions evaluated; Recall@1, Recall@3, and Recall@5 were 100%.

## Important decisions
- Tenant and role authorization is enforced in database queries.
- Authentication fails closed because production Entra ID/JWT configuration is not available.
- Retrieval evaluation does not call the LLM.
- Show Source returns 404 for missing or unauthorized documents.

## Limitations
- Retrieval results are preliminary because the evaluation corpus contains only five authorized documents.
- Production authentication and a representative larger evaluation corpus remain outstanding.
- AI-generated changes must be reviewed before submission.
