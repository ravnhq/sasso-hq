# hq

Org agent hub. Unified Claude Code skills, plugins, and workflow playbooks —
consumed via the native plugin marketplace, **no cloning required**.

## Get started

In any repo, from Claude Code:

```shell
/plugin marketplace add ravnhq/sasso-hq
/plugin install hq-core@hq
```

Then run `/hq-core:onboarding` — it takes over from there: asks what you're
working on, recommends the right skills, and walks you through the workflow.

> Private repo — your machine needs GitHub access (SSH or `gh`). You already
> have this from day-one setup.

## What's here

- **`hq-core`** (mandatory) — onboarding, workflow recommendations, code-review
  standards, commit conventions, the SDD pipeline, plus the `grill-me` /
  `grill-with-docs` / `to-prd` / `to-issues` / `handoff` skills.
- **`codebase-toolkit`** (optional) — `map-the-codebase`,
  `improve-codebase-architecture`, `write-a-skill`, `triage`, `zoom-out`,
  `prototype`.
- **`fun`** (optional) — `caveman`.
- **`chatbot-toolkit`** (optional) — build a full-stack, Claude-powered Meta
  messaging bot (WhatsApp + Instagram).
- **`frontend-toolkit`** (optional) — cross-cutting frontend craft for
  React-family web + React Native: `component-design`, `state-management`,
  `styling-systems`, `data-fetching`, `forms-and-validation`,
  `animation-and-motion`, `accessibility-audit`, `frontend-performance`,
  `frontend-testing`, `mobile-navigation`, `touch-interaction`,
  `native-performance`.

Don't install the optional plugins blindly. Run `/hq-core:onboarding` (or
`/hq-core:recommend-workflow`) and it installs the ones relevant to your task —
keeping per-session context cost down. Full machine-readable index:
[`plugins/hq-core/catalog.json`](./plugins/hq-core/catalog.json).

## Contributing

Open a PR. CI validates structure; a `hq-core` maintainer reviews. `hq-core`
and `taxonomy.yml` are locked to the core group. Rolling `main` — merged
changes ship to everyone on their next `/plugin marketplace update`.

See [`SPEC.md`](./SPEC.md) for the full design.
