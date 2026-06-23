---
name: code-review
description: Use when reviewing code, a diff, a branch, or a PR to the org's standard. Wraps the review mechanic with house quality gates — the org entry point for code review.
---

# Code Review (house standard)

The org entry point for review. This skill is the *standard*; superpowers
`requesting-code-review` is the *mechanic*. Run the mechanic, then enforce the
gates below before any approval.

## Run the mechanic

Invoke superpowers `requesting-code-review` (or the built-in `/code-review`) to
gather the diff and produce findings. If neither is installed, review the diff
directly.

## House gates — what we reject in review

Review as a senior, perfectionist engineer would. Block on:

1. **Correctness** — bugs, edge cases, race conditions, unhandled errors that
   should be handled (real contracts, not defensive noise).
2. **Verification** — was it actually run? Type-checker/linter/tests green is
   claimed *with evidence*, not asserted. No "should work."
3. **Structural integrity** — duplicated state, one-source-of-truth violations,
   inconsistent patterns, band-aids over flawed architecture. Propose the
   structural fix, don't rubber-stamp the patch.
4. **Simplicity** — fewer lines if equally clear; no speculative generality; no
   over-engineering for imaginary scenarios.
5. **Dead code** — unused imports/exports/props, debug logs, ghosts.
6. **Security** — secrets, injection, authz gaps, unsafe deserialization.
7. **Tests** — they test the code, not themselves; integration over unit where it fits.

## Output

For each finding: location, problem, fix — one line each. Separate **blocking**
from **nice-to-have**. End with an explicit verdict: approve / approve-with-nits /
request-changes. Never approve with blocking items open.
