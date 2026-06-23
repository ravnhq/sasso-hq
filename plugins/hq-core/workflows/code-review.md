---
name: code-review
description: Reviewing a diff, branch, or PR to the org standard before merge.
tags: [review, security]
skills: [code-review, requesting-code-review, commit-conventions]
---

# Code review

The org review path. `code-review` is the standard; `requesting-code-review`
(superpowers) is the mechanic that gathers the diff.

```mermaid
flowchart TD
    A[Change ready] --> B[requesting-code-review<br/>gather diff + findings]
    B --> C[code-review<br/>apply house gates]
    C --> D{blocking?}
    D -- yes --> E[author fixes]
    E --> B
    D -- no --> F[commit-conventions → merge]
```

## House gates (block on these)

1. **Correctness** — bugs, edge cases, unhandled real-contract errors.
2. **Verification** — green type-check/lint/tests *with evidence*, not "should work".
3. **Structural integrity** — no duplicated state, one source of truth, fix flawed
   architecture rather than patch it.
4. **Simplicity** — fewer lines if equally clear; no speculative generality.
5. **Dead code** — no unused imports/exports/debug logs.
6. **Security** — secrets, injection, authz gaps.
7. **Tests** — test the code, not themselves; integration over unit where it fits.

Verdict is explicit: approve / approve-with-nits / request-changes. Never
approve with blocking items open.
