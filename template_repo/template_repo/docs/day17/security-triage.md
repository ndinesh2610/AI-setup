# Day 17 — Security Triage Report

## Security Scan Results

| Tool | Result |
|---|---|
| Pytest | 60 tests passed |
| Ruff | All checks passed |
| Bandit | No findings reported |
| Gitleaks | Passed |
| pip-audit | No known vulnerabilities after update |
| Semgrep OSS 1.150.0 | 456 rules, 68 files, 1 finding |
| Pyright (upload module) | 0 errors |
| Pyright (repository) | 27 errors remain |

## Finding 1: Vulnerable Dependency

- Package: opentelemetry-api
- Vulnerable version: 1.45.1
- Advisory: CVE-2026-126360
- Fixed version: 1.45.2
- Status: Fixed
- Verification: pip-audit reports no known vulnerabilities.

## Finding 2: Semgrep CSRF Warning

- File: app/templates/index.html
- Rule: django-no-csrf-token
- Classification: Likely false positive
- Reason: Application uses FastAPI/Jinja2, not Django.
- Evidence: Form includes a hidden csrf_token field.
- Backend: app/routers/ui.py validates the token using
  secrets.compare_digest and returns HTTP 403 on mismatch.
- Status: Reviewed; no code change required for this finding.

## Finding 3: Semgrep Engine Crash

- Semgrep 1.187.0 crashed with signal 11 under WSL2.
- Semgrep 1.150.0 completed successfully.
- Status: Workaround verified.

## Remaining Work

- Resolve repository-wide Pyright errors.
- Verify upload functionality with real authentication.
- Review upload storage and PDF processing security.
- Complete the remaining Day 17 security exercises.
