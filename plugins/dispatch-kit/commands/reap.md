---
description: For each busy slot whose issue has been closed, park the worktree back on the default branch and mark the slot idle.
allowed-tools: Bash
---

Run:

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/reap.sh"
```

This walks every busy slot in the pool. For each one whose issue is `CLOSED` on
GitHub (merged or rejected), it:

1. parks the worktree: fetch, reset, clean, check out `wt/<id>` at origin/<default>
2. deletes the local `task/<n>` branch
3. closes the worker workspace via the configured dispatcher
4. marks the slot `idle`

Build caches survive, so the next dispatch into that slot is fast. Report how many
slots were freed and which issues they were on.
