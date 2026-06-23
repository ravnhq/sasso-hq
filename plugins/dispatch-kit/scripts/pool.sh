#!/usr/bin/env bash
# Manage the worktree pool for the current repo.
#
#   pool.sh list
#   pool.sh add <N>
#   pool.sh remove <slot-id>
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=lib.sh
. "$HERE/lib.sh"

require_jq; ensure_pool

SUB="${1:-list}"; [ "$#" -gt 0 ] && shift || true

case "$SUB" in
  list)
    jq . "$POOL_FILE"
    ;;
  add)
    N="${1:?usage: pool.sh add <N>}"
    max="$(jq '([.slots[].id] + [0]) | max' "$POOL_FILE")"
    for i in $(seq 1 "$N"); do
      id=$((max + i))
      path="$(slot_path "$id")"
      ensure_slot_worktree "$id" "$path"
      tmp="$(mktemp)"
      jq --argjson id "$id" --arg path "$path" '
        .slots += [{id: $id, path: $path, status: "idle"}]
        | .slots |= sort_by(.id)
      ' "$POOL_FILE" > "$tmp" && mv "$tmp" "$POOL_FILE"
      echo "added slot $id at $path"
    done
    ;;
  remove)
    ID="${1:?usage: pool.sh remove <slot-id>}"
    status="$(jq -r --argjson id "$ID" '.slots[] | select(.id == ($id|tonumber)) | .status' "$POOL_FILE")"
    [ -n "$status" ] || { echo "slot $ID not found"; exit 1; }
    [ "$status" = "idle" ] || { echo "slot $ID is not idle ($status); refusing"; exit 1; }
    path="$(jq -r --argjson id "$ID" '.slots[] | select(.id == ($id|tonumber)) | .path' "$POOL_FILE")"
    # Remove the worktree (and its branch), then the pool entry.
    git -C "$BRAIN_REPO" worktree remove --force "$path" 2>/dev/null || rm -rf "$path"
    git -C "$BRAIN_REPO" branch -D "wt/$ID" 2>/dev/null || true
    git -C "$BRAIN_REPO" worktree prune 2>/dev/null || true
    tmp="$(mktemp)"
    jq --argjson id "$ID" '.slots |= map(select(.id != ($id|tonumber)))' "$POOL_FILE" > "$tmp" && mv "$tmp" "$POOL_FILE"
    echo "removed slot $ID"
    ;;
  *)
    echo "Usage: pool.sh {list | add <N> | remove <slot-id>}" >&2
    exit 2
    ;;
esac
