---
name: feature-dev
description: Building a new feature end-to-end — from a vague idea to reviewed, merged code.
tags: [feature-dev, planning]
skills: [grill-me, sdd-kit, to-prd, to-issues, writing-plans, executing-plans, dispatch-kit, tdd, code-review, commit-conventions]
---

# Feature development

The full spec-driven path. Use it for anything 3+ steps or with an
architectural decision. Trivial single-file changes skip to TDD + review.

> **Building UI?** The optional `frontend-toolkit` skills (`component-design`,
> `state-management`, `styling-systems`, `data-fetching`, `forms-and-validation`,
> `accessibility-audit`, `frontend-performance`, `frontend-testing`, and the
> React Native trio) slot into steps 5–7 — reach for them by concern during build
> and review.

```mermaid
flowchart TD
    A[Vague idea] --> B[grill-me<br/>resolve every decision branch]
    B --> C[to-prd<br/>PRD → GitHub issue in the working repo]
    C --> D[to-issues<br/>tracer-bullet vertical slices]
    D --> E[writing-plans<br/>step-by-step plan per slice]
    E --> F[executing-plans<br/>build, ≤5 files per phase<br/>or dispatch-kit: durable workers]
    F --> G[tdd<br/>red-green-refactor throughout]
    G --> H[code-review<br/>house gates]
    H --> I{blocking findings?}
    I -- yes --> F
    I -- no --> J[commit-conventions → merge]
```

## The path

| Step | Skill | What you get |
|------|-------|--------------|
| 1. Interview | `grill-me` | Shared understanding; no code yet |
| 2. Spec | `to-prd` | A PRD as the contract, in the working repo's issues |
| 3. Slice | `to-issues` | Independently-grabbable tickets |
| 4. Plan | `writing-plans` | A reviewable plan per slice |
| 5. Build | `executing-plans` (inline) or `dispatch-kit` (durable workers) | Implementation, phased — inline, or one autonomous worker per slice |
| 6. Discipline | `tdd` | Tests drive the code |
| 7. Review | `code-review` | House quality gates before merge |
| 8. Commit | `commit-conventions` | Clean history |

`sdd-kit` orchestrates steps 1–7 with the house gates. Start there:
`/hq-core:sdd-kit`.

## Gates

- Plan and build are separate — accept the spec before any code.
- Forced verification — type-check, lint, tests green *with evidence* before "done".
- Loop step 6→5 until review has no blocking findings.
