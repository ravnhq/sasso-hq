#!/usr/bin/env bash
# Create N worktree slots for the current repo. Each slot is a git worktree
# parked on wt/<id> off origin/<default>. Worktrees share one .git object store,
# so a single fetch updates origin/<default> for every slot.
#
# Usage: init-pool.sh [N]   (default 3)
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=lib.sh
. "$HERE/lib.sh"

N="${1:-3}"
require_jq; ensure_pool

for i in $(seq 1 "$N"); do
  path="$(slot_path "$i")"
  ensure_slot_worktree "$i" "$path"
  tmp="$(mktemp)"
  jq --argjson id "$i" --arg path "$path" '
    .slots = ((.slots // [])
      | (map(select(.id != $id)))
      + [{id: $id, path: $path, status: "idle"}])
    | .slots |= sort_by(.id)
  ' "$POOL_FILE" > "$tmp" && mv "$tmp" "$POOL_FILE"
  echo "slot $i: idle at $path"
done

echo
echo "Pool state:"
jq . "$POOL_FILE"
