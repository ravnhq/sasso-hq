---
description: Show the worker pool, in-flight tasks, open PRs, and open issues for the current repo.
allowed-tools: Bash
---

Run:

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/status.sh"
```

It prints three sections:
- **Slots** — every worktree slot with status (idle/busy), assigned issue, branch, workspace, path.
- **Open PRs** — number, draft/open, branch, CI status (green/running/fail/mixed), title.
- **Open issues** — number + title.

Pass the output through to the user unchanged.
