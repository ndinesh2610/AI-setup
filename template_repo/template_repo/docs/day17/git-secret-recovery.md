# Day 17 — Git Secret Recovery Drill

## Practice Results

- Repository: /tmp/day17_git_drill_repo
- Branch: oops
- Leaked file: settings.txt
- Secret: Deliberately fake training key
- Detection: Gitleaks custom rule
- Initial scan: 1 finding
- Final scan: 0 findings
- History cleanup: git filter-repo
- Credential rotation: Simulated only

## Five-Step Team Recovery Procedure

1. Revoke or rotate the exposed credential immediately.
2. Identify the affected files, commits, branches and systems.
3. Remove the secret from source code and move credentials
   to a secure secret manager.
4. If history cleanup is necessary, coordinate with the team
   and rewrite affected Git history using git-filter-repo.
5. Verify the cleanup, notify collaborators to re-clone,
   and prevent old clones or forks from restoring the secret.

## Important Lessons

- Deleting a file in a new commit does not erase Git history.
- A clean Gitleaks scan does not guarantee no secrets exist.
- History rewriting does not revoke an exposed credential.
- Rewriting shared history requires team coordination.
- Never force-push rewritten history without approval.
