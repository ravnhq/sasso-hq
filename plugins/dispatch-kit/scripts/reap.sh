#!/usr/bin/env bash
# For each busy slot whose issue has been CLOSED, park the worktree back to clean
# state on wt/<id>, close the worker workspace via the dispatcher, and mark the
# slot idle.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=lib.sh
. "$HERE/lib.sh"

require_jq; require_gh; dispatcher_require; ensure_pool
[ -n "$ISSUES_REPO" ] || { echo "ISSUES_REPO is empty — set it in .claude/brain/config.sh." >&2; exit 1; }

# Bash 3.2-compatible: avoid `mapfile`.
BUSY=()
while IFS= read -r row; do
  BUSY+=("$row")
done < <(jq -r '.slots[] | select(.status=="busy") | "\(.id)|\(.issue // "")|\(.branch // "")|\(.path)|\(.workspace // "")"' "$POOL_FILE")

if [ "${#BUSY[@]}" -eq 0 ]; then
  echo "No busy slots."
  exit 0
fi

freed=0
for row in "${BUSY[@]}"; do
  IFS='|' read -r id issue branch path ws <<<"$row"
  [ -n "$issue" ] || { echo "slot $id: busy without issue, skipping"; continue; }

  state="$(gh issue view "$issue" -R "$ISSUES_REPO" --json state -q .state 2>/dev/null || echo UNKNOWN)"

  if [ "$state" = "CLOSED" ]; then
    echo "slot $id: issue #$issue is CLOSED — parking"
    park_slot "$id" "$path" "$branch"
    dispatcher_close "$ws" "$path"
    mark_slot_idle "$id"
    freed=$((freed+1))
  else
    echo "slot $id: issue #$issue is $state — leaving busy"
  fi
done

echo
echo "Freed $freed slot(s)."
