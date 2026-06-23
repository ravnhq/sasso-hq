# Changelog

## [Unreleased]

### Changed — sdd-kit: reach for frontend-toolkit on UI work
- The `sdd-kit` skill now carries a **"Building UI?"** callout naming the optional
  `frontend-toolkit` skills to pull in by concern during build and review (steps
  5–7), mirroring the pointer already in the `feature-dev` workflow. Spec-driven
  frontend features now route through the craft skills instead of generic build.

### Changed — frontend-toolkit: visual-companion guidance (#53)
- The six visual-output skills (`component-design`, `styling-systems`,
  `animation-and-motion`, `accessibility-audit`, `mobile-navigation`,
  `touch-interaction`) now carry a **"show visual choices, don't describe them"**
  principle plus a `Related` pointer to the superpowers brainstorming **visual
  companion** (`superpowers:brainstorming`). The nudge: when a decision is genuinely
  visual (layout, palette, motion, navigator tree…), render the options for the user
  via the companion and let them click, instead of asking in prose.

### Added — frontend-toolkit: devtools-debugging skill (#51)
- New craft skill `devtools-debugging` (`SKILL.md` + `references/{setup,snippets,
  pitfalls,checklist}.md`), tagged `[frontend, debugging]` — the first frontend
  skill to use the existing `debugging` vocab tag. Registered in `taxonomy.yml` and
  reflected in the regenerated catalog.
- Teaches debugging web issues against a **live Chrome via the Chrome DevTools MCP**
  instead of guessing from source: a reproduce-first loop and four MCP-tool
  workflows (console errors, network requests, DOM/layout, performance), opening
  with a project-scoped MCP setup runbook (`--isolated` headed default; user-level
  and `--headless` variants). Defers debugging discipline to
  `superpowers:systematic-debugging`, the perf *fix* to `frontend-performance`, and
  regression capture to `frontend-testing`. Web-only by construction (RN pointed at
  RN DevTools / Flipper).
- MCP config and tool sequences grounded via Context7 against
  `/chromedevtools/chrome-devtools-mcp` (current server; `chrome-devtools-mcp@latest`,
  Chrome stable, Node ≥22).

