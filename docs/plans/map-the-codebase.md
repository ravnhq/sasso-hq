# Plan: Wire graphify into hq as codebase-mapping infrastructure

Integrate [graphify](https://github.com/safishamsi/graphify) (MIT, © 2026 Safi
Shamsi) into hq so the org's agents reason over a real structural map of a repo —
not by recommending graphify as a tool, but by making a code graph *infrastructure*
that an hq skill builds and another hq skill consumes.

## Shape (decided)

graphify becomes a silent, offline, code-only CLI backend. A new home skill
`map-the-codebase` (in `codebase-toolkit`) builds the graph; `improve-codebase-architecture`
(ICA) is the first consumer, grounding its deletion-test in real structure. Loose
coupling via a repo artifact — ICA still works with no graph, no graphify installed.

## Decisions

| # | Branch | Decision |
|---|--------|----------|
| 1 | Integration shape | **C** — graphify is infrastructure hq agents lean on, not just a recommended tool |
| 2 | Home + first consumer | New home skill **`map-the-codebase`** builds the graph; **ICA** is the first consumer |
| 3 | Host plugin | **`codebase-toolkit`** (co-located with ICA; artifacts live in the user repo, so no cross-plugin file refs) |
| 4 | Install/invocation | **Detect-and-offer**: check `graphify` on PATH; offer `uv tool install graphifyy`, wait. Build **code-only / offline** — no media extras, no API key, no cost |
| 5 | Coupling | **Loose** — ICA detects `graphify-out/graph.json`; absent ⇒ offer `map-the-codebase` ⇒ else fall back to today's organic Explore |
| 6 | Consumption mechanism | **`GRAPH_REPORT.md` for orientation + `jq`/`grep` over `graph.json`** for targeted structural signals. No MCP server, no NL query, no raw-JSON dump |
| 7 | Commit policy | **Gitignored / ephemeral** — `map-the-codebase` adds `graphify-out/` to `.gitignore`; the graph is a local cache |
| 8 | Staleness | **Cheap mtime/dirty check + offer** — stale if `graph.json` older than newest tracked source or `git status` dirty; surface + offer rebuild; default proceed-with-caveat |
| 9 | Skill name + surface | **`map-the-codebase`**, tag `[refactor]`, 4-step surface (detect/offer-install → offline build → ensure gitignore → report). Single responsibility: produce/refresh the map |
| 10 | ICA edit | **Additive insert in Explore + new `GRAPH-EVIDENCE.md`** (progressive disclosure). ICA's philosophy/deletion-test/report format untouched; graph *informs*, never replaces, judgment |
| 11 | Attribution | **Lightweight, honestly framed** — in-skill link + new "External tools driven (not vendored)" subsection in `ATTRIBUTIONS.md`. No pasted MIT block (we don't redistribute) |
| 12 | Workflow playbook | **Add optional step 1.5 to `refactor.md`** (`map-the-codebase` before ICA). Marked optional to preserve graceful degradation |
| 13 | Verification | **Smoke-build first, as a hard prerequisite** — recipes are written *against the real `graph.json` schema*, never invented. Pin graphify major version |
| 14 | Test repos | **hq** for schema + mechanics (markdown-heavy ⇒ thin but schema-complete graph); **`../oc-chatbot-poc`** (31 `.py` files) for signal richness |
| 15 | IDE-skill install | **CLI only** — `uv tool install graphifyy` and drive `graphify extract .`. **Never** run `graphify install` (would inject a competing `/graphify` skill). Note this in the skill so no one re-adds it |

## graphify facts that shaped this

- **Code extraction is fully offline** — tree-sitter AST, no API call, no key, nothing
  leaves the machine. API keys are only for docs/media (PDF/video/image), which we
  scope out entirely.
- `graphify extract .` → `graphify-out/{graph.json, GRAPH_REPORT.md, graph.html}`.
- **Structural traversal over `graph.json` is offline** (`get_neighbors`, `shortest_path`,
  etc.); only `graphify query` (natural language) needs a key — we don't use it.
- `graph.json` is portable (relative-path keys), "safe to commit" — but we gitignore it.
- License: **MIT**. We drive the installed CLI; we do not vendor its source.

## Graph signal → ICA vocabulary (goes in `GRAPH-EVIDENCE.md`)

Recipes authored **after** inspecting the real schema (see Build order). Intended mapping:

- high **fan-in** node → candidate *earning its keep* (deletion test "concentrates complexity")
- wide interface / thin implementation → **shallow** module
- dense edges between two modules → leaky **seam** / tight coupling
- pass-through node (1 in, 1 out) → deletion-test pass-through

## Change set

**`codebase-toolkit` (open-PR, normal review):**
- `plugins/codebase-toolkit/skills/map-the-codebase/SKILL.md` — new home skill (4-step surface)
- `plugins/codebase-toolkit/skills/improve-codebase-architecture/SKILL.md` — additive Explore insert
- `plugins/codebase-toolkit/skills/improve-codebase-architecture/GRAPH-EVIDENCE.md` — new; `jq` recipes vs real schema
- `plugins/codebase-toolkit/.claude-plugin/plugin.json` — description mentions codebase mapping

**`hq-core` (CODEOWNERS-locked — needs core-group review):**
- `plugins/hq-core/taxonomy.yml` — add `map-the-codebase: [refactor]`
- `plugins/hq-core/workflows/refactor.md` — optional step 1.5 (Mermaid + table + `skills:` frontmatter)
- `plugins/hq-core/catalog.json` — regenerated by pre-commit/CI (not hand-edited)

**Repo root:**
- `ATTRIBUTIONS.md` — new "External tools driven (not vendored)" subsection
- `CHANGELOG.md` — entry
- `README.md` — (optional) mention `map-the-codebase` under codebase-toolkit

## Build order (verification-gated)

1. **Smoke-build for schema (hard prerequisite).** `uv tool install graphifyy`; run
   `graphify extract .` in hq; inspect the real `graph.json` node/edge schema. *Do not
   write any `jq` before this.* Pin the observed graphify major version.
2. **Author `GRAPH-EVIDENCE.md`** recipes against the real schema.
3. **Signal validation.** Run `graphify extract .` in `../oc-chatbot-poc`; confirm the
   recipes produce non-trivial, sane output (real high-fan-in / coupled modules light up).
   Correct recipes as needed.
4. **Write `map-the-codebase` SKILL.md** (detect/offer-install CLI only, offline build,
   gitignore, report).
5. **Wire ICA** — additive Explore insert (detect → fresh? → offer build → else fall back).
6. **End-to-end dry run** in `../oc-chatbot-poc`: `map-the-codebase` → ICA picks up the
   graph → produces a sane architecture report.
7. **Mechanical/CI:** taxonomy, regen catalog (pre-commit), refactor.md, ATTRIBUTIONS,
   CHANGELOG, plugin.json, README. Run hq CI (schema/frontmatter/tags/catalog-freshness/
   no-dangling-refs) green.
8. **PR(s).** Core-locked files (`taxonomy.yml`, `refactor.md`, regenerated `catalog.json`)
   need core-group review.

## Risks / open caveats

- **Schema coupling.** Recipes depend on graphify's `graph.json` shape; a major-version
  bump can rot them. Mitigation: version pin + recipes written defensively against missing
  fields. CI is static and *cannot* catch a recipe referencing a dropped field — only the
  smoke test does.
- **Thin graph on doc-heavy repos** (e.g. hq itself). Expected; that's why signal validation
  runs on `oc-chatbot-poc`, not hq.
- **graphify is a single-maintainer external dep.** Acceptable for an optional, offline,
  gracefully-degrading enhancement; ICA never hard-depends on it.

## Out of scope (deliberately deferred)

- Media/docs extraction, API keys, multi-LLM backends, `graphify query` (NL).
  - **Revisit later:** an API key unlocks richer extraction — docs/media nodes and
    `graphify query` (NL) — which could yield a denser, more useful graph for ICA and
    future consumers. Evaluate once the offline, code-only baseline proves its value:
    weigh the result quality gain against the added cost, key management, and the
    "fully offline / nothing leaves the machine" guarantee we'd be relaxing.
- MCP-server consumption (`python -m graphify.serve`) — reserved for a future richer skill
  (`graphify-prs`, interactive querying).
- Committing the graph / CI-maintained shared org graph — only if a real shared-infra need appears.
- Promoting to a standalone `graph-toolkit` plugin — only when a second consumer or sibling
  skill appears (SPEC decision #19 discipline).
- Other consumers (`onboarding`, SDD pipeline) — only after ICA proves the value.
