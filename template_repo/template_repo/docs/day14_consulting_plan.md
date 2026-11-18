# Day 14 - Knowledge Assistant Consulting Plan

## 1. Confirmed Requirements

- Build a Knowledge Assistant using FastAPI, Jinja2 and HTMX.
- Display answers and document citations.
- Enable HTML autoescaping, CSRF protection and CSP.
- Provide accessible labels, keyboard navigation and visible focus.
- Display clear loading states and actionable error messages.

## 2. Suggestions

- Add production JWT authentication.
- Provide feedback on answer quality.
- Add automated browser accessibility tests.
- Improve mobile responsiveness and monitoring.

## 3. Risks and Caveats

- Authentication is not configured for live answer generation.
- PostgreSQL and the LLM service must be available.
- Retrieved documents may contain malicious content.
- Generated answers may be inaccurate.
- Production deployment requires HTTPS.

## Acceptance Tests

| Test | Expected Result | Status |
|---|---|---|
| Open Knowledge Assistant | Page renders correctly | Passed |
| Submit question | Answer and citations displayed | Mock-tested |
| Invalid CSRF token | Request rejected with 403 | Passed |
| Empty question | Request rejected with 400 | Passed |
| Script injection | Script rendered as escaped text | Passed |
| CSP header | Restrictive policy present | Passed |
| Keyboard navigation | Visible focus and keyboard operation | Passed |
| Unauthorized request | Helpful authentication error | Passed |
| Live authenticated answer | Grounded answer with citations | Pending JWT |

## UX Review

- Clear field labels and plain language.
- Visible keyboard focus.
- High-contrast text and buttons.
- Loading indicator implemented.
- Actionable authentication error verified in browser.

## Test Evidence

37 automated tests passed.
