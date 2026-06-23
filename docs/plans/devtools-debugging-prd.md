## Problem Statement

When a frontend engineer hits a bug in a running web app — a console error, a
failed network request, a layout that renders wrong, a page that janks — the
agent helping them tends to *guess from source*: it reads the component, forms a
theory, and edits, without ever observing the live page. That loop is slow and
frequently wrong, because the real signal (the actual console output, the actual
response body, the actual computed style) lives in the browser, not the source.
The team has the Chrome DevTools MCP available, which can drive a real Chrome and
surface exactly that signal — but there is no house skill telling an engineer how
to wire it up or how to debug *with* it, and no shared default that everyone on a
frontend repo gets it set up the same way.

## Solution

A new `frontend-toolkit` craft skill, `devtools-debugging`, that teaches the agent
to debug frontend issues against a **live Chrome via the Chrome DevTools MCP**
instead of guessing from source. It opens with a setup section that wires the MCP
into the working repo at **project scope** (so every frontend dev on the team gets
it by default), then teaches a reproduce-first debugging spine and four concrete,
MCP-tool-driven workflows. It defers general debugging discipline to
`superpowers:systematic-debugging`, hands performance fixes off to
`frontend-performance`, and points at `frontend-testing` for capturing the repro
as a regression test. It is web-only by construction — the DevTools MCP drives
Chrome — and says so explicitly.

## User Stories

1. As a frontend engineer, I want a house skill that wires the Chrome DevTools MCP into my repo, so that I don't have to figure out the install incantation myself.
2. As a frontend engineer, I want the MCP wired at project scope by default, so that everyone on my team debugs the same way without each person configuring it.
3. As a frontend engineer working solo, I want a documented user-level install variant, so that I can use the DevTools MCP across all my repos without committing config.
4. As a CI/automation author, I want a documented `--headless` variant, so that I can run the DevTools MCP in a non-interactive environment.
5. As a security-conscious engineer, I want `--isolated` recommended as the baseline, so that debugging runs in a throwaway profile and doesn't pollute or leak my real browser session.
6. As an engineer who just wired the MCP, I want a verification step (`claude mcp list`) and a troubleshooting note, so that I can confirm it's connected before I start debugging.
7. As an engineer chasing a console error, I want a workflow that navigates to the page, reproduces the error, reads the console, and traces it to source, so that I fix the real exception instead of a guessed one.
8. As an engineer chasing a failed API call, I want a workflow that inspects the live request/response/headers/status, so that I can tell a client bug from a server bug instead of assuming.
9. As an engineer chasing a layout or styling bug, I want a workflow that snapshots the live DOM and computed styles and screenshots the result, so that I diagnose what actually rendered rather than what the source implies.
10. As an engineer chasing a slow interaction, I want a workflow that records a performance trace and reads the bottleneck, so that I know where the time goes — and then hands me to `frontend-performance` for the fix.
11. As an engineer, I want the skill to follow a reproduce-first spine (reproduce in the live page → observe the real signal → one hypothesis → change one thing → verify in the same live page), so that my debugging is disciplined and grounded in observation.
12. As an engineer already using `superpowers:systematic-debugging`, I want this skill to defer the method to it and add only the live-page mechanics, so that I'm not taught the same discipline twice.
13. As a React Native engineer, I want the skill to state up front that it's web-only and point me to RN DevTools/Flipper, so that I'm not confused about why there's no mobile parity section.
14. As an engineer who just fixed a bug, I want a closing pointer to `frontend-testing`, so that I capture the repro as a regression test.
15. As an engineer who falls into a common trap (debugging a stale build, losing my auth session under `--isolated`, missing a layout bug because I ran headless), I want a pitfalls reference, so that I avoid the failure modes that waste the most time.
16. As an engineer mid-bug, I want an ordered live-page debugging checklist, so that I have a reproduce-first sequence to run against any frontend bug.
17. As an engineer using `recommend-workflow`, I want this skill registered in the taxonomy under `[frontend, debugging]`, so that it surfaces when I describe a frontend debugging task.
18. As a maintainer, I want the skill to mirror the sibling exemplar shape exactly (SKILL.md + references), so that the toolkit stays consistent and navigable.
19. As a maintainer, I want every MCP config snippet and tool sequence grounded against the Chrome DevTools MCP docs via Context7, so that the runbook is correct against the current server, not from memory.

## Implementation Decisions

**Skill package** — `plugins/frontend-toolkit/skills/devtools-debugging/`, mirroring
the sibling exemplar shape (`component-design`, `frontend-performance`, etc.):

- `SKILL.md` — frontmatter (`name: devtools-debugging`, a trigger-rich `description`),
  the reproduce-first spine, the four workflows, a short setup pointer into
  `references/setup.md`, the web-only scope line with the RN out-of-scope pointer,
  and the three cross-links. ~70–90 lines, matching siblings.
