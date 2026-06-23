# frontend-toolkit Walking Skeleton + component-design Exemplar — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stand up the `frontend-toolkit` plugin end-to-end with one fully-authored exemplar skill (`component-design`), wired into the hub so hq CI is green — establishing the pattern the other 11 skills (issues #27–#37) will copy.

**Architecture:** A new optional plugin `plugins/frontend-toolkit/` containing one skill directory. The skill is markdown only — `SKILL.md` plus a `references/` bundle. Wiring is data-driven: `marketplace.json` registers the plugin, `taxonomy.yml` carries the tag vocab + skill→tag map, and `scripts/build-catalog.py` regenerates `catalog.json` from those two sources. There is no runtime code and no test suite; verification is the existing static CI (`scripts/build-catalog.py` + `scripts/check-workflows.py` + the JSON/frontmatter checks in `.github/workflows/ci.yml`).

**Tech Stack:** Markdown skills, JSON manifests, a Python 3.12 catalog generator (`scripts/build-catalog.py`, depends on `pyyaml`). Snippets in the skill target React 19 + current React Native/Expo, grounded via the Context7 MCP.

---

## Verification model (read first)

This plugin has no unit tests. "Green" means all four CI gates in `.github/workflows/ci.yml` pass locally:

1. **JSON manifests parse** — `marketplace.json` + every `plugin.json` are valid JSON.
2. **SKILL.md frontmatter present** — every `SKILL.md` starts with a `---` line.
3. **Catalog fresh + taxonomy valid** — `python3 scripts/build-catalog.py` exits 0 (every first-party skill is in `taxonomy.yml` with tags ⊆ `vocab`; no taxonomy entry lacks a SKILL.md) **and** the committed `catalog.json` matches the generator output (`git diff --exit-code plugins/hq-core/catalog.json`).
4. **Workflow playbooks reference real skills** — `python3 scripts/check-workflows.py` exits 0. It only inspects each playbook's `skills:` frontmatter list, **not prose**.

**Hard constraint from gate 3:** a skill's `SKILL.md` and its `taxonomy.yml` entry must land together. Adding the dir without the taxonomy entry (or vice-versa) fails the build.

**Hard constraint from gate 4:** do **not** add `component-design` (or any frontend skill) to `feature-dev.md`'s `skills:` frontmatter. The pointer is prose only. (Adding it to frontmatter is allowed only once the skill exists in the catalog, but the decision is prose-only to avoid coupling — keep it prose.)

Run the full local verification any time with:

```bash
python3 scripts/build-catalog.py && \
git diff --exit-code plugins/hq-core/catalog.json && \
python3 scripts/check-workflows.py && \
for f in .claude-plugin/marketplace.json plugins/*/.claude-plugin/plugin.json; do python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$f"; done && \
echo "ALL GREEN"
```

Ensure `pyyaml` is importable first: `python3 -c "import yaml" || pip install pyyaml`.

---

## File structure

| Path | Responsibility | Action |
|------|----------------|--------|
| `plugins/frontend-toolkit/.claude-plugin/plugin.json` | Plugin manifest (name, description, author) | Create |
| `plugins/frontend-toolkit/skills/component-design/SKILL.md` | The exemplar skill body + frontmatter | Create |
| `plugins/frontend-toolkit/skills/component-design/references/checklist.md` | Component-design review checklist | Create |
| `plugins/frontend-toolkit/skills/component-design/references/snippets.md` | Context7-grounded React/RN code snippets | Create |
| `plugins/frontend-toolkit/skills/component-design/references/pitfalls.md` | Common mistakes + fixes | Create |
| `.claude-plugin/marketplace.json` | Register `frontend-toolkit` as an optional plugin | Modify |
| `plugins/hq-core/taxonomy.yml` | Add `frontend`+`perf` to vocab; add `component-design` to skills | Modify |
| `plugins/hq-core/catalog.json` | Regenerated index | Regenerate (never hand-edit) |
| `plugins/hq-core/workflows/feature-dev.md` | Prose pointer to frontend-toolkit | Modify |
| `plugins/hq-core/skills/onboarding/SKILL.md` | List frontend-toolkit among optional plugins | Modify |
| `README.md` | List frontend-toolkit among optional plugins | Modify |
| `CHANGELOG.md` | Unreleased entry | Modify |