### Added — frontend-toolkit: 11 craft skills (roster complete)
- Eleven cross-cutting skills replicating the `component-design` exemplar shape (#26),
  each `SKILL.md` + `references/{checklist,snippets,pitfalls}.md`, registered in
  `taxonomy.yml` and reflected in the regenerated catalog (issues #27–#37):
  - **Web:** `state-management`, `styling-systems`, `data-fetching`,
    `forms-and-validation`, `animation-and-motion`, `accessibility-audit`
    (`[frontend, review]`, ships a WCAG 2.2 checklist), `frontend-performance`
    (`[frontend, perf]`), `frontend-testing` (`[frontend, testing]`).
  - **React Native:** `mobile-navigation`, `touch-interaction`, `native-performance`
    (`[frontend, perf]`). Remaining web skills are `[frontend, feature-dev]`.
- New taxonomy vocab tags `frontend` and `perf` (added with the skeleton).
- Every snippet grounded via Context7 against current library docs (React 19,
  React Native 0.81, plus TanStack Query v5, Zustand v5, Zod 4, React Hook Form 7,
  Reanimated 4, React Navigation 7, web-vitals v4, Testing Library / MSW v2, etc.)
  and version-pinned per skill. Each PR passed hq CI and an independent code review
  verifying snippet correctness against Context7.

### Added — frontend-toolkit (skeleton + component-design exemplar)
- New optional plugin `plugins/frontend-toolkit/` — cross-cutting frontend craft
  skills for React-family web + React Native. Registered in `marketplace.json`.
- First skill `component-design` (`SKILL.md` + `references/{checklist,snippets,
  pitfalls}.md`), tagged `[frontend, feature-dev]`. Snippets grounded via Context7
  against `/reactjs/react.dev` (React 19) and `/facebook/react-native` (0.81).
- New taxonomy vocab tags `frontend` and `perf`; catalog regenerated.
- `feature-dev.md` gains a prose pointer to the frontend skills; `onboarding` and
  `README.md` list `frontend-toolkit` among the optional plugins.
- Establishes the exemplar shape for the remaining 11 skills (issues #27–#37).

### Added — map-the-codebase (offline code-graph infrastructure)
- New skill `plugins/codebase-toolkit/skills/map-the-codebase`, tag `[refactor]`.
  Drives [graphify](https://github.com/safishamsi/graphify) (the `graphifyy` CLI,
  installed via `uv tool install graphifyy`) as an **offline, code-only** backend
  — tree-sitter AST + local community detection, no API key, no network, no cost
  — producing `graphify-out/{graph.json, GRAPH_REPORT.md}` as a gitignored local
  cache. Offline is enforced by excluding doc/paper/image files (which graphify
  would otherwise route through an LLM); `cluster-only --no-label --no-viz` writes
  the orientation report without LLM community naming.
- `improve-codebase-architecture` now optionally grounds its Explore step in the
  graph: a new `GRAPH-EVIDENCE.md` provides schema-defensive `jq` recipes mapping
  structural signals (high fan-in → earning its keep, wide-surface/low-inbound →
  shallow, 1-in/1-out → pass-through, dense cross-file edges → leaky seam) onto
  the skill's deletion-test vocabulary. The graph *informs* judgment, never
  replaces it; ICA still works with no graph and no graphify installed.
- Wired into the org: `taxonomy.yml` (`map-the-codebase: [refactor]`), catalog
  regenerated, and `refactor.md` gains an optional step 1.5 (map before ICA).
- Driven, not vendored: graphify's source isn't bundled. See `ATTRIBUTIONS.md`.

### Added — dispatch-kit (autonomous worker orchestration)
- New optional plugin `plugins/dispatch-kit`, adapted and generic-ified from the
  abyssinia-sap-demo repo-local "brain". Lets a Claude session file an issue and
  dispatch a separate, durable Claude worker into an isolated git worktree, which
  implements it test-first, opens one PR, comments on the issue, and stops — the
  human reviews and merges. It is the runtime execution tail of the SDD pipeline
  (`to-prd`/`to-issues` produce the spec; dispatch-kit runs it).
- Commands `/dispatch`, `/adopt`, `/status`, `/reap`, `/pool` (in `commands/`,
  referencing bundled scripts via `${CLAUDE_PLUGIN_ROOT}`). `/dispatch` wires to the
  existing `to-prd`/`to-issues` skills for spec drafting rather than duplicating them.
- Worktree slot pool: `init-pool.sh`, `pool.sh`, `dispatch.sh`, `status.sh`,
  `reap.sh`, plus `lib.sh`. Unlike the repo-local original, the scripts live in the
  plugin cache and resolve the **target repo from the caller's cwd**, so one install
  drives any repo. State lives at `<repo>/.claude/brain/state/pool.json` (auto-
  gitignored); `config.sh` is committable.
- Pluggable dispatcher backend (`scripts/dispatchers/`): `cmux` (default, watchable
  workspace), `tmux` (detached session), `plain` (`nohup` background `claude`). Each
  defines `dispatcher_require` / `dispatcher_spawn` / `dispatcher_close`.
- `WORKER_EFFORT` knob encoding the CLI trade-off: `max` (top raw effort, no
  multi-agent orchestration) vs `ultracode` (`--effort xhigh` + `{"ultracode":true}`,
  orchestration on). Per-repo config via `.claude/brain/config.sh` (env-overridable):
  `ISSUES_REPO`, `WT_PREFIX`, `WT_BASE`, `WORKER_MODEL`, `WORKER_EFFORT`,
  `GREEN_LIGHT_CMD`, `DISPATCHER`.
- Worker prompt rendering uses bash literal substitution (not `sed`), so green-light
  commands containing `&&` / `|` render correctly. Registered in `marketplace.json`.

### Added — chatbot-toolkit (README listing, issue #20)
- README's "What's here" now lists `chatbot-toolkit` (optional) — a full-stack,
  Claude-powered Meta messaging bot (WhatsApp + Instagram) — matching its
  `marketplace.json` description. The plugin shipped in #19 but the README
  listing had drifted.

### Added — chatbot-toolkit (Instagram as second channel, issue #8)
- `InstagramChannel` in `reference-app/app/channel.py`, implementing the same
  `Channel` protocol as `WhatsAppChannel` with no change to the webhook
  orchestration. Proves the channel abstraction holds: both channels now subclass
  a new `MetaChannel` base that owns the parts Meta makes identical — the verify
  handshake, the `X-Hub-Signature-256` check, and the authenticated Graph POST —
  so each channel only overrides `parse` and `send`.
- Instagram inbound parsing for the Messenger-style `object: "instagram"` →
  `entry[].messaging[]` payload (vs WhatsApp's `entry[].changes[].value.messages[]`),
  normalizing to the same `InboundMessage`; echo events (`message.is_echo`) are
  skipped so the bot never replies to itself.
- Instagram outbound send via the Graph client to `/{ig_id}/messages` with the
  `{recipient, message}` envelope (no `messaging_product` field).
- `CHANNEL` env var (default `whatsapp`) selects the channel at startup via
  `build_channel` in `app/main.py`; `INSTAGRAM_ACCESS_TOKEN` / `INSTAGRAM_ID`
  added to `config.py` and `.env.example`. `META_APP_SECRET` / `META_VERIFY_TOKEN`
  stay shared across both products.
- Captured IG webhook fixtures (`tests/fixtures/instagram_message.json`,
  `instagram_echo.json`) and tests: IG verify/signature/parse/send unit tests, a
  webhook integration test routing an IG payload through the unchanged flow, and
  `build_channel` selection tests (43 reference-app tests pass).
- `meta-messaging` skill gains an Instagram section (payload shape, echo guard,
  send envelope, Facebook-Login vs Instagram-Login Graph hosts) plus
  `references/instagram-messaging.md` (24h DM window + tags, story replies/mentions,
  reactions, login variants). Skill description broadened to cover both channels;
  `catalog.json` regenerated (still 31 entries).

### Added — chatbot-toolkit (build-a-chatbot playbook, issue #10)
- `plugins/hq-core/workflows/build-a-chatbot.md`: the curated workflow playbook
  that makes the chatbot domain discoverable as one cohesive path. Specializes the
  SDD pipeline (`grill-me → to-prd → to-issues`) with the `chatbot-toolkit` skills
  — brain (`bot-brain-basics`/`bot-brain-agent`), `meta-messaging`,
  `bot-session-state`, `scaffold-bot`, `bot-safety`, `deploy-bot` — with
  `testing-bots` applied throughout and `code-review`/`commit-conventions` as the
  merge gate. Includes a Mermaid diagram of the end-to-end path and `skills:`
  frontmatter referencing only catalogued skills, so `recommend-workflow` surfaces
  the whole path when an engineer describes building a WhatsApp/Instagram bot.
  Validated by `scripts/check-workflows.py`. Completes the chatbot-toolkit slices
  (#2–#10).

### Added — chatbot-toolkit (testing-bots, issue #9)
- `testing-bots` skill codifying how the reference app tests itself entirely
  offline: simulating inbound webhooks from captured fixtures
  (`tests/fixtures/*.json`), reproducing Meta's `X-Hub-Signature-256` HMAC to
  exercise accept/reject paths, mocking Graph via `httpx.MockTransport` and
  Anthropic via an injected fake client / `StubBrain`, and asserting through the
  HTTP boundary with FastAPI's `TestClient`. Documents the injectable seams
  (`create_app` factory, `InMemorySessionStore`, mockable `Channel`/`Brain`,
  network-free `Guardrails`), the integration-over-unit preference with the
  webhook integration test as the house end-to-end example, the
  `asyncio.run`-not-`pytest-asyncio` convention, and the `pytest-postgresql`
  temp-database approach for the durable store. Doc-only slice — no reference-app
  code change. Registered in `taxonomy.yml` (`[testing]`) and `catalog.json`.

### Added — chatbot-toolkit (deploy-bot + Dockerization, issue #7)
- `reference-app/Dockerfile`: multi-stage build (uv, `python:3.12-slim`) that
  installs deps with `uv sync --locked --no-dev`, ships only the non-editable
  venv, runs as a non-root user, and starts uvicorn bound to `$PORT` (fallback
  8000) — so a container PaaS image runs unchanged. Added `.dockerignore`
  (excludes `.venv` / `.env` / caches) so secrets and the host venv never enter
  the build context. Verified: image builds and the running container serves the
  `/webhook` verify handshake (200).
- `deploy-bot` skill covering the dev tunnel workflow (cloudflared / ngrok) for
  receiving Meta webhooks on a laptop and container-PaaS deploy (Fly / Railway /
  Render) with public HTTPS, per-platform secret configuration, and a post-deploy
  verify-handshake check. Registered in `taxonomy.yml` (`[infra]`) and
  `catalog.json`.

### Added — chatbot-toolkit (Postgres session state, issue #3)
- `PostgresSessionStore` (asyncpg, raw SQL) in the reference app's
  `app/session.py`: a durable `SessionStore` keyed by `conversation_id` with a
  monotonic `seq`, so history survives restarts and stays isolated per
  conversation. Pool is created lazily on first use (schema ensured via
  `CREATE TABLE IF NOT EXISTS`) so `create_default_app` stays synchronous.
- `create_default_app` now wires `PostgresSessionStore(settings.database_url)`;
  `Settings` gains `database_url` (env `DATABASE_URL`), with a local placeholder
  in `.env.example`. `InMemorySessionStore` stays as the test seam.
- Round-trip integration test using `pytest-postgresql` (temp real Postgres via
  the local binaries, no Docker): append-then-get order + conversation isolation.
- `bot-session-state` skill documenting the schema, lazy-pool pattern, webhook
  wiring, and temp-Postgres testing; registered in `taxonomy.yml`
  (`[feature-dev]`) and `catalog.json`.

### Added — chatbot-toolkit (safety guardrails, issue #4)
- Real `HeuristicGuardrails` replacing the no-op seam: deterministic,
  network-free screening. `screen_input` blocks prompt-injection (e.g. "ignore
  previous instructions", "reveal your system prompt", "developer mode") with a
  canned refusal so blocked messages never reach the Brain, and redacts PII
  (email / phone / US SSN / credit-card) so the model only sees `[REDACTED_*]`
  tokens. `screen_output` redacts the same PII leaking from the model. PII
  redaction is a single shared helper used by both methods. `create_default_app`
  now wires `HeuristicGuardrails`; `NoOpGuardrails` stays for tests.
- `bot-safety` skill documenting deterministic input/output screening, the
  canned-response short-circuit, and where an LLM-moderation layer could slot in;
  registered in `taxonomy.yml` (`[security]`) and `catalog.json`.

### Added — chatbot-toolkit (meta-messaging skill, issue #5)
- `meta-messaging` skill documenting the reference app's Meta integration:
  creating a Meta App, the webhook verify handshake (`hub.mode` /
  `hub.verify_token` → `hub.challenge`), `X-Hub-Signature-256` validation
  (raw body, HMAC-SHA256, constant-time compare), and the WhatsApp Graph API
  send client (`v21.0`). WhatsApp section covers the 24-hour window, template
  categories (marketing/utility/authentication), and media; deep payloads in
  `references/whatsapp-window.md` + `references/whatsapp-media.md`.
- Registered in `taxonomy.yml` (`[feature-dev, infra]`) and `catalog.json`.

### Added — chatbot-toolkit (brain teaching skills, issue #6)
- `bot-brain-basics` skill — teaches the raw Anthropic Python SDK behind the
  reference app's `Brain`: `messages.create`, the tool-use loop, streaming, and
  prompt caching. Layers on `reference-app/app/brain.py` (`ClaudeBrain`).
- `bot-brain-agent` skill — teaches the Claude Agent SDK (`claude-agent-sdk`):
  the agent loop, in-process `@tool`s + `create_sdk_mcp_server`, MCP, and context
  management — framed as the recommended upgrade layered behind the same
  `Brain.respond()` interface.
- Both registered in `taxonomy.yml` (`[feature-dev]`) and `catalog.json`; cross-link
  each other.

### Added — chatbot-toolkit (tracer bullet, issue #2)
- New optional plugin `chatbot-toolkit` with a runnable `reference-app/`: a
  full-stack Claude-powered WhatsApp bot (FastAPI webhook → `Channel` /
  `Brain` / `SessionStore` / `Guardrails` deep modules). WhatsApp inbound
  parse + `X-Hub-Signature-256` validation + Graph API send; Claude reply via
  the Anthropic Messages API; in-memory sessions + no-op guardrails as seams.
- `scaffold-bot` skill documenting the reference app; registered in
  `taxonomy.yml` (`[feature-dev]`) and `catalog.json`.
- Marketplace lists `chatbot-toolkit`.

### Added — Phase 4: optional-plugin polish
- `workflows/refactor.md` — refactor playbook chaining `zoom-out` →
  `improve-codebase-architecture` → `tdd` → `writing-plans` → `code-review`,
  tying `codebase-toolkit` into the recommendation system.
- README lists the optional plugins (`codebase-toolkit`, `fun`) and their skills,
  with a pointer to the catalog. Verified both plugins install and load.

### Changed
- `onboarding` now adds a permissions step: merges a `claude plugin` allowlist
  into the working repo's `.claude/settings.json` so the flow runs without
  per-command prompts. Each rule's rationale is documented in the skill (settings
  JSON can't hold comments).
- `onboarding` now sets up the Context7 docs MCP via `npx ctx7 setup --claude`
  (global, OAuth-authenticated) as a dedicated step, with a skip check against
  `claude mcp list`. Notes that a `Skill failed: GitHub API error` is only the
  skill-file fetch hitting rate limits — the MCP is installed regardless — and
  documents fetching the `context7-mcp` skill directly from `raw.githubusercontent.com`.

### Added — Phase 3: workflow playbooks
- `plugins/hq-core/workflows/{feature-dev,bugfix,code-review}.md` — curated
  skill-combination paths with Mermaid diagrams and `skills:` frontmatter
  (validated against the catalog by `check-workflows.py`). Onboarding and
  `recommend-workflow` run these interactively.

### Added — Phase 2: hq-core content
- Vendored mattpocock skills (MIT, see `ATTRIBUTIONS.md`): `grill-me`,
  `grill-with-docs`, `to-prd`, `to-issues`, `handoff` into `hq-core`;
  `improve-codebase-architecture`, `write-a-skill`, `triage`, `zoom-out`,
  `prototype` into new `codebase-toolkit`; `caveman` into new `fun`.
- New orchestrator skills in `hq-core`: full `onboarding` (task-driven +
  `GITHUB_TOKEN` setup + superpowers dependency check), `recommend-workflow`,
  `code-review` (house gates over superpowers `requesting-code-review`),
  `commit-conventions`, `sdd-kit` (orchestrates the SDD pipeline).
- `taxonomy.yml` — locked task-tag vocab + skill→tag assignments + referenced
  external (superpowers) skills.
- `scripts/build-catalog.py` → generates `plugins/hq-core/catalog.json`;
  `scripts/check-workflows.py` validates playbook skill refs.
- CI: catalog-freshness + taxonomy-validity + workflow-ref checks.
- `.pre-commit-config.yaml` regenerates the catalog on skill/taxonomy changes.
- Marketplace now lists `hq-core`, `codebase-toolkit`, `fun`.

### Changed
- README install path corrected to `ravnhq/sasso-hq`.
- SPEC: added Authentication section, `GITHUB_TOKEN` onboarding step, and the
  Q12 refinement (tags in `taxonomy.yml`, not per-skill frontmatter).

### Added — Phase 1: skeleton + bootstrap proof
- `SPEC.md` — full design contract (19 decisions, suites, layout, phasing).
- `.claude-plugin/marketplace.json` — marketplace `hq` listing `hq-core`.
- `plugins/hq-core/` — plugin manifest (no `version`, rolling-main) + minimal
  `onboarding` skill stub to prove the install path loads.
- `README.md` — two-line bootstrap.
- `.github/workflows/ci.yml` — JSON-parse + SKILL.md-frontmatter validation
  (full check set deferred to Phase 2).
- `.github/CODEOWNERS` — `hq-core` + `taxonomy.yml` locked to core group.
