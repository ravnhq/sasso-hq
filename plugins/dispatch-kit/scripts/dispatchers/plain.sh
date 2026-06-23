#!/usr/bin/env bash
# plain dispatcher — runs each worker as a backgrounded `claude` via nohup.
# Lowest-common-denominator fallback: no multiplexer, just a PID + log file in
# the slot's .claude/ dir. Closes by PID (name is unused; cwd carries the pid).
# Contract: dispatcher_require, dispatcher_spawn <name> <desc> <cwd> <cmd>,
#           dispatcher_close <name> <cwd>.

dispatcher_require() { :; }   # nohup + the claude CLI are assumed present

dispatcher_spawn() {
  # shellcheck disable=SC2034  # uniform dispatcher contract; name/desc unused here
  local name="$1" desc="$2" cwd="$3" cmd="$4"
  mkdir -p "$cwd/.claude"
  local log="$cwd/.claude/worker.log"
  ( cd "$cwd" && nohup bash -lc "$cmd" >"$log" 2>&1 & echo $! > "$cwd/.claude/worker.pid" )
  echo "  background pid: $(cat "$cwd/.claude/worker.pid" 2>/dev/null)  log: $log"
}

# Close by the PID recorded in the slot's worktree. ($name unused.)
dispatcher_close() {
  # shellcheck disable=SC2034  # uniform dispatcher contract; name unused here
  local name="$1" cwd="$2"
  local pidfile="$cwd/.claude/worker.pid"
  if [ -f "$pidfile" ]; then
    local pid; pid="$(cat "$pidfile" 2>/dev/null)"
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null && echo "  killed worker pid $pid"
    else
      echo "  worker process already gone"
    fi
    rm -f "$pidfile"
  else
    echo "  no worker pid file"
  fi
}
