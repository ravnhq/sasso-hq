#!/usr/bin/env bash
# Shared helpers for dispatch-kit. Sourced, not executed directly.
#
# Unlike a repo-local brain, this ships inside a Claude Code plugin, so the
# scripts live in the plugin cache while the STATE (slot pool, worktrees) lives
# in the TARGET repo — resolved from the caller's cwd, not the script location.
#
# Worktree-based: dispatch-kit parks autonomous Claude workers into a pool of
# git worktrees of the target repo. A "slot" is one such worktree; a "dispatcher"
# (cmux | tmux | plain) is what spawns the durable worker session inside it.

# Bash 3.2 compatible (macOS): no mapfile, no associative arrays.

LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"          # .../scripts
TEMPLATES_DIR="${TEMPLATES_DIR:-$LIB_DIR/../templates}"

# The target repo is resolved from the CALLER'S cwd, so the same plugin drives
# whatever repo you invoke it from.
BRAIN_REPO="${BRAIN_REPO:-$(git -C "$PWD" rev-parse --show-toplevel 2>/dev/null || true)}"
if [ -z "$BRAIN_REPO" ]; then
  echo "dispatch-kit: not inside a git repo (cwd=$PWD)" >&2
  exit 1
fi

# Per-repo state + config live under <repo>/.claude/brain.
STATE_BASE="${STATE_BASE:-$BRAIN_REPO/.claude/brain}"
POOL_FILE="$STATE_BASE/state/pool.json"

# Optional per-repo config. Use `: "${VAR:=value}"` form inside it so that
# environment overrides still win over the committed config file.
# shellcheck source=/dev/null
[ -f "$STATE_BASE/config.sh" ] && . "$STATE_BASE/config.sh"

# Defaults (env / config can override). WT_PREFIX derives from the repo name so
# two repos' slots never collide as siblings.
REPO_NAME="$(basename "$BRAIN_REPO")"
WT_BASE="${WT_BASE:-$(dirname "$BRAIN_REPO")}"
WT_PREFIX="${WT_PREFIX:-${REPO_NAME}-wt-}"
WORKER_MODEL="${WORKER_MODEL:-claude-opus-4-8}"

# WORKER_EFFORT encodes the BRAIN.md tradeoff:
#   max       → top raw reasoning, but multi-agent Workflow orchestration OFF
#               (the CLI gates orchestration on resolved-effort xhigh; --effort wins)
#   ultracode → --effort xhigh + {"ultracode":true}: orchestration ON, slightly
#               lower raw effort
# Any other value is passed through verbatim as --effort <value>.
WORKER_EFFORT="${WORKER_EFFORT:-max}"

# Green-light check the worker must pass before opening its PR. Repo-specific;
# override in config.sh. Empty means "no automated gate" (worker notes that).
GREEN_LIGHT_CMD="${GREEN_LIGHT_CMD:-}"

# Issues + PRs both live here. Defaults to the target repo's origin slug.
ISSUES_REPO="${ISSUES_REPO:-$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || true)}"

# Which backend spawns the durable worker workspace.
DISPATCHER="${DISPATCHER:-cmux}"
DISPATCHER_FILE="$LIB_DIR/dispatchers/$DISPATCHER.sh"
[ -f "$DISPATCHER_FILE" ] || { echo "dispatch-kit: unknown DISPATCHER '$DISPATCHER' (no $DISPATCHER_FILE)" >&2; exit 1; }
# Each dispatcher defines: dispatcher_require, dispatcher_spawn <name> <desc> <cwd> <cmd>,
# dispatcher_close <name> <cwd>.
# shellcheck source=/dev/null
. "$DISPATCHER_FILE"

require_jq() { command -v jq >/dev/null || { echo "jq is required (brew install jq)" >&2; exit 1; }; }
require_gh() { command -v gh >/dev/null || { echo "gh CLI is required" >&2; exit 1; }; }

ensure_pool() {
  if [ ! -f "$POOL_FILE" ]; then
    mkdir -p "$(dirname "$POOL_FILE")"
    echo '{"slots":[]}' > "$POOL_FILE"
  fi
  # Keep transient state out of git; config.sh stays committable.
  if [ ! -f "$STATE_BASE/.gitignore" ]; then
    printf 'state/\n' > "$STATE_BASE/.gitignore"
  fi
}

