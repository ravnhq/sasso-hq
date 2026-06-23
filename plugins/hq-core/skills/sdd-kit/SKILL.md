---
name: sdd-kit
description: Use when starting any non-trivial feature (3+ steps or an architectural decision). Orchestrates the org's spec-driven development pipeline from interview through reviewed, merged code.
---

# SDD Kit — Spec-Driven Development

Orchestrates the house pipeline. Each stage uses a dedicated skill; this kit
stitches them with the gates between. Don't skip stages for non-trivial work;
the spec is the contract.

> **Building UI?** When the feature is frontend work (React-family web or React
> Native), reach for the optional `frontend-toolkit` skills during build and
> review (steps 5–7) — pick by concern: `component-design`, `state-management`,
> `styling-systems`, `data-fetching`, `forms-and-validation`,
> `animation-and-motion`, `accessibility-audit`, `frontend-performance`,
> `frontend-testing`, `devtools-debugging`, and the React Native trio
> (`native-performance`, `touch-interaction`, `mobile-navigation`).

## Pipeline

```
grill-me ──▶ to-prd ──▶ to-issues ──▶ writing-plans ──▶ executing-plans ──▶ tdd ──▶ requesting-code-review
 (interview)  (spec)     (slices)      (plan)         /subagent-driven/dispatch-kit  (review)
                                                          (build)
```

1. **Interview — `grill-me`** (or `grill-with-docs` if the project has a
   CONTEXT.md / ADRs). Resolve every branch of the decision tree before code.
   No building during this stage.
2. **Spec — `to-prd`.** Synthesize the interview into a PRD and publish it as a
   GitHub issue in the **current working repo** (the repo being worked on, not hq).
   The PRD is the contract.
3. **Slices — `to-issues`.** Break the PRD into independently-grabbable issues
   using tracer-bullet vertical slices.
4. **Plan — `writing-plans`** (superpowers). Turn a slice into a step-by-step plan.
5. **Build.** Two execution modes — pick by where the work should run:
   - *Inline* (spends this session's context): `executing-plans` or
     `subagent-driven-development` (superpowers). ≤5 files per phase; verify between.
   - *Dispatched* (separate, durable workers): `dispatch-kit` (hq, optional). After
     `to-issues` has produced independently-grabbable slices, `/dispatch` (or
     `/adopt <issue#>`) hands each to an autonomous worker in its own git worktree
     that implements it, opens one PR, and stops. Best for fanning independent
     slices out in parallel without consuming the orchestrator's context.
6. **Discipline — `tdd`** (superpowers). Red-green-refactor throughout step 5.
7. **Review — `code-review`** (hq-core) wrapping `requesting-code-review`. House
   gates must pass before merge.

## Gates (house rules)

- **Plan and build are separate.** Output the spec/plan first; no code until accepted.
- **Forced verification.** Don't claim done until type-check, lint, and tests are
  green *with evidence*.
- **Tracker = GitHub Issues, current repo.** Configurable, but this is the default.

## When to skip

Trivial, single-file, obvious changes don't need the full pipeline — go straight
to `tdd` + `code-review`. Use judgement; the pipeline is for 3+ step or
architectural work.