---

## Task 1: Plugin skeleton + marketplace registration

**Files:**
- Create: `plugins/frontend-toolkit/.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`

- [ ] **Step 1: Create the plugin manifest**

Create `plugins/frontend-toolkit/.claude-plugin/plugin.json`:

```json
{
  "name": "frontend-toolkit",
  "description": "Optional: cross-cutting frontend craft skills for React-family web + React Native — components, state, styling, data fetching, forms, motion, accessibility, performance, and testing.",
  "author": {
    "name": "HQ Core Team",
    "email": "raphaelsasso@ravn.co"
  }
}
```

- [ ] **Step 2: Register the plugin in the marketplace**

In `.claude-plugin/marketplace.json`, add this object to the end of the `plugins` array (after the `dispatch-kit` entry — add a comma after the `dispatch-kit` object's closing brace):

```json
    {
      "name": "frontend-toolkit",
      "source": "./plugins/frontend-toolkit",
      "description": "Optional: cross-cutting frontend craft skills for React-family web + React Native — components, state, styling, a11y, performance, and testing."
    }
```

- [ ] **Step 3: Verify both manifests parse**

Run:
```bash
for f in .claude-plugin/marketplace.json plugins/frontend-toolkit/.claude-plugin/plugin.json; do python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$f" && echo "ok $f"; done
```
Expected: `ok .claude-plugin/marketplace.json` and `ok plugins/frontend-toolkit/.claude-plugin/plugin.json`. No `JSONDecodeError`.

- [ ] **Step 4: Commit**

```bash
git add plugins/frontend-toolkit/.claude-plugin/plugin.json .claude-plugin/marketplace.json
git commit -m "feat(frontend-toolkit): scaffold plugin + register in marketplace"
```

---

## Task 2: Add the tag vocab and exemplar skill mapping to taxonomy

Do this **before** authoring the skill, so the catalog generator has the mapping ready. The catalog stays stale until Task 4 regenerates it; that is expected and CI is not run mid-task.

**Files:**
- Modify: `plugins/hq-core/taxonomy.yml`

- [ ] **Step 1: Add `frontend` and `perf` to the vocab**

In `plugins/hq-core/taxonomy.yml`, the `vocab:` list currently ends with the `meta` line. Add two entries immediately after the `data` line and before `meta` (keep alignment with the existing inline comments):

```yaml
  - data           # data/ML pipelines, analysis
  - frontend       # UI / component / styling / client-side work (web + mobile)
  - perf           # performance profiling + optimization (frontend or backend)
  - meta           # skills about the workflow itself (onboarding, handoff, authoring)
```

- [ ] **Step 2: Register `component-design` in the skills map**

In the `skills:` block, add this line (placement is not significant; put it after the `caveman: [meta]` line to group it before the chatbot skills, or anywhere in the block):

```yaml
  component-design: [frontend, feature-dev]
```

- [ ] **Step 3: Sanity-check YAML parses**

Run:
```bash
python3 -c "import yaml; d=yaml.safe_load(open('plugins/hq-core/taxonomy.yml')); assert 'frontend' in d['vocab'] and 'perf' in d['vocab']; assert d['skills']['component-design']==['frontend','feature-dev']; print('taxonomy ok')"
```
Expected: `taxonomy ok`.

- [ ] **Step 4: Commit**

```bash
git add plugins/hq-core/taxonomy.yml
git commit -m "feat(taxonomy): add frontend + perf tags and component-design mapping"
```

---

## Task 3: Author the `component-design` exemplar skill

This is the pattern the other 11 skills copy: a focused `SKILL.md` plus three reference files. Snippets MUST be grounded against Context7 before writing — do not write React/RN code from memory.

**Files:**
- Create: `plugins/frontend-toolkit/skills/component-design/SKILL.md`
- Create: `plugins/frontend-toolkit/skills/component-design/references/checklist.md`
- Create: `plugins/frontend-toolkit/skills/component-design/references/snippets.md`
- Create: `plugins/frontend-toolkit/skills/component-design/references/pitfalls.md`

- [ ] **Step 1: Ground the snippets via Context7**

Before writing any code block, fetch current docs:
- `mcp__context7__resolve-library-id` with `react` → pick the React 19 entry → `mcp__context7__query-docs` with a query like "component composition, props, children, memo, forwardRef in React 19".
- Repeat for `react-native` (current stable) → query "function components, props, FlatList item components".

Keep the resolved library IDs and versions; you will cite them as the skill's version targets. If Context7 is unavailable in the worker, STOP and surface that — do not fall back to memory (per the PRD grounding decision).

- [ ] **Step 2: Write `SKILL.md`**

Create `plugins/frontend-toolkit/skills/component-design/SKILL.md`. Frontmatter `name` MUST equal the directory name `component-design` (CI/catalog match). Description follows the house "what it does + when to use" shape seen in sibling skills:

```markdown
---
name: component-design
description: Design React-family and React Native components with clear composition, prop boundaries, and ownership — when to split, when to compose, what to lift, and what to keep local. Use when creating a new component, refactoring a bloated one, deciding a component's props/children API, or reviewing component structure.
---

# Component design

Stack-agnostic principles, concrete examples in React 19 and React Native.
The examples port to Vue/Svelte; the judgments don't change.

**Version targets:** React 19, React Native (current stable). Snippets grounded
against Context7 at authoring time — see `references/snippets.md`.

## The core question

Every component decision reduces to: *what does this component own, and what does
it merely render?* Owned state and behavior justify a component; pure rendering of
parent-owned data is often a prop or a child, not a new component.

## Principles

- **Compose over configure.** Prefer `children` and slot props to a growing list
  of boolean flags. A component with 8 `is*`/`show*` props is usually several
  components wearing a trench coat.
- **Lift state to its lowest common owner — no higher.** State lives at the
  closest ancestor that needs it. Lifting "just in case" creates prop-drilling
  and re-render cost.
- **Keep the public prop surface narrow and honest.** Props are an API. Fewer,
  well-named props beat many overlapping ones. Avoid leaking implementation
  (no `className` pass-through unless the component is genuinely a primitive).
- **Separate layout from data.** A component that both fetches and lays out is
  hard to reuse and test. Split the data owner from the presentational shell.
- **Mobile parity.** The same ownership rules hold in React Native; the
  difference is primitives (`View`/`Text`/`Pressable`) and that list item
  components must be cheap (they render many times). See `references/pitfalls.md`.

## How to use this skill

1. Run the **`references/checklist.md`** against the component you're designing or reviewing.
2. Reach for a pattern in **`references/snippets.md`** (composition, compound components, controlled/uncontrolled, RN list item).
3. Check **`references/pitfalls.md`** before you ship — most component PRs hit at least one.

## Related

- State that crosses components → `state-management`
- Styling the component → `styling-systems`
- Making it accessible → `accessibility-audit`
- Testing it by behavior → `frontend-testing`
```

- [ ] **Step 3: Write `references/checklist.md`**

Create `plugins/frontend-toolkit/skills/component-design/references/checklist.md`:

```markdown
# Component design checklist

Run this against any component you create or review.

## Ownership
- [ ] Does this component own state/behavior, or is it just rendering parent data? (If the latter, should it be a prop or child instead?)
- [ ] Is each piece of state at the lowest common owner — not lifted "just in case"?
- [ ] Is there exactly one source of truth for each value it renders? (No state copied to fix a render.)

## Prop surface
- [ ] Are there ≤ ~5 meaningful props? More usually means split or compose.
- [ ] Are boolean flags (`isX`, `showY`) multiplying? Prefer `children`/slots.
- [ ] Are prop names honest about what they do (no leaked internals)?
- [ ] Are required vs optional props clear, with sensible defaults?

## Composition
- [ ] Could a config-heavy component be expressed as composition (`children`, compound components)?
- [ ] Is data-fetching separated from presentation?
- [ ] Is the component reusable without its current parent's context?

## React Native parity (if applicable)
- [ ] Are list item components cheap (memoized, no inline allocation per render)?
- [ ] Primitives correct (`View`/`Text`/`Pressable`, not web `div`/`span`)?

## Reuse / boundaries
- [ ] Does a sibling skill own part of this? (state → `state-management`, styling → `styling-systems`, a11y → `accessibility-audit`.)
```

- [ ] **Step 4: Write `references/snippets.md`**

Create `plugins/frontend-toolkit/skills/component-design/references/snippets.md`. Fill each fenced block with the **Context7-grounded** code from Step 1. The structure below is the contract; the code must be real React 19 / current RN, not invented:

```markdown
# Component design snippets

> Grounded against Context7: React 19 (`<resolved-id>`) and React Native
> (`<resolved-id>`). Update the IDs/versions when you re-ground.

## Compose over configure (children + slots)
<!-- Replace with a Context7-grounded React 19 example: a Card that takes
     children/slots instead of title/subtitle/footer boolean-driven props. -->
\`\`\`tsx
// ...grounded React 19 snippet...
\`\`\`

## Compound components
<!-- Grounded example: <Tabs>/<Tabs.List>/<Tabs.Panel> sharing state via context. -->
\`\`\`tsx
// ...grounded React 19 snippet...
\`\`\`

## Controlled vs uncontrolled
<!-- Grounded example showing both, and when to pick each. -->
\`\`\`tsx
// ...grounded React 19 snippet...
\`\`\`

## React Native: a cheap list item
<!-- Grounded RN example: memoized FlatList renderItem with stable callbacks. -->
\`\`\`tsx
// ...grounded React Native snippet...
\`\`\`
```

- [ ] **Step 5: Write `references/pitfalls.md`**

Create `plugins/frontend-toolkit/skills/component-design/references/pitfalls.md`:

```markdown
# Component design pitfalls

## Boolean prop explosion
**Symptom:** `<Modal isOpen isFullscreen showHeader showFooter hideClose ...>`.
**Fix:** compose — `<Modal><Modal.Header/>...</Modal>` — or split into variants.

## Premature state lifting
**Symptom:** state lives three levels up and is prop-drilled through components
that only pass it along.
**Fix:** move state down to the lowest common owner; if truly cross-cutting, that's
a `state-management` concern, not deeper drilling.

## God component
**Symptom:** one component fetches data, manages state, lays out, and styles.
**Fix:** split the data owner from the presentational shell; the shell takes props.

## Duplicated source of truth
**Symptom:** state copied into another `useState` to fix a stale render.
**Fix:** one source of truth; derive, don't copy. (This is the "One Source of Truth" rule.)

## RN: expensive list items
**Symptom:** janky `FlatList`; new closures/objects allocated per row render.
**Fix:** memoize the item component; hoist stable callbacks; give `keyExtractor`.

## className/style pass-through on non-primitives
**Symptom:** every component accepts `className` and forwards it, leaking layout
control to callers.
**Fix:** only true primitives expose styling hooks; others own their look.
```

- [ ] **Step 6: Verify the skill files exist and frontmatter is well-formed**

Run:
```bash
test -f plugins/frontend-toolkit/skills/component-design/SKILL.md && \
head -n1 plugins/frontend-toolkit/skills/component-design/SKILL.md | grep -qx -- '---' && \
ls plugins/frontend-toolkit/skills/component-design/references/{checklist,snippets,pitfalls}.md && \
python3 -c "import yaml; t=open('plugins/frontend-toolkit/skills/component-design/SKILL.md').read(); fm=yaml.safe_load(t.split('---',2)[1]); assert fm['name']=='component-design', fm['name']; print('skill ok')"
```
Expected: the three reference paths listed and `skill ok`.

- [ ] **Step 7: Commit**

```bash
git add plugins/frontend-toolkit/skills/component-design/
git commit -m "feat(frontend-toolkit): add component-design exemplar skill"
```

---

## Task 4: Regenerate the catalog

**Files:**
- Regenerate: `plugins/hq-core/catalog.json`

- [ ] **Step 1: Ensure pyyaml is available**

Run: `python3 -c "import yaml" || pip install pyyaml`
Expected: no output (already present) or a successful install.

- [ ] **Step 2: Run the catalog generator**

Run: `python3 scripts/build-catalog.py`
Expected: `wrote plugins/hq-core/catalog.json (N entries)` where N is one more than before. No `catalog build failed` lines. If it reports `component-design ... not in taxonomy.yml`, Task 2 was skipped — fix that first.

- [ ] **Step 3: Confirm the new entry landed**

Run:
```bash
python3 -c "import json; d=json.load(open('plugins/hq-core/catalog.json')); e=[s for s in d['skills'] if s['name']=='component-design'][0]; assert e['plugin']=='frontend-toolkit' and e['tags']==['frontend','feature-dev'], e; print('catalog ok')"
```
Expected: `catalog ok`.

- [ ] **Step 4: Confirm the catalog is now fresh (no diff after a second run)**

Run: `python3 scripts/build-catalog.py && git diff --exit-code plugins/hq-core/catalog.json && echo FRESH`
Expected: `FRESH` (exit 0 — the committed-to-be file matches the generator).

- [ ] **Step 5: Commit**

```bash
git add plugins/hq-core/catalog.json
git commit -m "chore(catalog): regenerate for component-design"
```

---

## Task 5: Wire docs — feature-dev pointer, onboarding, README

**Files:**
- Modify: `plugins/hq-core/workflows/feature-dev.md`
- Modify: `plugins/hq-core/skills/onboarding/SKILL.md`
- Modify: `README.md`

- [ ] **Step 1: Add a prose pointer to feature-dev.md**

Do NOT touch the `skills:` frontmatter (gate 4). Add this paragraph immediately after the intro paragraph that ends "...skip to TDD + review." (after line ~11, before the ```mermaid block):

```markdown

> **Building UI?** The optional `frontend-toolkit` skills (`component-design`,
> `state-management`, `styling-systems`, `data-fetching`, `forms-and-validation`,
> `accessibility-audit`, `frontend-performance`, `frontend-testing`, and the
> React Native trio) slot into steps 5–7 — reach for them by concern during build
> and review.
```

- [ ] **Step 2: Verify the workflow check still passes**

Run: `python3 scripts/check-workflows.py`
Expected: `workflow playbooks ok`. (It reads only the `skills:` frontmatter, which we did not change. If it fails with "references unknown skill", you edited frontmatter by mistake — revert that.)

- [ ] **Step 3: Add frontend-toolkit to the onboarding optional-plugins line**

In `plugins/hq-core/skills/onboarding/SKILL.md`, change the optional-plugins bullet (currently lists `codebase-toolkit`, `chatbot-toolkit`, `dispatch-kit` ... `fun`) to include `frontend-toolkit`:

Old:
```markdown
- Optional plugins add more, installed on demand: `codebase-toolkit`,
  `chatbot-toolkit`, `dispatch-kit` (dispatch autonomous workers into git
  worktrees — the SDD pipeline's durable-build mode), and `fun`.
```
New:
```markdown
- Optional plugins add more, installed on demand: `codebase-toolkit`,
  `chatbot-toolkit`, `frontend-toolkit` (React-family web + React Native craft
  skills), `dispatch-kit` (dispatch autonomous workers into git worktrees — the
  SDD pipeline's durable-build mode), and `fun`.
```

- [ ] **Step 4: Add frontend-toolkit to the README plugin list**

In `README.md`, add a bullet immediately after the `chatbot-toolkit` bullet (the one ending "messaging bot (WhatsApp + Instagram)."):

```markdown
- **`frontend-toolkit`** (optional) — cross-cutting frontend craft for
  React-family web + React Native: `component-design`, `state-management`,
  `styling-systems`, `data-fetching`, `forms-and-validation`,
  `animation-and-motion`, `accessibility-audit`, `frontend-performance`,
  `frontend-testing`, `mobile-navigation`, `touch-interaction`,
  `native-performance`.
```

- [ ] **Step 5: Commit**

```bash
git add plugins/hq-core/workflows/feature-dev.md plugins/hq-core/skills/onboarding/SKILL.md README.md
git commit -m "docs(frontend-toolkit): pointer in feature-dev, list in onboarding + README"
```

---

## Task 6: CHANGELOG + full green verification

**Files:**
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Add an Unreleased entry**

In `CHANGELOG.md`, under `## [Unreleased]`, add a new section above the existing `### Added — map-the-codebase` block:

```markdown
### Added — frontend-toolkit (skeleton + component-design exemplar)
- New optional plugin `plugins/frontend-toolkit/` — cross-cutting frontend craft
  skills for React-family web + React Native. Registered in `marketplace.json`.
- First skill `component-design` (`SKILL.md` + `references/{checklist,snippets,
  pitfalls}.md`), tagged `[frontend, feature-dev]`. Snippets grounded via Context7;
  version targets React 19 + current React Native.
- New taxonomy vocab tags `frontend` and `perf`; catalog regenerated.
- `feature-dev.md` gains a prose pointer to the frontend skills; `onboarding` and
  `README.md` list `frontend-toolkit` among the optional plugins.
- Establishes the exemplar shape for the remaining 11 skills (issues #27–#37).
```

- [ ] **Step 2: Run the full local CI gate**

Run:
```bash
python3 -c "import yaml" || pip install pyyaml
python3 scripts/build-catalog.py && \
git diff --exit-code plugins/hq-core/catalog.json && \
python3 scripts/check-workflows.py && \
for f in .claude-plugin/marketplace.json plugins/*/.claude-plugin/plugin.json; do python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$f"; done && \
while IFS= read -r f; do head -n1 "$f" | grep -qx -- '---' || { echo "BAD frontmatter: $f"; exit 1; }; done < <(find plugins -name SKILL.md) && \
echo "ALL GREEN"
```
Expected: ends with `ALL GREEN`. Any failure line names the offending file — fix and re-run.

- [ ] **Step 3: Commit**

```bash
git add CHANGELOG.md
git commit -m "docs(changelog): note frontend-toolkit skeleton + component-design"
```

- [ ] **Step 4: Push and open the PR**

```bash
git push -u origin HEAD
gh pr create --title "feat(frontend-toolkit): walking skeleton + component-design exemplar" \
  --body "Implements #26. Stands up the frontend-toolkit plugin with the component-design exemplar and all hub wiring (marketplace, taxonomy vocab + mapping, regenerated catalog, feature-dev pointer, onboarding + README, CHANGELOG). Establishes the pattern for #27–#37.

Touches core-locked files (taxonomy.yml vocab, feature-dev.md) — needs core-group review.

Closes #26."
```
Expected: PR URL printed. Note in the PR that it touches core-locked files and needs core-group review.

---

## Self-review against the spec (issue #26)

- **Plugin skeleton + plugin.json** → Task 1 ✓
- **marketplace.json entry** → Task 1 ✓
- **vocab += frontend, perf** → Task 2 ✓
- **component-design registered `[frontend, feature-dev]`** → Task 2 ✓
- **No existing skills retagged** → Task 2 only adds one line; verified by the catalog diff being additive ✓
- **component-design SKILL.md + 3 references** → Task 3 ✓
- **Context7-grounded snippets + explicit version targets** → Task 3 Step 1 (grounding) + SKILL.md version-targets line + snippets.md header ✓
- **feature-dev.md pointer (no new playbook, prose only)** → Task 5 Step 1–2 ✓
- **onboarding + README list it** → Task 5 Steps 3–4 ✓
- **CHANGELOG entry** → Task 6 Step 1 ✓
- **catalog regenerated, not hand-edited** → Task 4 ✓
- **hq CI green (all four gates)** → Task 6 Step 2 ✓

No placeholders in executable steps. The only intentionally-templated content is the snippet code in `snippets.md`, which must be filled from Context7 at author time (Task 3 Step 1/4) — this is a grounding requirement from the PRD, not a plan placeholder, and Step 4's structure makes the contract explicit.
