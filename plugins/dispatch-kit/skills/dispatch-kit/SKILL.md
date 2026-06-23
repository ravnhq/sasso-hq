---
name: dispatch-kit
description: Use when you want to hand work to autonomous Claude workers instead of doing it inline — files an issue and spawns a worker in an isolated git worktree, then tracks and reaps it. The runtime tail of the SDD pipeline. Commands - /dispatch /adopt /status /reap /pool.
---

# Dispatch Kit — autonomous worker orchestration

Turn "here are issues" into "here are running workers." From inside a session you
file an issue and dispatch a **separate, durable** Claude Code worker that
implements it in an isolated git worktree, opens one PR, and stops. You review and
merge. This is the execution-dispatch layer the SDD pipeline stops short of —
`to-prd`/`to-issues` produce the spec; dispatch-kit runs it.

## Model

- **Issues + PRs** both live in `$ISSUES_REPO` (the current repo by default).
- A **slot** is a git worktree of this repo at `../<repo>-wt-<id>`, parked on
  `wt/<id>`. All slots share one `.git` object store, so a single fetch updates
  `origin/<default>` for every slot.
- **Dispatch** files/adopts an issue, resets an idle slot to `task/<N>` off the
  default branch, renders the worker prompt, and spawns a worker via the configured
  **dispatcher**.
- A **worker** implements the issue test-first, runs the green-light check, opens
  **one PR**, comments on the issue, and **stops**. It never merges.
- The **human** reviews + merges the PR (which closes the issue), then runs `/reap`
  to park the freed slot.

It's opt-in via the commands; normal direct work in the repo is unaffected.

## Commands

| Want to… | Use |
|---|---|
| Start a task from a one-liner | `/dispatch "<text>"` |
| Start a worker on an existing issue | `/adopt <issue#>` |
| See pool + PRs + issues | `/status` |
| Free slots for closed issues | `/reap` |
| Add/remove slots | `/pool list \| add <N> \| remove <id>` |

## Bootstrap (one-time, per repo)

```bash
# Optional config (else sensible defaults; ISSUES_REPO falls back to the gh origin):
mkdir -p .claude/brain && cp "${CLAUDE_PLUGIN_ROOT}/templates/config.sh.example" .claude/brain/config.sh

"${CLAUDE_PLUGIN_ROOT}/scripts/init-pool.sh" 3   # create 3 worktree slots
"${CLAUDE_PLUGIN_ROOT}/scripts/status.sh"        # inspect
```

`state/` under `.claude/brain` is auto-gitignored; `config.sh` is committable.

## Dispatchers (pluggable)

`DISPATCHER` (env or `config.sh`) selects what spawns the durable worker workspace:

- **`cmux`** (default) — a watchable cmux workspace per worker.
- **`tmux`** — a detached tmux session (`tmux attach -t <name>`). Portable fallback.
- **`plain`** — a backgrounded `claude` via `nohup`, PID + log in the slot's `.claude/`.

Each is a small file under `scripts/dispatchers/` defining `dispatcher_require`,
`dispatcher_spawn`, and `dispatcher_close` — add your own backend by dropping in
another file.

## Worker effort knob

`WORKER_EFFORT` (default `max`) encodes a real CLI trade-off:

- **`max`** — top raw reasoning, but multi-agent Workflow orchestration is OFF (the
  CLI gates orchestration on resolved-effort `xhigh`, and `--effort` wins the resolver).
- **`ultracode`** — expands to `--effort xhigh --settings '{"ultracode":true}'`:
  orchestration ON, slightly lower raw effort.
- any other value passes through as `--effort <value>`.

## Config knobs (`.claude/brain/config.sh`, all env-overridable)

`ISSUES_REPO`, `WT_PREFIX`, `WT_BASE`, `WORKER_MODEL`, `WORKER_EFFORT`,
`GREEN_LIGHT_CMD`, `DISPATCHER`. Use `: "${VAR:=value}"` form so env still wins.

## Dispatch flow you MUST follow

1. Take the one-liner. For non-trivial work, run `to-prd` → `to-issues`; for trivial
   work, draft inline from `templates/issue.md`.
2. **Show the draft and WAIT for approval.** This is the review gate — don't file
   until the user okays it.
3. On approval, write the body to a temp file and run `scripts/dispatch.sh
   --create-issue --title "<t>" --body-file <f>` (or `--adopt <issue#>`).
4. Report: issue #, slot id, branch, dispatcher, workspace name.

If dispatch reports "no idle slots", offer `/pool add <N>`.

## Source of truth

- `state/pool.json` (gitignored) — slot allocation.
- GitHub — issue/PR state. `/reap` reconciles the two by closing-issue.
