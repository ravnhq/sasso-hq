# `hq` — Org Agent Hub: Design Spec

One private GitHub monorepo unifying agent skills, Claude Code plugins, and
workflow playbooks. Engineers consume skills via Claude Code's native plugin
marketplace — **no cloning**.

## Core decisions

| #  | Decision        | Choice |
|----|-----------------|--------|
| 1  | Distribution    | Claude Code native plugin marketplace; Claude Code only |
| 2  | Granularity     | Mandatory `hq-core` + optional plugins |
| 3  | Diagrams        | Mermaid, human reference only |
| 4  | Workflows       | Playbooks (markdown + Mermaid) = recommended skill *combinations* per task-type; one canonical `.md` per workflow |
| 5  | Catalog         | CI-generated `catalog.json` from frontmatter; `recommend-workflow` advises + auto-installs on accept |
| 6  | Repo shape      | Monorepo |
| 7  | Release         | Rolling `main`, protected, CI-gated (plugins omit `version` so every commit ships) |
| 8  | Visibility      | Private; SSH auth |
| 9  | Contribution    | Open PRs + CODEOWNERS + 1 review + CI; `hq-core` & `taxonomy.yml` locked to core group |
| 10 | Seed            | Curate existing; vendor mattpocock (MIT), reference superpowers |
| 11 | Onboarding      | 2-line README → install `hq-core` → `onboarding` skill drives the rest; onboarding sets `GITHUB_TOKEN` so rolling-main auto-updates work |
| 12 | Matching        | Locked task-tag vocab + curated playbooks + LLM bridge. **Refinement:** vocab AND skill→tag assignments live in one core-owned `taxonomy.yml` (not per-skill frontmatter) — keeps vendored skills pristine and forces deliberate placement of every new skill |
| 13 | Layout          | Self-contained `hq-core` (workflows/catalog/taxonomy ship *inside* it — required by plugin cache isolation) |
| 14 | CI              | Schema + frontmatter + tag-enforcement + no-dangling-refs + catalog-freshness; catalog committed, pre-commit regenerates |
| 16 | Suites          | mattpocock vendored (primary); superpowers referenced |
| 17 | Overlap         | superpowers wins `tdd` + `systematic-debugging`; mattpocock supplies the rest |
| 18 | Tracker         | GitHub Issues, current working repo, configurable hq-core setting |
| 19 | Domain plugins  | Deferred until a real domain skill exists |

## Skill suites

**Vendored (mattpocock, MIT — preserve attribution):**
`grill-me`, `grill-with-docs`, `to-prd`, `to-issues`, `handoff`, `write-a-skill`,
`triage`, `improve-codebase-architecture`, `zoom-out`, `prototype`.
Drop `setup-matt-pocock-skills`.

**Referenced (superpowers, bootstrap-installed dependency):**
`tdd`, `systematic-debugging`, `writing-plans`, `executing-plans`,
`subagent-driven-development`, `dispatching-parallel-agents`, `requesting-code-review`.

**Composed SDD pipeline:**
`grill-me → to-prd → to-issues` (spec/contract, mattpocock) →
`writing-plans → executing-plans / subagent-driven-development` (build, superpowers) →
`tdd` (discipline, superpowers) → `requesting-code-review`.
`sdd-kit` orchestrates this chain with house gates.

## Plugins

- **`hq-core`** (mandatory, core-group owned): `onboarding`, `recommend-workflow`,
  `code-review` (wraps superpowers `requesting-code-review` + house standards),
  `commit-conventions`, `sdd-kit`, `handoff`, `grill-me`, `grill-with-docs`,
  `to-prd`, `to-issues`. Ships self-contained: `workflows/`, `catalog.json`, `taxonomy.yml`.
- **`codebase-toolkit`** (optional): `improve-codebase-architecture`, `write-a-skill`,
  `triage`, `zoom-out`, `prototype`.
- **`fun`** (optional): `caveman`.

## Layout

```
hq/
├── .claude-plugin/marketplace.json
├── plugins/
│   ├── hq-core/
│   │   ├── .claude-plugin/plugin.json
│   │   ├── skills/{onboarding,recommend-workflow,code-review,commit-conventions,
│   │   │           sdd-kit,handoff,grill-me,grill-with-docs,to-prd,to-issues}/SKILL.md
│   │   ├── workflows/{feature-dev,bugfix,code-review}.md
│   │   ├── catalog.json          # CI-generated, committed
│   │   └── taxonomy.yml          # locked vocab
│   ├── codebase-toolkit/
│   └── fun/
├── scripts/build-catalog.py
├── .github/{CODEOWNERS,workflows/ci.yml}
├── CHANGELOG.md
└── README.md                     # marketplace add + install hq-core
```

## Consumption (the headline goal)

```shell
/plugin marketplace add ravnhq/sasso-hq      # SSH-authed; private repo
/plugin install hq-core@hq                 # onboarding skill takes over
```

Skills are namespaced: `/hq-core:onboarding`. Plugins are copied to a cache on
install — they **cannot** reference files outside their own directory, which is
why workflows/catalog/taxonomy live inside `hq-core`.

### Authentication

The marketplace has no auth of its own — it delegates to git.
- **Manual add/update**: uses existing git credential helpers. SSH works when the
  host is in `known_hosts` and the key is loaded in `ssh-agent` (CC suppresses
  interactive prompts, so a passphrase key not in the agent fails silently).
- **Startup auto-update**: runs without credential helpers. For a private repo it
  needs `GITHUB_TOKEN`/`GH_TOKEN` in the environment, else it silently can't fetch
  and the engineer drifts stale.

**Implication for rolling-main (Q7):** "everyone always current" only holds if
`GITHUB_TOKEN` is set. The `onboarding` skill (Phase 2) sets it up; without it,
engineers must run `/plugin marketplace update` manually over SSH.

GitHub Actions auto-provides `GITHUB_TOKEN` for same-org repos, so CI needs no token setup.

## Build phasing

1. **Skeleton + bootstrap proof** — repo, `marketplace.json`, `hq-core` `plugin.json`,
   minimal `onboarding` skill, README two-liner, CI scaffold. Verify marketplace-add
   + install loads the skill from a *separate* working dir. De-risks the headline goal.
2. **hq-core content** — vendor mattpocock, write orchestrators (`sdd-kit`,
   `code-review`, `commit-conventions`), wire superpowers dependency, `taxonomy.yml`,
   catalog generator + pre-commit + CI checks. `onboarding` sets up `GITHUB_TOKEN`
   for private-repo auto-update.
3. **Workflows** — `feature-dev.md`, `bugfix.md`; onboarding runs them interactively.
4. **Optional plugins** — `codebase-toolkit`, `fun`.

## Deferred (not blockers)

- Naming conventions — default: kebab-case skills, `<domain>-toolkit` plugins.
- Public/generic split — only if open-sourcing later.
- Multi-repo split — only when a sub-team needs release independence.
