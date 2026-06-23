#!/usr/bin/env bash
# cmux dispatcher — spawns each worker as a durable cmux workspace. Default.
# Contract: dispatcher_require, dispatcher_spawn <name> <desc> <cwd> <cmd>,
#           dispatcher_close <name> <cwd>.

dispatcher_require() {
  command -v cmux >/dev/null || { echo "cmux is required (DISPATCHER=cmux)" >&2; exit 1; }
}

dispatcher_spawn() {
  local name="$1" desc="$2" cwd="$3" cmd="$4"
  cmux new-workspace \
    --cwd "$cwd" \
    --name "$name" \
    --description "$desc" \
    --command "$cmd" \
    --focus false
  echo "  cmux workspace: $name"
}

# Close a cmux workspace by display name. No-op if already gone. ($cwd unused.)
dispatcher_close() {
  local name="$1"
  [ -n "$name" ] || return 0
  local ref
  ref="$(cmux list-workspaces 2>/dev/null | grep -F -- "$name" | grep -oE 'workspace:[0-9]+' | head -1 || true)"
  if [ -z "$ref" ]; then
    echo "  cmux workspace already gone"
    return 0
  fi
  if cmux close-workspace --workspace "$ref" >/dev/null 2>&1; then
    echo "  closed cmux workspace ($ref)"
  else
    echo "  failed to close cmux workspace ($ref)"
  fi
}
