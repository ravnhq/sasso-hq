---
name: onboarding
description: Use when an engineer first installs hq-core or asks how the org's agent setup works. Introduces the hub, grants the permissions the flow needs, ensures auto-updates work, sets up the Context7 docs MCP, asks what they're working on, and recommends + installs the right skills and workflow playbook.
---

# Onboarding

Entry point after installing `hq-core`. Run interactively — one step at a time,
wait for the engineer between steps.

## 1. Orient

Explain briefly:
- `hq-core` is mandatory; it carries onboarding, workflow recommendations,
  code-review standards, commit conventions, and the SDD pipeline.
- Optional plugins add more, installed on demand: `codebase-toolkit`,
  `chatbot-toolkit`, `frontend-toolkit` (React-family web + React Native craft
  skills), `dispatch-kit` (dispatch autonomous workers into git worktrees — the
  SDD pipeline's durable-build mode), and `fun`.
- Skills are namespaced: `/hq-core:<skill>`.

## 2. Smooth out permissions

Onboarding and `recommend-workflow` run `claude plugin` commands. Without
pre-granted permissions each one prompts, which is jarring. Merge the allowlist
below into the working repo's `.claude/settings.json` (create the file/dir if
absent; **preserve any existing keys** — only add missing rules).

`settings.json` is strict JSON and cannot hold comments, so the rationale for
each rule lives in this table, not in the file:

| Rule | Why it's needed |
|------|-----------------|
| `Bash(claude plugin *)` | All onboarding/recommend plugin work: list installed, add the superpowers marketplace, install optional plugins + the dependency, and update for new skills (rolling `main`). |
| `Read(~/.claude/plugins/cache/**)` | `recommend-workflow` reads hq-core's bundled `catalog.json` and playbooks from the install cache, and inspects other installed plugins there while resolving what to recommend. |

Write exactly this (merged into any existing `permissions.allow`):

```json
{
  "permissions": {
    "allow": [
      "Bash(claude plugin *)",
      "Read(~/.claude/plugins/cache/**)"
    ]
  }
}
```

Always write the committed, team-scoped `.claude/settings.json` (don't ask which
scope) with **exactly these two portable rules and nothing else**. Never put a
machine-specific or absolute path in this file — it's shared, and an absolute
path is wrong for every other engineer and leaks a local path.

> **Local-clone dev setups:** if hq-core was installed from a local clone rather
> than `ravnhq/sasso-hq`, recommend-workflow reads from the clone path, not the
> cache. That needs `Read(<clone>/plugins/hq-core/**)` — but it's machine-specific,
> so add it to gitignored `.claude/settings.local.json`, **never** the committed
> team file.

## 3. Enable auto-updates (private repo)

The marketplace is a private repo. Startup auto-updates need a token, or the
engineer silently drifts stale. Ask whether `GITHUB_TOKEN`/`GH_TOKEN` is set; if
not, walk them through it:
1. Create a fine-grained PAT with read access to `ravnhq/sasso-hq` at
   GitHub → Settings → Developer settings → Personal access tokens.
2. Add to their shell config (`~/.zshrc`): `export GITHUB_TOKEN=github_pat_xxx`
3. Reload (`source ~/.zshrc`) and restart Claude Code.

If they decline: auto-update won't work — they must run
`/plugin marketplace update` manually over SSH to get new skills.

## 4. Ensure the SDD dependency

The SDD pipeline (`sdd-kit`) leans on superpowers for `tdd`,
`systematic-debugging`, and plan execution. Check it's installed:

```shell
claude plugin list | grep -q superpowers && echo present || echo missing
```

If missing, offer to install:
```shell
claude plugin marketplace add anthropics/claude-code
claude plugin install superpowers
```

## 5. Set up Context7 docs MCP

Context7 is the org's MCP server for current library and framework docs (see the
Context7 rule). Install it and wire it into Claude Code in one step:

```shell
npx ctx7 setup --claude
```

Skip if `claude mcp list` already shows `context7`.

A `Skill failed: GitHub API error` on `~/.claude/skills/context7-mcp/SKILL.md`
is only the skill-file fetch hitting GitHub API rate limits — the MCP server is
still installed and wired up regardless. Just fetch the skill file directly over
`raw.githubusercontent.com`, which isn't rate-limited the same way:

```shell
mkdir -p ~/.claude/skills/context7-mcp && \
curl -sL https://raw.githubusercontent.com/upstash/context7/master/skills/context7-mcp/SKILL.md \
  -o ~/.claude/skills/context7-mcp/SKILL.md
```

## 6. Task-driven recommendation

Ask: **"What are you working on right now?"** (No roles — everyone's fullstack;
recommend by task, not title.)

Then invoke `recommend-workflow` with their answer. It maps the task to the
right skills + a workflow playbook, and offers to install any optional plugins
needed.

## 7. First playbook

Run the recommended workflow playbook interactively as a guided walkthrough —
"here's step 1, here's the skill it uses, try it." Playbooks live in
`workflows/` inside this plugin.

## Done

The engineer should now know: how to update, what's installed, and which skills
fit their current task. Point them at `/hq-core:recommend-workflow` anytime they
start something new.
