# Ask Feature Specification

## 1. Problem
Users need answers to questions based on documents they are authorized to access.

## 2. Expected behaviour
- Accept a non-empty question.
- Identify the authenticated user's tenant and roles.
- Retrieve only documents permitted for that tenant and role.
- Apply access-control filters before ranking results.
- Assemble retrieved passages within a configured context-token budget.
- Generate answers using only the retrieved passages.
- Return citations containing the source and supporting passage.
- Return "I don't know" when the retrieved passages do not support an answer.
- Never expose documents belonging to another tenant or unauthorized role.

## 3. Authentication and authorization
- Production requests must use validated Microsoft Entra ID JWTs.
- Validate token signature, issuer, audience, and expiry.
- Obtain tenant and roles only from validated claims or trusted identity data.
- Missing or invalid authentication must be rejected.
- Local tests may override the authentication dependency with test-only users.
- No production authentication bypass or trusted request headers.

## 4. Context budget
- Use a configurable maximum context-token budget.
- Include only complete passages that fit within the budget.
- Do not silently exceed the budget.

## 5. Citations
- Every factual answer must include supporting source citations.
- A citation must identify the source and the supporting passage.
- Do not invent citations or unsupported facts.

## 6. Show source passage
- Provide a way to display the exact passage associated with a citation.
- The passage must come from an authorized retrieved document.
- Unauthorized users must not be able to retrieve the passage.

## 7. Evaluation
- Create a 15-question golden test set.
- Record the expected source chunk for each question.
- Calculate recall@k for retrieval.
- Include tests for missing evidence, tenant isolation, role filtering, and context budget.

## 8. Out of scope
- Production Microsoft Entra ID configuration until application details are provided.
- Training or fine-tuning an LLM.
- Allowing the LLM to access the database directly.