# Worktree dir for a slot id. e.g. slot 2 -> <parent>/<repo>-wt-2
slot_path() { echo "$WT_BASE/${WT_PREFIX}$1"; }

# Default branch of the repo (origin/HEAD), falling back to main.
default_branch() {
  git -C "$BRAIN_REPO" symbolic-ref refs/remotes/origin/HEAD --short 2>/dev/null | sed 's|^origin/||' || true
}

# First idle slot id, or empty string if none.
pick_idle_slot() {
  require_jq; ensure_pool
  jq -r '.slots[] | select(.status=="idle") | .id' "$POOL_FILE" | head -1
}

# Build the headless claude command the dispatcher runs in the worker workspace.
build_worker_cmd() {
  local instr="Read .claude/worker-prompt.md in this directory and execute it end-to-end. Report back when the PR is open."
  local effort_args
  if [ "$WORKER_EFFORT" = "ultracode" ]; then
    effort_args="--effort xhigh --settings '{\"ultracode\":true}'"
  else
    effort_args="--effort $WORKER_EFFORT"
  fi
  echo "claude --model $WORKER_MODEL $effort_args --dangerously-skip-permissions \"$instr\""
}

# Create the worktree for a slot if it doesn't exist yet, parked on wt/<id>.
# Lazy + idempotent: safe to re-run; existing worktrees are left alone.
ensure_slot_worktree() {
  local id="$1" path="$2"
  if git -C "$BRAIN_REPO" worktree list --porcelain | grep -qxF "worktree $path"; then
    return 0
  fi
  git -C "$BRAIN_REPO" fetch origin --prune
  local db; db="$(default_branch)"; [ -n "$db" ] || db="main"
  rm -rf "$path"
  echo "  creating worktree slot $id at $path (parked on wt/$id)"
  git -C "$BRAIN_REPO" worktree add -B "wt/$id" "$path" "origin/$db"
}

# Prep a slot for a fresh task: fetch, discard local changes, check out the task
# branch off origin/<default>. Build caches (gitignored) survive `git clean -fd`,
# so the next dispatch into this slot stays fast.
prep_slot_for_task() {
  local path="$1" branch="$2"
  local db; db="$(default_branch)"; [ -n "$db" ] || db="main"
  git -C "$path" fetch origin --prune
  git -C "$path" reset --hard
  git -C "$path" clean -fd
  git -C "$path" checkout -B "$branch" "origin/$db"
}

# Park a slot back to clean state on wt/<id> and drop the merged task branch.
park_slot() {
  local id="$1" path="$2" task_branch="$3"
  local db; db="$(default_branch)"; [ -n "$db" ] || db="main"
  git -C "$path" rev-parse --git-dir >/dev/null 2>&1 || return 0
  git -C "$path" fetch origin --prune 2>/dev/null || true
  git -C "$path" reset --hard >/dev/null 2>&1 || true
  git -C "$path" clean -fd >/dev/null 2>&1 || true
  git -C "$path" checkout -B "wt/$id" "origin/$db" >/dev/null 2>&1 || true
  [ -n "$task_branch" ] && git -C "$path" branch -D "$task_branch" 2>/dev/null || true
}

mark_slot_busy() {
  local slot="$1" issue="$2" branch="$3" ws="$4"
  local tmp; tmp="$(mktemp)"
  jq --argjson id "$slot" --arg issue "$issue" --arg branch "$branch" --arg ws "$ws" --arg now "$(date -u +%FT%TZ)" '
    .slots = (.slots | map(if .id == ($id|tonumber) then
      .status = "busy"
      | .issue = ($issue|tonumber)
      | .branch = $branch
      | .workspace = $ws
      | .claimed_at = $now
    else . end))
  ' "$POOL_FILE" > "$tmp" && mv "$tmp" "$POOL_FILE"
}

mark_slot_idle() {
  local slot="$1"
  local tmp; tmp="$(mktemp)"
  jq --argjson id "$slot" '
    .slots = (.slots | map(if .id == ($id|tonumber) then
      {id: .id, path: .path, status: "idle"}
    else . end))
  ' "$POOL_FILE" > "$tmp" && mv "$tmp" "$POOL_FILE"
}
