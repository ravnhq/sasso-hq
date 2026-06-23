#!/usr/bin/env bash
# tmux dispatcher — spawns each worker as a detached tmux session. Portable
# fallback for machines without cmux. Attach with: tmux attach -t <session>.
# Contract: dispatcher_require, dispatcher_spawn <name> <desc> <cwd> <cmd>,
#           dispatcher_close <name> <cwd>.

dispatcher_require() {
  command -v tmux >/dev/null || { echo "tmux is required (DISPATCHER=tmux)" >&2; exit 1; }
}

# tmux session names can't contain . : or whitespace — sanitize to underscores.
_tmux_session() { printf '%s' "$1" | tr ' .:/#' '_____'; }

dispatcher_spawn() {
  # shellcheck disable=SC2034  # uniform dispatcher contract; desc unused here
  local name="$1" desc="$2" cwd="$3" cmd="$4"
  local s; s="$(_tmux_session "$name")"
  tmux new-session -d -s "$s" -c "$cwd" "$cmd"
  echo "  tmux session: $s  (attach: tmux attach -t $s)"
}

dispatcher_close() {
  local name="$1"
  local s; s="$(_tmux_session "$name")"
  if tmux has-session -t "$s" 2>/dev/null; then
    tmux kill-session -t "$s" && echo "  killed tmux session $s"
  else
    echo "  tmux session already gone"
  fi
}
