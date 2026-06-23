---
name: commit-conventions
description: Use when writing a commit message or preparing a commit in any org repo. Enforces the house Conventional Commits format.
---

# Commit Conventions

House format: **Conventional Commits**, terse, intent-first.

## Format

```
<type>(<optional scope>): <subject>

<optional body — only when the "why" isn't obvious from the subject>
```

- **type**: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `perf`, `ci`, `build`.
- **subject**: imperative mood, ≤50 chars, no trailing period.
- **body**: wrap at ~72 cols. Explain *why*, not *what* — the diff shows what.
  Omit entirely when the subject is self-evident.
- **breaking change**: footer `BREAKING CHANGE: <description>`.

## Rules

- One logical change per commit. Cleanup (dead code removal) commits separately
  from feature work.
- No noise bodies restating the subject.
- Reference issues in the footer when relevant: `Refs #123`.

## Examples

```
fix(auth): use <= for token expiry check

Off-by-one let tokens live one tick past expiry.
```

```
refactor(catalog): generate from taxonomy instead of frontmatter
```
