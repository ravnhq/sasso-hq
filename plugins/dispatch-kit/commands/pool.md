---
description: Manage the worktree pool for the current repo. Subcommands - list, add <N>, remove <slot-id>.
argument-hint: list | add <N> | remove <slot-id>
allowed-tools: Bash
---

Run:

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/pool.sh" $ARGUMENTS
```

Subcommands:
- `list` — dump the pool state.
- `add <N>` — create N new worktree slots at `../<repo>-wt-<next>...`, each a git
  worktree parked on `wt/<id>` off origin/<default>.
- `remove <slot-id>` — only allowed for idle slots; removes the git worktree, its
  `wt/<id>` branch, and the pool entry (including any build caches it accumulated).

If no pool exists yet, bootstrap it first:

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/init-pool.sh" <N>
```

Pass output through to the user.
