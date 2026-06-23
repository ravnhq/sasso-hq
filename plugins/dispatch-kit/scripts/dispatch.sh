#!/usr/bin/env bash
# Dispatch a worker on an issue. Issues + PRs live in $ISSUES_REPO (the current
# repo by default). The worker gets a git worktree on branch task/<N>, implements,
# opens one PR, comments on the issue, and stops. The human merges.
#
#   dispatch.sh --create-issue --title "<t>" --body-file <f>
#   dispatch.sh --adopt <issue#>
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=lib.sh
. "$HERE/lib.sh"

usage() {
  cat <<'EOF' >&2
Usage:
  dispatch.sh --create-issue --title "<t>" --body-file <path>
  dispatch.sh --adopt <issue#>

Issues + PRs live in $ISSUES_REPO. The worker gets a worktree on task/<N>.
EOF
  exit 2
}

ACTION=""; TITLE=""; BODY_FILE=""; ISSUE=""
while [ $# -gt 0 ]; do
  case "$1" in
    --create-issue) ACTION="create"; shift;;
    --adopt) ACTION="adopt"; ISSUE="${2:?--adopt requires issue#}"; shift 2;;
    --title) TITLE="${2:?--title requires value}"; shift 2;;
    --body-file) BODY_FILE="${2:?--body-file requires path}"; shift 2;;
    -h|--help) usage;;
    *) echo "Unknown arg: $1" >&2; usage;;
  esac
done

require_jq; require_gh; dispatcher_require; ensure_pool
[ -n "$ISSUES_REPO" ] || { echo "ISSUES_REPO is empty — set it in .claude/brain/config.sh or run inside a repo with a GitHub origin." >&2; exit 1; }

# Validate args + require an idle slot BEFORE filing an issue, so a full pool
# can't orphan a freshly-created GitHub issue.
if [ "$ACTION" = "create" ]; then
  [ -n "$TITLE" ] && [ -f "$BODY_FILE" ] || usage
elif [ "$ACTION" = "adopt" ]; then
  [ -n "$ISSUE" ] || usage
else
  usage
fi

SLOT="$(pick_idle_slot)"
if [ -z "$SLOT" ]; then
  echo "No idle slots. Run: $LIB_DIR/pool.sh add <N>" >&2
  exit 1
fi

if [ "$ACTION" = "create" ]; then
  URL="$(gh issue create -R "$ISSUES_REPO" -t "$TITLE" -F "$BODY_FILE")"
  ISSUE="$(basename "$URL")"
  echo "Created issue #$ISSUE in $ISSUES_REPO — $URL"
elif [ "$ACTION" = "adopt" ]; then
  gh issue view "$ISSUE" -R "$ISSUES_REPO" --json number >/dev/null || {
    echo "issue #$ISSUE not found in $ISSUES_REPO" >&2; exit 1;
  }
fi

WS_PATH="$(slot_path "$SLOT")"
BRANCH="task/$ISSUE"

echo "Dispatching #$ISSUE to slot $SLOT ($WS_PATH) on branch $BRANCH"
ensure_slot_worktree "$SLOT" "$WS_PATH"   # lazy create on first use
prep_slot_for_task "$WS_PATH" "$BRANCH"

# Render the worker prompt into the worktree's gitignored .claude/ dir so it can
# never be accidentally committed by the worker.
PROMPT_TEMPLATE="$TEMPLATES_DIR/worker-prompt.md"
[ -f "$PROMPT_TEMPLATE" ] || { echo "missing $PROMPT_TEMPLATE" >&2; exit 1; }
mkdir -p "$WS_PATH/.claude"
# GREEN_LIGHT_CMD may be empty; render a clear placeholder so the prompt reads well.
GREEN_LIGHT_RENDER="${GREEN_LIGHT_CMD:-<none configured — see repo conventions>}"
# Pure-bash literal substitution (not sed): green-light commands routinely contain
# `&&` and `|`, which sed would mangle (`&` = matched text, `|` = our delimiter).
PROMPT="$(cat "$PROMPT_TEMPLATE")"
PROMPT="${PROMPT//\{\{ISSUE\}\}/$ISSUE}"
PROMPT="${PROMPT//\{\{BRANCH\}\}/$BRANCH}"
PROMPT="${PROMPT//\{\{ISSUES_REPO\}\}/$ISSUES_REPO}"
PROMPT="${PROMPT//\{\{REPO_NAME\}\}/$REPO_NAME}"
PROMPT="${PROMPT//\{\{GREEN_LIGHT\}\}/$GREEN_LIGHT_RENDER}"
printf '%s\n' "$PROMPT" > "$WS_PATH/.claude/worker-prompt.md"

# Workspace display name: "#<issue> <title>".
TITLE_SHORT="$(gh issue view "$ISSUE" -R "$ISSUES_REPO" --json title -q .title 2>/dev/null | cut -c1-50)"
WS_NAME="#${ISSUE} ${TITLE_SHORT}"

# Spawn the durable worker workspace via the configured dispatcher.
#   --dangerously-skip-permissions: fully autonomous worker. Safe because it
#     operates in an isolated worktree on a task branch and never touches the
#     default branch. Effort encoded by WORKER_EFFORT (see lib.sh / build_worker_cmd).
CLAUDE_CMD="$(build_worker_cmd)"
dispatcher_spawn "$WS_NAME" "Worker for issue #$ISSUE on $BRANCH" "$WS_PATH" "$CLAUDE_CMD"

mark_slot_busy "$SLOT" "$ISSUE" "$BRANCH" "$WS_NAME"

echo
echo "Dispatched."
echo "  Issue:      #$ISSUE in $ISSUES_REPO"
echo "  Slot:       $SLOT"
echo "  Path:       $WS_PATH"
echo "  Branch:     $BRANCH"
echo "  Dispatcher: $DISPATCHER"
echo "  Workspace:  $WS_NAME"