- `references/setup.md` — the wiring runbook, broken out as its own reference because
  setup is a first-class half of this skill and doesn't fit the snippets/pitfalls/
  checklist trio. Covers: prerequisites (current stable Chrome, Node ≥22); the
  **project-scoped install as the primary path** (`claude mcp add --scope project`
  → committed `.mcp.json` in the consuming repo) with `--isolated` headed as the
  baseline; the **user-level** and **`--headless` (CI)** variants; verification via
  `claude mcp list`; and troubleshooting.
- `references/snippets.md` — concrete MCP tool-call sequences, one per workflow,
  plus the config JSON. Grounded via Context7 against
  `/chromedevtools/chrome-devtools-mcp`.
- `references/pitfalls.md` — debugging a stale build, `--isolated` dropping your
  auth session, headless hiding layout/visual bugs, trusting source over the live
  page, and similar high-cost traps.
- `references/checklist.md` — an ordered, **reproduce-first** live-page debugging
  checklist (parallel in spirit to the perf skill's measure-first checklist).

**Debugging spine:** reproduce in the live page → observe the real signal
(console / network / DOM / screenshot) → form one hypothesis → change one thing →
verify in the same live page. The skill explicitly defers the general debugging
discipline to `superpowers:systematic-debugging` and adds only what's unique to
debugging against a running Chrome through the MCP.

**Four workflows** (each a concrete MCP-tool sequence): (1) console errors /
uncaught exceptions; (2) failed or wrong network requests; (3) DOM / layout /
styling bugs; (4) performance regressions — kept deliberately thin, a hand-off
into `frontend-performance` rather than a duplicate fix method. Deep
React-internals/profiler debugging is named as a limitation, not faked as a
workflow, because the DevTools MCP doesn't expose React DevTools cleanly.

**Scope:** web-only (the DevTools MCP drives Chrome). One explicit line directing
React Native debugging to RN DevTools / Flipper as out of scope.

**Cross-links:** `superpowers:systematic-debugging` (owns the method),
`frontend-performance` (owns the perf fix, workflow 4 hands off), `frontend-testing`
(capture the repro as a regression test). No link to `accessibility-audit`.

**Setup-scope decision:** the project-scoped MCP is configured in the *consuming
frontend repo*, not in hq. hq is a plugins repo, not a frontend app, so no
`.mcp.json` is committed into hq itself; the setup runbook instructs the reader to
add it in their own repo.

**Registration / housekeeping (CI-enforced by `scripts/build-catalog.py`):**

- `plugins/hq-core/taxonomy.yml`: add `devtools-debugging: [frontend, debugging]`.
  Uses the existing `debugging` vocab tag — no new vocab needed.
- Regenerate `plugins/hq-core/catalog.json` via `uv run scripts/build-catalog.py`.
- `CHANGELOG.md` `[Unreleased]`: add an entry under frontend-toolkit.

**Version targets:** `chrome-devtools-mcp@latest`, current stable Chrome, Node ≥22.
All config and tool snippets grounded against `/chromedevtools/chrome-devtools-mcp`
via Context7 at authoring time, version-noted in the skill like its siblings.

## Testing Decisions

A skill is a documentation artifact, not executable code — the sibling exemplars
(#27–#37) shipped **no unit tests**, and this skill follows suit. "A good test"
here means verifying *external behavior the skill promises*, which is:

- **Catalog/registration correctness** — `uv run scripts/build-catalog.py` must
  pass: the skill's `SKILL.md` frontmatter must parse, `name` must match the
  `taxonomy.yml` entry, and its tags must be drawn from the locked vocab. This is
  the prior art for "tests" in this repo and is CI-enforced.
- **Snippet/runbook correctness** — every MCP config block and tool sequence is
  grounded against Context7 (`/chromedevtools/chrome-devtools-mcp`) at authoring
  time, exactly as the sibling skills grounded their snippets. Code review verifies
  the snippets against that source (the house bar applied to #27–#37).

No new automated test code is introduced. Verification = catalog build green +
Context7-grounded review.

## Out of Scope

- Committing a `.mcp.json` into the hq repo itself (hq is a plugins repo).
- React Native / mobile debugging (no Chrome; pointer to RN DevTools / Flipper).
- A from-scratch debugging *method* — deferred to `superpowers:systematic-debugging`.
- A performance *fix* method — deferred to `frontend-performance`; workflow 4 only
  diagnoses and hands off.
- Deep React-internals / React DevTools profiler debugging — named as a limitation,
  not built as a workflow.
- An exhaustive flag reference for the DevTools MCP — the skill covers the baseline
  plus 2–3 knobs and links upstream for the rest.

## Further Notes

- Title convention follows the siblings: `frontend-toolkit: devtools-debugging skill`.
- The `debugging` vocab tag already exists in `taxonomy.yml`; this is the first
  frontend skill to use it, which is the intended fit.
- Single self-contained skill = one buildable slice, so `to-issues` collapses to
  this one issue; build proceeds on a branch → PR → house code review, matching how
  #27–#37 were delivered.
